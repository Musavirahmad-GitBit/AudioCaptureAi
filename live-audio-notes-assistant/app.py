"""Streamlit app for Live Audio Notes Assistant."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import dotenv_values, load_dotenv

from audio_utils import (
    calculate_audio_level,
    find_blackhole_device,
    list_input_devices,
    record_audio_chunk,
    save_wav_temp,
)
from openai_utils import SUPPORTED_NOTE_MODES, generate_notes, transcribe_audio

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent


def load_environment() -> None:
    """Load .env files from the app directory and repo root, without exposing values."""
    # Support both documented workflows:
    # 1. cd live-audio-notes-assistant && streamlit run app.py
    # 2. streamlit run live-audio-notes-assistant/app.py from the repo root
    for env_path in (ROOT_DIR / ".env", APP_DIR / ".env"):
        if env_path.exists():
            load_dotenv(env_path, override=False)


def env_example_has_real_key() -> bool:
    """Detect the common mistake of pasting a real key into .env.example."""
    placeholder = "your_openai_api_key_here"
    for example_path in (ROOT_DIR / ".env.example", APP_DIR / ".env.example"):
        if not example_path.exists():
            continue
        value = (dotenv_values(example_path).get("OPENAI_API_KEY") or "").strip()
        if value and value != placeholder:
            return True
    return False


load_environment()

st.set_page_config(page_title="Live Audio Notes Assistant", layout="wide")
st.title("Live Audio Notes Assistant")
st.info(
    "Use only with permission. This tool is intended for portfolio demos, lectures, "
    "webinars, podcasts, and meetings where AI note-taking is allowed."
)


def init_session_state() -> None:
    defaults = {
        "transcript_chunks": [],
        "notes_chunks": [],
        "timestamps": [],
        "full_transcript": "",
        "full_notes": "",
        "auto_mode": False,
        "last_audio_level": 0.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def rebuild_full_text() -> None:
    transcript_parts = []
    notes_parts = []
    for timestamp, transcript, notes in zip(
        st.session_state.timestamps,
        st.session_state.transcript_chunks,
        st.session_state.notes_chunks,
    ):
        transcript_parts.append(f"[{timestamp}]\n{transcript}")
        notes_parts.append(f"[{timestamp}]\n{notes}")
    st.session_state.full_transcript = "\n\n".join(transcript_parts)
    st.session_state.full_notes = "\n\n".join(notes_parts)


def clear_session() -> None:
    st.session_state.transcript_chunks = []
    st.session_state.notes_chunks = []
    st.session_state.timestamps = []
    st.session_state.full_transcript = ""
    st.session_state.full_notes = ""
    st.session_state.last_audio_level = 0.0
    st.session_state.auto_mode = False


def process_one_chunk(device_id: int, chunk_seconds: int, sample_rate: int, mode: str) -> None:
    """Record, transcribe, summarize, store, and clean up one audio chunk."""
    temp_path: str | None = None

    try:
        with st.spinner(f"Recording {chunk_seconds} seconds of audio..."):
            audio = record_audio_chunk(device_id=device_id, seconds=chunk_seconds, sample_rate=sample_rate)
            st.session_state.last_audio_level = calculate_audio_level(audio)
            temp_path = save_wav_temp(audio, sample_rate)
    except Exception as exc:
        st.error(f"Recording failed: {exc}")
        return

    try:
        with st.spinner("Transcribing audio chunk..."):
            transcript = transcribe_audio(temp_path)
    except Exception as exc:
        st.error(f"Transcription failed: {exc}")
        return
    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except OSError:
                pass

    rolling_context = st.session_state.full_transcript[-4000:]
    try:
        with st.spinner("Generating AI notes..."):
            notes = generate_notes(transcript, rolling_context, mode)
    except Exception as exc:
        st.error(f"Notes generation failed: {exc}")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.timestamps.append(timestamp)
    st.session_state.transcript_chunks.append(transcript or "[No transcript returned]")
    st.session_state.notes_chunks.append(notes)
    rebuild_full_text()


init_session_state()

api_key_available = bool(os.getenv("OPENAI_API_KEY"))
if not api_key_available:
    st.error("OPENAI_API_KEY is missing. Create a .env file with OPENAI_API_KEY=your_key_here")
    if env_example_has_real_key():
        st.warning(
            "It looks like an API key was pasted into .env.example. Rename or copy .env.example to .env, "
            "put the real key in .env, and reset .env.example back to the placeholder. If that key was "
            "shared in a screenshot or committed anywhere, rotate it in the OpenAI dashboard."
        )

try:
    devices = list_input_devices()
except Exception as exc:
    devices = []
    st.error(str(exc))

blackhole_device = find_blackhole_device(devices)
if not devices:
    st.warning("No audio input devices were detected. Check macOS microphone permissions and audio setup.")

with st.sidebar:
    st.header("Controls")
    device_labels = [
        f"{device['name']} (id {device['id']}, {device['max_input_channels']} input ch)" for device in devices
    ]
    default_index = 0
    if blackhole_device:
        default_index = next(
            (index for index, device in enumerate(devices) if device["id"] == blackhole_device["id"]),
            0,
        )

    selected_index = st.selectbox(
        "Audio input device",
        options=range(len(devices)) if devices else [],
        format_func=lambda index: device_labels[index],
        index=default_index if devices else None,
        placeholder="Select an input device",
    )

    chunk_seconds = st.slider("Chunk length (seconds)", min_value=3, max_value=15, value=6)
    sample_rate = st.selectbox("Sample rate", options=[16000, 24000, 44100, 48000], index=0)
    mode = st.selectbox("Notes mode", options=SUPPORTED_NOTE_MODES, index=0)

    record_clicked = st.button("Record one chunk", disabled=not devices or not api_key_available)
    col_start, col_stop = st.columns(2)
    start_clicked = col_start.button("Start auto mode", disabled=not devices or not api_key_available)
    stop_clicked = col_stop.button("Stop auto mode")
    clear_clicked = st.button("Clear session")

selected_device = devices[selected_index] if devices and selected_index is not None else None
if selected_device:
    st.write(f"Selected device: **{selected_device['name']}**")
if blackhole_device:
    st.success(f"BlackHole input detected: {blackhole_device['name']}")
else:
    st.warning(
        "BlackHole 2ch was not detected. Install BlackHole 2ch or select another "
        "loopback/system-audio input device."
    )

if clear_clicked:
    clear_session()
    st.rerun()
if stop_clicked:
    st.session_state.auto_mode = False
if start_clicked:
    st.session_state.auto_mode = True

if record_clicked and selected_device:
    process_one_chunk(selected_device["id"], chunk_seconds, sample_rate, mode)

# Streamlit reruns the script after interactions. For auto mode, this MVP records
# one chunk per run and then calls st.rerun(), creating a simple repeated loop
# that remains stoppable by pressing Stop auto mode on the next render.
if st.session_state.auto_mode and selected_device and api_key_available:
    process_one_chunk(selected_device["id"], chunk_seconds, sample_rate, mode)
    st.rerun()

left_col, right_col = st.columns(2)
with left_col:
    st.header("Live Transcript")
    st.text_area("Transcript", value=st.session_state.full_transcript, height=450, label_visibility="collapsed")
    st.download_button(
        "Download transcript (.txt)",
        data=st.session_state.full_transcript or "No transcript captured yet.",
        file_name="live_audio_transcript.txt",
        mime="text/plain",
    )

with right_col:
    st.header("AI Notes")
    st.text_area("Notes", value=st.session_state.full_notes, height=450, label_visibility="collapsed")
    st.download_button(
        "Download notes (.txt)",
        data=st.session_state.full_notes or "No notes generated yet.",
        file_name="live_audio_notes.txt",
        mime="text/plain",
    )

with st.expander("Debug audio capture"):
    st.metric("Last audio level", f"{st.session_state.last_audio_level:.5f}")
    if st.session_state.last_audio_level < 0.005:
        st.warning(
            "Audio level is very low. Check that macOS output is set to your Multi-Output "
            "Device and that BlackHole 2ch is selected as the input."
        )

st.divider()
st.caption(
    "macOS setup reminder: Install BlackHole 2ch, create a Multi-Output Device in Audio MIDI Setup, "
    "include both your headphones/speakers and BlackHole 2ch, set that Multi-Output Device as your "
    "Mac output, then select BlackHole 2ch in this app."
)
