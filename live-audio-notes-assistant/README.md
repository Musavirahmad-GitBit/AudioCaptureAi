# Live Audio Notes Assistant

A macOS-first local AI note-taking dashboard that captures permitted system audio using BlackHole 2ch, transcribes it with OpenAI, and generates live notes.

## Ethical / consent note

Use only with permission. This project is intended for lectures, webinars, podcasts, accessibility-style note support, personal recordings, demos, and meetings where AI note-taking is allowed. It does not include stealth, concealment, bypass, cheating, or hidden-assistance features.

## Features

- macOS system audio capture through BlackHole 2ch
- Audio input device picker
- Chunk-based transcription
- AI-generated summaries, action items, follow-up questions, study notes, and meeting notes
- Transcript and notes dashboard
- Download transcript/notes
- Clear session
- Basic audio-level debugging

## How to get an OpenAI API key

1. Go to [platform.openai.com](https://platform.openai.com/).
2. Sign in.
3. Go to **Dashboard** and then **API keys**.
4. Create a new secret key.
5. Copy it immediately.
6. Add it to your local `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

ChatGPT Pro does not automatically include API usage. OpenAI API billing is separate from ChatGPT subscriptions, so make sure your API account has billing or credits enabled.

## macOS BlackHole setup

1. Install **BlackHole 2ch**.
2. Open **Audio MIDI Setup** on macOS.
3. Click the **+** button and create a **Multi-Output Device**.
4. Check both your headphones/speakers and **BlackHole 2ch**.
5. Set your Mac sound output to the Multi-Output Device.
6. Open the Streamlit app.
7. Select **BlackHole 2ch** as the input device.
8. Play permitted audio.
9. Click **Record one chunk** or **Start auto mode**.

## Installation

```bash
cd live-audio-notes-assistant
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` and replace `your_openai_api_key_here` with your real OpenAI API key. If `python3.11` is not installed, install Python 3.11+ first; Python 3.8 is older than this project target.

## Run

```bash
streamlit run app.py
```

If you prefer to stay in the repository root instead, use:

```bash
streamlit run live-audio-notes-assistant/app.py
```

## Troubleshooting

### BlackHole not detected

- Confirm BlackHole 2ch is installed.
- Restart the app after installing BlackHole.
- Select another loopback/system-audio input if you use a different virtual audio driver.

### No audio being captured

- Confirm your Mac output is set to the Multi-Output Device.
- Confirm the Multi-Output Device includes both your speakers/headphones and BlackHole 2ch.
- Confirm BlackHole 2ch is selected in the app.

### Audio level is very low

- Play louder permitted audio.
- Check that the app is listening to BlackHole 2ch, not your microphone.
- Check the Multi-Output Device configuration in Audio MIDI Setup.

### Microphone permission denied

- Open **System Settings → Privacy & Security → Microphone**.
- Allow your terminal or Python/Streamlit environment to access the microphone/input device.
- Restart Streamlit.

### OPENAI_API_KEY missing

- Copy `.env.example` to `.env`.
- Add `OPENAI_API_KEY=your_real_key_here`.
- Restart Streamlit so the environment is reloaded.

### OpenAI API billing/key issue

- Verify the key was copied correctly.
- Confirm API billing or credits are enabled in your OpenAI platform account.
- Remember that ChatGPT Pro and API billing are separate.

### Python or virtual environment problems

- Make sure you are using Python 3.11+. Your prompt may show an older pyenv version such as Python 3.8; use `python3.11 -m venv .venv` instead.
- If virtual environment creation was interrupted with `Ctrl+C`, run `rm -rf .venv` and create it again.
- Run `source .venv/bin/activate` as one complete command. If your terminal line breaks in the middle of the path, `source` may fail with `no such file or directory`.

### sounddevice installation problems

- Make sure you are using Python 3.11+.
- Upgrade pip with `python -m pip install --upgrade pip`.
- If PortAudio issues appear, install PortAudio with Homebrew: `brew install portaudio`, then reinstall requirements.

### Streamlit auto mode keeps rerunning

- This is expected while auto mode is active. The MVP records one chunk per rerun.
- Click **Stop auto mode** to stop recording new chunks.
- If needed, stop the terminal process with `Ctrl+C`.

## Limitations

- MVP uses chunk-based near-real-time processing, not true low-latency streaming.
- Accuracy depends on audio quality.
- System audio capture depends on macOS routing.
- Requires OpenAI API billing/credits.
- Use only where permitted.

## Project structure

```text
live-audio-notes-assistant/
  app.py
  audio_utils.py
  openai_utils.py
  requirements.txt
  README.md
  .env.example
  .gitignore
```
