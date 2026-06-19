"""OpenAI API helpers for transcription and note generation."""

from __future__ import annotations

import os

from openai import OpenAI

SUPPORTED_NOTE_MODES = [
    "Summary",
    "Action items",
    "Follow-up questions",
    "Explain technical concepts",
    "Study notes",
    "Meeting notes",
    "Key points only",
]

NOTE_TAKING_INSTRUCTIONS = (
    "You are a helpful AI note-taking assistant. You only assist with permitted "
    "audio where the user has permission to capture and process the audio. "
    "Produce concise, useful notes based on the transcript. Do not invent details."
)


def get_openai_client() -> OpenAI:
    """Create an OpenAI client from OPENAI_API_KEY in the environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Create a .env file with OPENAI_API_KEY=your_key_here.")
    return OpenAI(api_key=api_key)


def transcribe_audio(file_path: str, model: str = "gpt-4o-mini-transcribe") -> str:
    """Transcribe a WAV audio file and return plain transcript text."""
    client = get_openai_client()

    try:
        with open(file_path, "rb") as audio_file:
            result = client.audio.transcriptions.create(model=model, file=audio_file)
    except Exception as exc:
        raise RuntimeError(f"OpenAI transcription failed: {exc}") from exc

    text = getattr(result, "text", None)
    if text is None and isinstance(result, dict):
        text = result.get("text")
    return str(text or "").strip()


def generate_notes(
    transcript_chunk: str,
    rolling_context: str,
    mode: str,
    model: str = "gpt-4.1-mini",
) -> str:
    """Generate concise notes for a transcript chunk using the Responses API."""
    client = get_openai_client()
    selected_mode = mode if mode in SUPPORTED_NOTE_MODES else "Summary"

    if not transcript_chunk or not transcript_chunk.strip():
        return "Audio was empty or unclear, so no reliable notes can be generated for this chunk."

    prompt = f"""
Note mode: {selected_mode}

Rolling context from earlier chunks:
{rolling_context.strip() or "No earlier context yet."}

Latest transcript chunk:
{transcript_chunk.strip()}

Task:
Create concise, organized notes for the latest chunk. Use the rolling context only to preserve continuity.
Base the notes only on the transcript/context provided. If something is unclear, say so.
""".strip()

    try:
        response = client.responses.create(
            model=model,
            instructions=NOTE_TAKING_INSTRUCTIONS,
            input=prompt,
        )
    except Exception as exc:
        raise RuntimeError(f"OpenAI notes generation failed: {exc}") from exc

    text = getattr(response, "output_text", None)
    return str(text or "No notes were returned for this chunk.").strip()
