from __future__ import annotations

import logging
import threading
from pathlib import Path

import dawdreamer as daw
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from backend.config import Config

logger = logging.getLogger("py_mushra.audio_engine")

CROSSFADE_SECONDS = 0.05
PAUSE_FADE_SECONDS = 0.05

# PortAudio's PaErrorCode for "Invalid number of channels" -- not exposed publicly
# by sounddevice, so we match on the numeric code from PortAudioError.args[1].
_PA_INVALID_CHANNEL_COUNT = -9998


class AudioDeviceError(Exception):
    """Raised when the selected output device can't be opened, e.g. because it
    doesn't support the number of channels this test needs to render."""

_INT_MAX = {
    np.dtype("int16"): 2**15,
    np.dtype("int32"): 2**31,
    np.dtype("uint8"): 2**7,
}


def _read_wav_as_float32(path: Path) -> tuple[int, np.ndarray]:
    """Read a wav file with scipy.io.wavfile, returning (sample_rate, array[channels, samples])."""
    sample_rate, data = wavfile.read(path)
    if data.dtype != np.float32:
        if data.dtype in _INT_MAX:
            data = data.astype(np.float32) / _INT_MAX[data.dtype]
        else:
            data = data.astype(np.float32)
    if data.ndim == 1:
        data = data[:, np.newaxis]
    # scipy returns (samples, channels); pedalboard/AudioEngine convention is (channels, samples)
    return sample_rate, np.ascontiguousarray(data.T)


class AudioEngine:
    """Loads the AllRADecoder plugin (VST3/AU) via dawdreamer and streams Ambisonic
    stimuli through it in realtime to a chosen output device, with seamless switching
    between stimuli that share a page (and therefore a shared playhead).

    dawdreamer (not pedalboard) hosts the plugin because AllRADecoder's bus is
    asymmetric (Ambisonic channels in, loudspeaker channels out) -- pedalboard's
    plugin.process() only ever requests the same channel count for both the input
    and output bus, so it can never negotiate a real decoder's bus correctly."""

    def __init__(self, config: Config):
        self.config = config
        self.plugin = None
        self._dd_engine: daw.RenderEngine | None = None
        self._dd_input = None
        self.sample_rate = config.sample_rate
        self.block_size = config.block_size
        # The plugin's exact bus sizes -- must come from config.yaml (see there for
        # why), not from probing: dawdreamer needs both numbers upfront, and they
        # legitimately differ for a decoder (Ambisonic channels in, loudspeakers out).
        self.num_input_channels: int | None = config.num_input_channels
        self.num_output_channels: int | None = config.num_output_channels

        self._lock = threading.Lock()
        self._stimulus_cache: dict[Path, np.ndarray] = {}
        self.current_path: Path | None = None
        self.playing = False
        self.playhead = 0
        self._carry = np.zeros((0, 0), dtype=np.float32)

        self.crossfade_from: Path | None = None
        self.crossfade_total = 0
        self.crossfade_done = 0

        # Output gain envelope -- ramped (never stepped) toward _gain_target so
        # play/pause and stimulus toggles fade instead of clicking.
        self._gain = 0.0
        self._gain_target = 0.0

        self.device_index: int | None = None
        self.stream: sd.OutputStream | None = None
        # Set when the current device can't render num_output_channels -- surfaced
        # to the UI so the user can be prompted to pick a working device.
        self.device_error: str | None = None
        # The attempted device's own max_output_channels when device_error is set
        # (self.device_index is reverted on failure, so this is captured separately).
        self.device_error_output_channels: int | None = None
        # Set when the open stream is using fewer than num_output_channels because the
        # device can't render the full count -- lets you monitor decoded audio on e.g.
        # a stereo device instead of being blocked entirely. Only the plugin's first
        # monitor_channels outputs are audible; this is for validating processing, not
        # a real listening setup.
        self.monitor_channels: int | None = None

    # -- startup -----------------------------------------------------------

    def startup(self, probe_stimulus_path: Path) -> None:
        probe_sr, probe_audio = _read_wav_as_float32(probe_stimulus_path)
        if probe_sr != self.sample_rate:
            logger.warning(
                "Stimulus sample rate (%d) does not match config sample_rate (%d); "
                "using the stimulus's sample rate for playback.",
                probe_sr,
                self.sample_rate,
            )
            self.sample_rate = probe_sr

        if self.config.plugin_path:
            if self.num_input_channels is None or self.num_output_channels is None:
                raise RuntimeError(
                    "plugin_path is set, so config.yaml must also declare num_input_channels "
                    "and num_output_channels -- dawdreamer needs the plugin's exact bus size "
                    "upfront and can't auto-detect it (input and output channel counts differ "
                    "for a decoder, so probing the stimulus files isn't enough)."
                )
            if probe_audio.shape[0] != self.num_input_channels:
                logger.warning(
                    "Reference stimulus %s has %d channel(s), but config.yaml declares "
                    "num_input_channels=%d -- check the stimuli match the loaded preset.",
                    probe_stimulus_path.name,
                    probe_audio.shape[0],
                    self.num_input_channels,
                )
            self._load_plugin()
        else:
            logger.warning(
                "No plugin_path configured -- running in passthrough fallback "
                "(no AllRADecoder decoding will happen). Set plugin_path in "
                "config.yaml to a VST3 or AU build of AllRADecoder."
            )
            self.plugin = None
            if self.num_input_channels is None:
                self.num_input_channels = probe_audio.shape[0]
            if self.num_output_channels is None:
                device_max = sd.query_devices(kind="output")["max_output_channels"]
                self.num_output_channels = min(self.num_input_channels, device_max)

        logger.info(
            "Rendering %d input channel(s) -> %d output channel(s)",
            self.num_input_channels,
            self.num_output_channels,
        )

        try:
            self._open_stream()
        except AudioDeviceError as exc:
            # Don't fail startup over this -- leave the engine running with no
            # active stream so the UI can list devices and let the user pick
            # one that supports the required channel count.
            logger.warning("%s", exc)
            self.device_error = str(exc)

    def _load_plugin(self) -> None:
        try:
            self._dd_engine = daw.RenderEngine(self.sample_rate, self.block_size)
            self._dd_input = self._dd_engine.make_playback_processor(
                "input", np.zeros((self.num_input_channels, self.block_size), dtype=np.float32)
            )
            plugin = self._dd_engine.make_plugin_processor("decoder", str(self.config.plugin_path))

            if not plugin.can_set_bus(self.num_input_channels, self.num_output_channels):
                raise RuntimeError(
                    f"AllRADecoder does not support a {self.num_input_channels}-in/"
                    f"{self.num_output_channels}-out bus."
                )
            plugin.set_bus(self.num_input_channels, self.num_output_channels)
            if (
                plugin.get_num_input_channels() != self.num_input_channels
                or plugin.get_num_output_channels() != self.num_output_channels
            ):
                raise RuntimeError(
                    f"AllRADecoder's bus is {plugin.get_num_input_channels()}-in/"
                    f"{plugin.get_num_output_channels()}-out after set_bus(), expected "
                    f"{self.num_input_channels}-in/{self.num_output_channels}-out."
                )

            if self.config.plugin_preset_path and self.config.plugin_preset_path.exists():
                plugin.load_vst3_preset(str(self.config.plugin_preset_path))
                logger.info("Loaded plugin preset: %s", self.config.plugin_preset_path)

            self._dd_engine.load_graph([(self._dd_input, []), (plugin, ["input"])])
            self.plugin = plugin
            logger.info("Loaded plugin: %s", plugin.get_name())
        except Exception:
            logger.exception(
                "Failed to load plugin at %s -- running in passthrough fallback.",
                self.config.plugin_path,
            )
            self.plugin = None
            self._dd_engine = None
            self._dd_input = None

    def _run_plugin(self, chunk: np.ndarray) -> np.ndarray:
        self._dd_input.set_data(chunk)
        self._dd_engine.render(self.block_size / self.sample_rate)
        return self.plugin.get_audio()

    # -- device management ---------------------------------------------------

    def list_output_devices(self) -> list[dict]:
        devices = []
        for index, device in enumerate(sd.query_devices()):
            if device["max_output_channels"] > 0:
                devices.append(
                    {
                        "index": index,
                        "name": device["name"],
                        "max_input_channels": device["max_input_channels"],
                        "max_output_channels": device["max_output_channels"],
                    }
                )
        return devices

    def active_device_info(self) -> dict | None:
        """Info about the device currently backing self.stream, or None if no
        stream is open (e.g. the configured device_error hasn't been resolved)."""
        if self.stream is None:
            return None
        if self.device_index is None:
            device = sd.query_devices(kind="output")
        else:
            device = sd.query_devices(self.device_index)
        return {
            "name": device["name"],
            "max_input_channels": device["max_input_channels"],
            "max_output_channels": device["max_output_channels"],
        }

    def set_output_device(self, index: int | None) -> None:
        previous_index = self.device_index
        self.device_index = index
        try:
            self._open_stream()
        except AudioDeviceError as exc:
            # _open_stream leaves the previous (working) stream untouched when
            # opening the new one fails, so just revert the recorded index.
            self.device_index = previous_index
            self.device_error = str(exc)
            raise
        self.device_error = None
        self.device_error_output_channels = None

    def _open_stream(self) -> None:
        device_max = self._query_output_channels(self.device_index)
        if device_max >= self.num_output_channels:
            stream_channels = self.num_output_channels
        elif device_max >= 2:
            # Not enough channels for the real decode -- fall back to a fixed stereo
            # monitor (first 2 of the decoder's outputs) purely for validation.
            stream_channels = 2
        else:
            name = self._device_name(self.device_index)
            self.device_error_output_channels = device_max
            raise AudioDeviceError(
                f"'{name}' only supports {device_max} output channel(s) -- at least 2 are needed, "
                "even for stereo monitoring. Please choose a different output device."
            )

        try:
            stream = sd.OutputStream(
                device=self.device_index,
                channels=stream_channels,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                dtype="float32",
                callback=self._callback,
            )
            stream.start()
        except sd.PortAudioError as exc:
            raise self._describe_stream_error(exc) from exc

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.stream = stream

        self.monitor_channels = stream_channels if stream_channels < self.num_output_channels else None
        if self.monitor_channels:
            logger.warning(
                "Device only supports %d output channel(s) (need %d) -- monitoring in stereo "
                "on the decoder's first 2 output(s) only. Not a real listening setup.",
                device_max,
                self.num_output_channels,
            )

    def _device_name(self, index: int | None) -> str:
        if index is None:
            return sd.query_devices(kind="output")["name"]
        return sd.query_devices(index)["name"]

    def _query_output_channels(self, index: int | None) -> int:
        if index is None:
            return sd.query_devices(kind="output")["max_output_channels"]
        return sd.query_devices(index)["max_output_channels"]

    def _describe_stream_error(self, exc: sd.PortAudioError) -> AudioDeviceError:
        if self.device_index is None:
            device_info = sd.query_devices(kind="output")
        else:
            device_info = sd.query_devices(self.device_index)
        name = device_info["name"]
        available = device_info["max_output_channels"]
        self.device_error_output_channels = available

        pa_error_code = exc.args[1] if len(exc.args) > 1 else None
        if pa_error_code == _PA_INVALID_CHANNEL_COUNT:
            preset_name = (
                self.config.plugin_preset_path.name if self.config.plugin_preset_path else "the current preset"
            )
            return AudioDeviceError(
                f"The current preset ({preset_name}) requires {self.num_output_channels} output "
                f"channels, but '{name}' only supports {available}. Please choose a different output device."
            )
        return AudioDeviceError(f"Could not open output device '{name}': {exc}")

    def channel_status(self) -> dict:
        """A single summary of channel counts + the active plugin preset, used to
        build the device-selector's status line whether or not a stream is open."""
        if self.device_error is not None:
            device_output_channels = self.device_error_output_channels
        else:
            active = self.active_device_info()
            device_output_channels = active["max_output_channels"] if active else None
        return {
            "device_output_channels": device_output_channels,
            "required_output_channels": self.num_output_channels,
            "detected_input_channels": self.num_input_channels,
            "plugin_preset": self.config.plugin_preset_path.name if self.config.plugin_preset_path else None,
            "error": self.device_error,
            "monitor_channels": self.monitor_channels,
        }

    # -- stimulus loading / transport ----------------------------------------

    def _load_stimulus(self, path: Path) -> np.ndarray:
        if path not in self._stimulus_cache:
            sample_rate, audio = _read_wav_as_float32(path)
            if sample_rate != self.sample_rate:
                logger.warning(
                    "%s has sample rate %d, expected %d; playback speed/pitch will be off.",
                    path.name,
                    sample_rate,
                    self.sample_rate,
                )
            if self.num_input_channels is not None and audio.shape[0] != self.num_input_channels:
                logger.error(
                    "%s has %d channel(s), but the plugin's bus was set up for %d input "
                    "channel(s) (config.yaml's num_input_channels) -- this stimulus will play "
                    "as silence rather than risk hanging the plugin with a mismatched channel count.",
                    path.name,
                    audio.shape[0],
                    self.num_input_channels,
                )
            self._stimulus_cache[path] = audio
        return self._stimulus_cache[path]

    def reset_page(self) -> None:
        with self._lock:
            self.playing = False
            self.current_path = None
            self.playhead = 0
            self._carry = np.zeros((0, 0), dtype=np.float32)
            self.crossfade_from = None
            self.crossfade_done = 0
            self._gain = 0.0
            self._gain_target = 0.0

    def select(self, path: Path) -> None:
        self._load_stimulus(path)  # populate cache outside the lock-held callback path
        with self._lock:
            if self._carry.shape[1] > 0:
                self.playhead = max(0, self.playhead - self._carry.shape[1])
                self._carry = np.zeros((0, 0), dtype=np.float32)
            previous = self.current_path
            self.current_path = path
            self.playing = True
            self._gain_target = 1.0
            if previous is not None and previous != path:
                # Crossfade in the Ambisonic domain so a single plugin instance/state
                # handles the (already-blended) signal -- avoids double-decoding.
                self.crossfade_from = previous
                self.crossfade_total = max(1, int(round(CROSSFADE_SECONDS * self.sample_rate)))
                self.crossfade_done = 0
            else:
                self.crossfade_from = None
                self.crossfade_done = 0

    def play(self) -> None:
        with self._lock:
            self.playing = True
            self._gain_target = 1.0

    def pause(self) -> None:
        with self._lock:
            # Don't cut self.playing immediately -- the callback keeps decoding
            # and fades _gain down to 0 first, then settles playing to False.
            self._gain_target = 0.0

    # -- realtime callback ----------------------------------------------------

    def _read_chunk(self, path: Path, start_sample: int, length: int) -> np.ndarray:
        source = self._stimulus_cache[path]
        source_len = source.shape[1]
        start = start_sample % source_len
        end = start + length
        if end <= source_len:
            return source[:, start:end]
        return np.concatenate([source[:, start:], source[:, : end - source_len]], axis=1)

    def _callback(self, outdata: np.ndarray, frames: int, time_info, status) -> None:
        if status:
            logger.warning("sounddevice status: %s", status)

        try:
            self._render_block(outdata, frames)
        except Exception:
            # An exception escaping this callback stops the whole PortAudio stream
            # (silence with no recovery) -- log and fall back to silence for this
            # block instead, so one bad block can't take down playback entirely.
            logger.exception("Audio callback failed; outputting silence.")
            outdata[:] = 0

    def _render_block(self, outdata: np.ndarray, frames: int) -> None:
        with self._lock:
            if not self.playing or self.current_path is None:
                outdata[:] = 0
                return

            num_source_channels = self._stimulus_cache[self.current_path].shape[0]
            fade_samples = max(1, int(round(PAUSE_FADE_SECONDS * self.sample_rate)))
            gain_step = 1.0 / fade_samples

            while self._carry.shape[1] < frames:
                if not self.playing:
                    # Fully faded out and settled -- pad the rest of this callback
                    # with silence instead of continuing to decode/advance.
                    remaining = frames - self._carry.shape[1]
                    pad = np.zeros((self.num_output_channels, remaining), dtype=np.float32)
                    self._carry = pad if self._carry.shape[1] == 0 else np.concatenate(
                        [self._carry, pad], axis=1
                    )
                    break

                length = self.block_size
                chunk = self._read_chunk(self.current_path, self.playhead, length)

                if self.crossfade_from is not None:
                    from_chunk = self._read_chunk(self.crossfade_from, self.playhead, length)
                    if from_chunk.shape[0] == chunk.shape[0]:
                        idx = np.arange(self.crossfade_done, self.crossfade_done + length, dtype=np.float32)
                        t = np.clip(idx / self.crossfade_total, 0.0, 1.0)
                        gain_to = np.sin(t * np.pi / 2.0).astype(np.float32)
                        gain_from = np.cos(t * np.pi / 2.0).astype(np.float32)
                        chunk = from_chunk * gain_from[np.newaxis, :] + chunk * gain_to[np.newaxis, :]
                    else:
                        # Can't blend stimuli with different channel counts -- hard-cut
                        # instead of crashing the audio callback.
                        logger.error(
                            "Cannot crossfade %s (%d ch) into %s (%d ch) -- channel count "
                            "mismatch; hard-cutting instead.",
                            self.crossfade_from.name,
                            from_chunk.shape[0],
                            self.current_path.name,
                            chunk.shape[0],
                        )
                    self.crossfade_done += length
                    if self.crossfade_done >= self.crossfade_total:
                        self.crossfade_from = None
                        self.crossfade_done = 0

                self.playhead += length

                if self.plugin is not None and chunk.shape[0] == self.num_input_channels:
                    try:
                        processed = self._run_plugin(chunk)
                    except Exception:
                        logger.exception("Plugin processing failed; outputting silence.")
                        processed = np.zeros((self.num_output_channels, chunk.shape[1]), dtype=np.float32)
                elif self.plugin is not None:
                    # Channel-count mismatch (see _load_stimulus's warning) -- never feed
                    # dawdreamer a chunk that doesn't match the plugin's declared bus size:
                    # doing so from this realtime callback thread hangs dawdreamer (and,
                    # since this lock is held, the whole app) rather than raising cleanly.
                    processed = np.zeros((self.num_output_channels, chunk.shape[1]), dtype=np.float32)
                else:
                    n = min(num_source_channels, self.num_output_channels)
                    processed = np.zeros((self.num_output_channels, chunk.shape[1]), dtype=np.float32)
                    processed[:n] = chunk[:n]

                if self._gain != self._gain_target:
                    direction = 1.0 if self._gain_target > self._gain else -1.0
                    ramp = self._gain + direction * gain_step * np.arange(1, length + 1, dtype=np.float32)
                    ramp = np.clip(ramp, 0.0, 1.0)
                    ramp = np.minimum(ramp, self._gain_target) if direction > 0 else np.maximum(
                        ramp, self._gain_target
                    )
                    self._gain = float(ramp[-1])
                else:
                    ramp = np.full(length, self._gain, dtype=np.float32)
                processed = processed * ramp[np.newaxis, :]

                if self._gain == 0.0 and self._gain_target == 0.0:
                    self.playing = False

                self._carry = (
                    processed
                    if self._carry.shape[1] == 0
                    else np.concatenate([self._carry, processed], axis=1)
                )

            to_output = self._carry[:, :frames]
            self._carry = self._carry[:, frames:]
            # outdata may have fewer channels than num_output_channels when monitoring
            # on a device that can't render the full channel count (see monitor_channels).
            outdata[:] = to_output[: outdata.shape[1]].T
