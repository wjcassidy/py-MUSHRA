from __future__ import annotations

import logging
import threading
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from backend.config import Config

logger = logging.getLogger("py_mushra.audio_engine")

CROSSFADE_SECONDS = 0.05
PAUSE_FADE_SECONDS = 0.05

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
    """Loads the AllRADecoder plugin (VST3/AU) and streams Ambisonic stimuli through it
    in realtime to a chosen output device, with seamless switching between stimuli that
    share a page (and therefore a shared playhead)."""

    def __init__(self, config: Config):
        self.config = config
        self.plugin = None
        self.sample_rate = config.sample_rate
        self.block_size = config.block_size
        self.num_output_channels: int | None = config.num_output_channels

        self._lock = threading.Lock()
        self._stimulus_cache: dict[Path, np.ndarray] = {}
        self.current_path: Path | None = None
        self.playing = False
        self.playhead = 0
        self._pending_reset = True
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

    # -- startup -----------------------------------------------------------

    def startup(self, probe_stimulus_path: Path) -> None:
        self._load_plugin()

        probe_sr, probe_audio = _read_wav_as_float32(probe_stimulus_path)
        if probe_sr != self.sample_rate:
            logger.warning(
                "Stimulus sample rate (%d) does not match config sample_rate (%d); "
                "using the stimulus's sample rate for playback.",
                probe_sr,
                self.sample_rate,
            )
            self.sample_rate = probe_sr

        if self.num_output_channels is None:
            self.num_output_channels = self._probe_output_channels(probe_audio)
            if self.plugin is None:
                device_max = sd.query_devices(kind="output")["max_output_channels"]
                self.num_output_channels = min(self.num_output_channels, device_max)
        logger.info("Rendering to %d output channel(s)", self.num_output_channels)

        self._open_stream()

    def _load_plugin(self) -> None:
        if not self.config.plugin_path:
            logger.warning(
                "No plugin_path configured -- running in passthrough fallback "
                "(no AllRADecoder decoding will happen). Set plugin_path in "
                "config.yaml to a VST3 or AU build of AllRADecoder."
            )
            return
        try:
            import pedalboard

            self.plugin = pedalboard.load_plugin(str(self.config.plugin_path))
            logger.info("Loaded plugin: %s", self.plugin.name)
        except Exception:
            logger.exception(
                "Failed to load plugin at %s -- running in passthrough fallback.",
                self.config.plugin_path,
            )
            self.plugin = None
            return

        if self.config.plugin_preset_path and self.config.plugin_preset_path.exists():
            try:
                self.plugin.load_preset(str(self.config.plugin_preset_path))
                logger.info("Loaded plugin preset: %s", self.config.plugin_preset_path)
            except Exception:
                logger.exception(
                    "Failed to load plugin preset at %s -- using plugin defaults.",
                    self.config.plugin_preset_path,
                )

    def _probe_output_channels(self, sample_audio: np.ndarray) -> int:
        if self.plugin is None:
            return sample_audio.shape[0]
        try:
            probe_block = np.zeros((sample_audio.shape[0], self.block_size), dtype=np.float32)
            output = self.plugin.process(probe_block, self.sample_rate, reset=True)
            self._pending_reset = True  # real playback should still start with a clean reset
            return output.shape[0]
        except Exception:
            logger.exception(
                "Failed to probe plugin output channel count -- falling back to input "
                "channel count. Set num_output_channels in config.yaml to override."
            )
            return sample_audio.shape[0]

    # -- device management ---------------------------------------------------

    def list_output_devices(self) -> list[dict]:
        devices = []
        for index, device in enumerate(sd.query_devices()):
            if device["max_output_channels"] > 0:
                devices.append(
                    {
                        "index": index,
                        "name": device["name"],
                        "max_output_channels": device["max_output_channels"],
                    }
                )
        return devices

    def set_output_device(self, index: int | None) -> None:
        self.device_index = index
        self._open_stream()

    def _open_stream(self) -> None:
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.stream = sd.OutputStream(
            device=self.device_index,
            channels=self.num_output_channels,
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            dtype="float32",
            callback=self._callback,
        )
        self.stream.start()

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
            self._stimulus_cache[path] = audio
        return self._stimulus_cache[path]

    def reset_page(self) -> None:
        with self._lock:
            self.playing = False
            self.current_path = None
            self.playhead = 0
            self._pending_reset = True
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
                    idx = np.arange(self.crossfade_done, self.crossfade_done + length, dtype=np.float32)
                    t = np.clip(idx / self.crossfade_total, 0.0, 1.0)
                    gain_to = np.sin(t * np.pi / 2.0).astype(np.float32)
                    gain_from = np.cos(t * np.pi / 2.0).astype(np.float32)
                    chunk = from_chunk * gain_from[np.newaxis, :] + chunk * gain_to[np.newaxis, :]
                    self.crossfade_done += length
                    if self.crossfade_done >= self.crossfade_total:
                        self.crossfade_from = None
                        self.crossfade_done = 0

                self.playhead += length

                if self.plugin is not None:
                    try:
                        processed = self.plugin.process(
                            chunk, self.sample_rate, reset=self._pending_reset
                        )
                    except Exception:
                        logger.exception("Plugin processing failed; outputting silence.")
                        processed = np.zeros((self.num_output_channels, chunk.shape[1]), dtype=np.float32)
                else:
                    n = min(num_source_channels, self.num_output_channels)
                    processed = np.zeros((self.num_output_channels, chunk.shape[1]), dtype=np.float32)
                    processed[:n] = chunk[:n]
                self._pending_reset = False

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
            outdata[:] = to_output.T
