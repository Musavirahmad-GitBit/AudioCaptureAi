"""Audio capture helpers for Live Audio Notes Assistant."""

from __future__ import annotations

import tempfile
import wave
from pathlib import Path
from typing import Any

import numpy as np
import sounddevice as sd


def list_input_devices() -> list[dict[str, Any]]:
    """Return input-capable audio devices reported by sounddevice.

    Each returned dictionary is intentionally small and UI-friendly. Device IDs
    are the indexes used by sounddevice when selecting a device for recording.
    """
    try:
        devices = sd.query_devices()
    except Exception as exc:  # sounddevice can fail if PortAudio is unavailable.
        raise RuntimeError(f"Could not query audio input devices: {exc}") from exc

    input_devices: list[dict[str, Any]] = []
    for device_id, device in enumerate(devices):
        max_input_channels = int(device.get("max_input_channels", 0) or 0)
        if max_input_channels > 0:
            input_devices.append(
                {
                    "id": device_id,
                    "name": str(device.get("name", f"Device {device_id}")),
                    "max_input_channels": max_input_channels,
                    "default_samplerate": float(device.get("default_samplerate", 0.0) or 0.0),
                }
            )

    return input_devices


def find_blackhole_device(devices: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the first BlackHole input device from a device list, if present."""
    for device in devices:
        if "blackhole" in str(device.get("name", "")).lower():
            return device
    return None


def record_audio_chunk(device_id: int, seconds: int | float, sample_rate: int) -> np.ndarray:
    """Record a mono, int16 audio chunk from the selected input device."""
    if seconds <= 0:
        raise ValueError("Recording duration must be greater than zero seconds.")
    if sample_rate <= 0:
        raise ValueError("Sample rate must be greater than zero.")

    frame_count = int(seconds * sample_rate)
    try:
        audio = sd.rec(
            frames=frame_count,
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            device=device_id,
        )
        sd.wait()
    except Exception as exc:
        raise RuntimeError(f"Audio recording failed: {exc}") from exc

    return np.asarray(audio, dtype=np.int16)


def save_wav_temp(audio: np.ndarray, sample_rate: int) -> str:
    """Save a mono int16 numpy audio array to a temporary WAV file."""
    if audio is None or audio.size == 0:
        raise ValueError("Cannot save an empty audio buffer.")
    if sample_rate <= 0:
        raise ValueError("Sample rate must be greater than zero.")

    mono_audio = np.asarray(audio, dtype=np.int16).reshape(-1)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_path = Path(temp_file.name)
    temp_file.close()

    try:
        with wave.open(str(temp_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit PCM = 2 bytes per sample.
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(mono_audio.tobytes())
    except Exception as exc:
        temp_path.unlink(missing_ok=True)
        raise RuntimeError(f"Could not save temporary WAV file: {exc}") from exc

    return str(temp_path)


def calculate_audio_level(audio: np.ndarray) -> float:
    """Return a simple normalized RMS level between 0.0 and roughly 1.0."""
    if audio is None or audio.size == 0:
        return 0.0

    samples = np.asarray(audio, dtype=np.float32).reshape(-1)
    if samples.size == 0:
        return 0.0

    rms = float(np.sqrt(np.mean(np.square(samples))))
    return rms / 32768.0
