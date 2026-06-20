# AudioCaptureAi

This repository contains the Streamlit MVP in [`live-audio-notes-assistant/`](live-audio-notes-assistant/).

## Quick start from this repository root

> Use Python 3.11 or newer. Your terminal log showed Python 3.8.10, which is older than this project's target and may cause dependency/runtime issues.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` and add your real OpenAI API key. Do not paste your real key into `.env.example`; that file is only a template:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

Run the app from the repository root:

```bash
streamlit run live-audio-notes-assistant/app.py
```

## Free no-quota mode

If your OpenAI quota is finished, select **Free browser live transcription** in the sidebar. This uses the browser speech-recognition API for near-instant interim transcripts and simple local notes, so it does not call OpenAI. Use Chrome or Edge for best support, allow microphone access, and select BlackHole 2ch/permitted audio as the input source when macOS or the browser offers an input selector.

## If virtual environment creation was interrupted

If you pressed `Ctrl+C` while `python -m venv .venv` was still creating the environment, delete the partial environment and recreate it:

```bash
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
```

If `source` is split across two terminal lines, the path will be broken and shell will report `no such file or directory`. Run the command as one complete line from the repository root:

```bash
source .venv/bin/activate
```

If you already pasted a real key into `.env.example` or shared it in a screenshot, rotate that key in the OpenAI dashboard and put the new key only in `.env`.

For full BlackHole 2ch setup, features, troubleshooting, and limitations, see [`live-audio-notes-assistant/README.md`](live-audio-notes-assistant/README.md).
