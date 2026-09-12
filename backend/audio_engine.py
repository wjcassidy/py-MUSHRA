from __future__ import annotations

import logging
import threading
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from backend.config import Config

logger = logging.getLogger("py_mushra.audio_engine")

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

    def select(self, path: Path) -> None:
        self._load_stimulus(path)  # populate cache outside the lock-held callback path
        with self._lock:
            if self._carry.shape[1] > 0:
                self.playhead = max(0, self.playhead - self._carry.shape[1])
                self._carry = np.zeros((0, 0), dtype=np.float32)
            self.current_path = path
            self.playing = True

    def play(self) -> None:
        with self._lock:
            self.playing = True

    def pause(self) -> None:
        with self._lock:
            self.playing = False

    # -- realtime callback ----------------------------------------------------

    def _callback(self, outdata: np.ndarray, frames: int, time_info, status) -> None:
        if status:
            logger.warning("sounddevice status: %s", status)

        with self._lock:
            if not self.playing or self.current_path is None:
                outdata[:] = 0
                return

            source = self._stimulus_cache[self.current_path]
            num_source_channels, source_len = source.shape

            while self._carry.shape[1] < frames:
                start = self.playhead % source_len
                end = start + self.block_size
                if end <= source_len:
                    chunk = source[:, start:end]
                else:
                    chunk = np.concatenate([source[:, start:], source[:, : end - source_len]], axis=1)
                self.playhead += self.block_size

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

                self._carry = (
                    processed
                    if self._carry.shape[1] == 0
                    else np.concatenate([self._carry, processed], axis=1)
                )

            to_output = self._carry[:, :frames]
            self._carry = self._carry[:, frames:]
            outdata[:] = to_output.T
