# Kokoro TTS

Fast, local text-to-speech for macOS using Kokoro-82M. Type or paste text, press Cmd+Enter, and hear it spoken with natural pauses.

https://github.com/ewernn/TTS-local-macos/raw/main/tts.mov

## Install

```bash
# Install dependencies
brew install espeak-ng
pip install kokoro soundfile

# Run it
python3 speak.py
```

That's it. First run downloads the model (~100MB).

## Features

- Fast (1-2s load vs 5-10s for Bark)
- Speed control (0.5x - 2.0x)
- Smart chunking at newlines/paragraphs
- Filters out URLs automatically

## Usage

- Type or paste text
- Cmd+Enter or click "Speak"
- Adjust speed slider as needed
