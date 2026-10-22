from __future__ import annotations

import logging
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from backend.config import Config

logger = logging.getLogger("py_mushra.audio_engine")

# Stimulus switches fade the current stimulus out, then the new one in, each
# over this long with a raised-cosine envelope (so a switch takes twice this).
SWITCH_FADE_SECONDS = 0.05
PAUSE_FADE_SECONDS = 0.05

# Listener-adjustable output volume range (dB), set before/during familiarisation.
VOLUME_MIN_DB = -60.0
VOLUME_MAX_DB = 0.0
VOLUME_DEFAULT_DB = -38.0

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
    """Streams Ambisonic stimuli in realtime, undecoded, to a chosen output device,
    with seamless switching between stimuli that share a page (and therefore a
    shared playhead). Decoding happens downstream of this app -- e.g. a Max patcher
    hosting SceneRotator + AllRADecoder, reading this output via a virtual device
    such as Pro Tools Audio Bridge 64.

    (In-process plugin hosting via dawdreamer/pedalboard was dropped: both hosts
    leave the IEM VST3s stuck on their default 4-in/4-out bus, silently truncating
    a 4th-order decode to first order over 4 loudspeakers.)"""

    def __init__(self, config: Config):
        self.config = config
        self.sample_rate = config.sample_rate
        self.block_size = config.block_size
        # Ambisonic channels sent to the output device -- from config.yaml, or the
        # reference stimulus's channel count if unset (see startup()).
        self.num_channels: int | None = config.num_channels

        self._lock = threading.Lock()
        # Only the current page's stimuli are kept in memory (the full stimulus set
        # can be far larger than RAM): set_page_stimuli() evicts the previous page
        # and preloads the next one in the background. _cache_lock guards the cache
        # bookkeeping; when both locks are needed, take _lock first. Entries are only
        # removed while holding _lock too, so the audio callback (which reads the
        # cache under _lock) never sees its current stimulus disappear.
        self._cache_lock = threading.Lock()
        self._stimulus_cache: dict[Path, np.ndarray] = {}
        self._loading: dict[Path, Future] = {}
        self._page_paths: frozenset[Path] = frozenset()
        self._preloader = ThreadPoolExecutor(max_workers=1, thread_name_prefix="stimulus-preload")
        self.current_path: Path | None = None
        # What the listener selected (e.g. a page letter). Switches fade when this
        # changes, even if the file doesn't -- the hidden reference shares the
        # reference's file, and switching between them must sound like any other.
        self.current_key: object = None
        self.playing = False
        self.playhead = 0
        self._carry = np.zeros((0, 0), dtype=np.float32)

        # Stimulus switch in progress: switch_from fades out over the first
        # switch_fade_samples of the switch, then current_path fades in over the
        # next switch_fade_samples. switch_done counts samples into the switch.
        self.switch_from: Path | None = None
        self.switch_from_key: object = None
        self.switch_fade_samples = 1
        self.switch_done = 0

        # Output gain envelope -- ramped (never stepped) toward _gain_target so
        # play/pause and stimulus toggles fade instead of clicking.
        self._gain = 0.0
        self._gain_target = 0.0

        # Listener volume (linear) -- _volume_applied trails _volume, ramped across
        # each rendered block so slider drags don't zipper.
        self.volume_db = VOLUME_DEFAULT_DB
        self._volume = 10.0 ** (VOLUME_DEFAULT_DB / 20.0)
        self._volume_applied = self._volume

        self.device_index: int | None = None
        self.stream: sd.OutputStream | None = None
        # Set when the current device can't render num_channels -- surfaced
        # to the UI so the user can be prompted to pick a working device.
        self.device_error: str | None = None
        # The attempted device's own max_output_channels when device_error is set
        # (self.device_index is reverted on failure, so this is captured separately).
        self.device_error_output_channels: int | None = None
        # Set when the open stream is using fewer than num_channels because the device
        # can't render the full count -- lets you check playback on e.g. a stereo
        # device instead of being blocked entirely. Only the first monitor_channels
        # Ambisonic channels are audible; this is for validation, not a listening setup.
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

        # The probe is the first page's reference -- keep it so preloading skips it.
        self._stimulus_cache[probe_stimulus_path] = probe_audio

        if self.num_channels is None:
            self.num_channels = probe_audio.shape[0]
        elif probe_audio.shape[0] != self.num_channels:
            logger.warning(
                "Reference stimulus %s has %d channel(s), but config.yaml declares "
                "num_channels=%d -- check the stimuli match the external decoder.",
                probe_stimulus_path.name,
                probe_audio.shape[0],
                self.num_channels,
            )

        logger.info("Sending %d Ambisonic channel(s) to the output device", self.num_channels)

        try:
            self._open_stream()
        except AudioDeviceError as exc:
            # Don't fail startup over this -- leave the engine running with no
            # active stream so the UI can list devices and let the user pick
            # one that supports the required channel count.
            logger.warning("%s", exc)
            self.device_error = str(exc)

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
        if device_max >= self.num_channels:
            stream_channels = self.num_channels
        elif device_max >= 2:
            # Not enough channels for the full Ambisonic signal -- fall back to a fixed
            # stereo monitor (first 2 channels) purely for validation.
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

        self.monitor_channels = stream_channels if stream_channels < self.num_channels else None
        if self.monitor_channels:
            logger.warning(
                "Device only supports %d output channel(s) (need %d) -- monitoring in stereo "
                "on the first 2 Ambisonic channel(s) only. Not a real listening setup.",
                device_max,
                self.num_channels,
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
            return AudioDeviceError(
                f"The stimuli need {self.num_channels} output channels, but '{name}' only "
                f"supports {available}. Please choose a different output device."
            )
        return AudioDeviceError(f"Could not open output device '{name}': {exc}")

    def channel_status(self) -> dict:
        """A single summary of channel counts, used to
        build the device-selector's status line whether or not a stream is open."""
        if self.device_error is not None:
            device_output_channels = self.device_error_output_channels
        else:
            active = self.active_device_info()
            device_output_channels = active["max_output_channels"] if active else None
        return {
            "device_output_channels": device_output_channels,
            "required_output_channels": self.num_channels,
            "error": self.device_error,
            "monitor_channels": self.monitor_channels,
        }

    # -- stimulus loading / transport ----------------------------------------

    def _read_stimulus(self, path: Path) -> np.ndarray:
        sample_rate, audio = _read_wav_as_float32(path)
        if sample_rate != self.sample_rate:
            logger.warning(
                "%s has sample rate %d, expected %d; playback speed/pitch will be off.",
                path.name,
                sample_rate,
                self.sample_rate,
            )
        if self.num_channels is not None and audio.shape[0] != self.num_channels:
            logger.error(
                "%s has %d channel(s), but %d are being sent to the decoder (config.yaml's "
                "num_channels) -- extra channels are dropped and missing ones are silent.",
                path.name,
                audio.shape[0],
                self.num_channels,
            )
        return audio

    def _load_stimulus(self, path: Path) -> np.ndarray:
        """Return path's audio, reading it into the cache if needed. If another
        thread (e.g. the preloader) is already reading it, wait for that read
        instead of reading the same file twice."""
        with self._cache_lock:
            audio = self._stimulus_cache.get(path)
            if audio is not None:
                return audio
            pending = self._loading.get(path)
            if pending is None:
                pending = Future()
                self._loading[path] = pending
                is_reader = True
            else:
                is_reader = False

        if not is_reader:
            return pending.result()

        try:
            audio = self._read_stimulus(path)
        except BaseException as exc:
            with self._cache_lock:
                del self._loading[path]
            pending.set_exception(exc)
            raise
        with self._cache_lock:
            del self._loading[path]
            self._stimulus_cache[path] = audio
        pending.set_result(audio)
        return audio

    def set_page_stimuli(self, paths: list[Path]) -> None:
        """Make paths the only stimuli kept in memory: evict everything else, then
        load paths in the background (in order) so the first click on each is
        instant. Call after reset_page(); pass [] to free everything."""
        with self._cache_lock:
            self._page_paths = frozenset(paths)
        self._evict_unneeded()
        self._preloader.submit(self._preload, list(paths))

    def _evict_unneeded(self) -> None:
        with self._lock, self._cache_lock:
            keep = self._page_paths | {self.current_path, self.switch_from}
            evicted = [self._stimulus_cache.pop(p) for p in list(self._stimulus_cache) if p not in keep]
        if evicted:
            logger.info("Released %.1f MB of stimulus audio", sum(a.nbytes for a in evicted) / 1e6)
        # evicted's arrays are freed here, outside the locks

    def _preload(self, paths: list[Path]) -> None:
        for path in paths:
            with self._cache_lock:
                if path not in self._page_paths:
                    break  # the page changed while queued/loading -- a newer preload takes over
            try:
                self._load_stimulus(path)
            except Exception:
                logger.exception("Failed to preload %s", path.name)
        # If the page changed mid-read, the file just read belongs to the old page.
        self._evict_unneeded()

    def reset_page(self) -> None:
        with self._lock:
            self.playing = False
            self.current_path = None
            self.current_key = None
            self.playhead = 0
            self._carry = np.zeros((0, 0), dtype=np.float32)
            self.switch_from = None
            self.switch_from_key = None
            self.switch_done = 0
            self._gain = 0.0
            self._gain_target = 0.0

    def select(self, path: Path, key: object = None) -> None:
        """Switch playback to path. key identifies the selection (defaults to path);
        selecting a different key fades out/in even when the file is the same."""
        if key is None:
            key = path
        audio = self._load_stimulus(path)  # read outside the lock-held callback path
        with self._lock:
            with self._cache_lock:
                # Re-insert in case a page change evicted it since loading, so the
                # callback can always find current_path/switch_from in the cache.
                self._stimulus_cache.setdefault(path, audio)
            if self._carry.shape[1] > 0:
                self.playhead = max(0, self.playhead - self._carry.shape[1])
                if self.switch_from is not None:
                    self.switch_done = max(0, self.switch_done - self._carry.shape[1])
                self._carry = np.zeros((0, 0), dtype=np.float32)
            was_playing = self.playing
            previous, previous_key = self.current_path, self.current_key
            self.current_path, self.current_key = path, key
            self.playing = True
            self._gain_target = 1.0
            fade = self.switch_fade_samples
            if not was_playing or previous is None:
                # Nothing audible to fade out -- the play fade-in covers the start.
                self.switch_from = self.switch_from_key = None
                self.switch_done = 0
            elif self.switch_from is None:
                if previous_key != key:
                    self.switch_from, self.switch_from_key = previous, previous_key
                    self.switch_fade_samples = fade = max(
                        1, int(round(SWITCH_FADE_SECONDS * self.sample_rate))
                    )
                    self.switch_done = 0
            elif self.switch_done < fade:
                # Mid fade-out: keep fading switch_from out toward the new target,
                # unless the listener went back to it -- then fade it back in from
                # its current gain (the envelope mirrors around switch_done == fade).
                if key == self.switch_from_key:
                    self.switch_from, self.switch_from_key = previous, previous_key
                    self.switch_done = 2 * fade - self.switch_done
            elif key != previous_key:
                # Mid fade-in of previous: fade it back out from its current gain.
                self.switch_from, self.switch_from_key = previous, previous_key
                self.switch_done = 2 * fade - self.switch_done

    def play(self) -> None:
        with self._lock:
            self.playing = True
            self._gain_target = 1.0

    def pause(self) -> None:
        with self._lock:
            # Don't cut self.playing immediately -- the callback keeps rendering
            # and fades _gain down to 0 first, then settles playing to False.
            self._gain_target = 0.0

    def set_volume_db(self, volume_db: float) -> float:
        volume_db = min(VOLUME_MAX_DB, max(VOLUME_MIN_DB, float(volume_db)))
        with self._lock:
            self.volume_db = volume_db
            self._volume = 10.0 ** (volume_db / 20.0)
        return volume_db

    # -- realtime callback ----------------------------------------------------

    def _read_chunk(self, path: Path, start_sample: int, length: int) -> np.ndarray:
        source = self._stimulus_cache[path]
        source_len = source.shape[1]
        start = start_sample % source_len
        end = start + length
        if end <= source_len:
            return source[:, start:end]
        return np.concatenate([source[:, start:], source[:, : end - source_len]], axis=1)

    def _read_output_chunk(self, path: Path, start_sample: int, length: int) -> np.ndarray:
        """_read_chunk, zero-padded or truncated to num_channels."""
        chunk = self._read_chunk(path, start_sample, length)
        n = min(chunk.shape[0], self.num_channels)
        processed = np.zeros((self.num_channels, length), dtype=np.float32)
        processed[:n] = chunk[:n]
        return processed

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

            fade_samples = max(1, int(round(PAUSE_FADE_SECONDS * self.sample_rate)))
            gain_step = 1.0 / fade_samples

            while self._carry.shape[1] < frames:
                if not self.playing:
                    # Fully faded out and settled -- pad the rest of this callback
                    # with silence instead of continuing to advance.
                    remaining = frames - self._carry.shape[1]
                    pad = np.zeros((self.num_channels, remaining), dtype=np.float32)
                    self._carry = pad if self._carry.shape[1] == 0 else np.concatenate(
                        [self._carry, pad], axis=1
                    )
                    break

                length = self.block_size
                processed = self._read_output_chunk(self.current_path, self.playhead, length)

                if self.switch_from is not None:
                    # Raised-cosine envelope: 1 -> 0 over the fade-out of switch_from,
                    # then 0 -> 1 over the fade-in of current_path. Applied in the
                    # Ambisonic domain, before the external decoder.
                    fade = self.switch_fade_samples
                    idx = np.arange(self.switch_done, self.switch_done + length)
                    fading_out = idx < fade
                    if fading_out.any():
                        from_chunk = self._read_output_chunk(self.switch_from, self.playhead, length)
                        processed = np.where(fading_out[np.newaxis, :], from_chunk, processed)
                    phase = np.minimum(idx, 2 * fade).astype(np.float32) / fade
                    envelope = (0.5 * (1.0 + np.cos(np.pi * phase))).astype(np.float32)
                    processed = processed * envelope[np.newaxis, :]
                    self.switch_done += length
                    if self.switch_done >= 2 * fade:
                        self.switch_from = self.switch_from_key = None
                        self.switch_done = 0

                self.playhead += length

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
                volume_ramp = np.linspace(self._volume_applied, self._volume, length + 1, dtype=np.float32)[1:]
                self._volume_applied = self._volume
                processed = processed * (ramp * volume_ramp)[np.newaxis, :]

                if self._gain == 0.0 and self._gain_target == 0.0:
                    self.playing = False

                self._carry = (
                    processed
                    if self._carry.shape[1] == 0
                    else np.concatenate([self._carry, processed], axis=1)
                )

            to_output = self._carry[:, :frames]
            self._carry = self._carry[:, frames:]
            # outdata may have fewer channels than num_channels when monitoring
            # on a device that can't render the full channel count (see monitor_channels).
            outdata[:] = to_output[: outdata.shape[1]].T
