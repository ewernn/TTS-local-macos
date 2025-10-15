# Kokoro TTS macOS App

A fast, local text-to-speech app for macOS using the Kokoro-82M model. Paste text, click speak, and hear it read aloud with natural-sounding voice.

## Features

- **Fast**: 1-2 second model load time (vs 5-10s for Bark)
- **Smart chunking**: Pauses at newlines, bullet points, and paragraphs
- **Speed control**: 0.5x to 2.0x playback speed (default 1.5x)
- **URL filtering**: Automatically removes long strings/URLs before speaking
- **Pipelined playback**: Generates next chunk while playing current one

## Prerequisites

- macOS
- Homebrew
- Python 3.9 or higher

## Installation

1. **Install Homebrew** (if you don't have it):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install espeak-ng**:
```bash
brew install espeak-ng
```

3. **Create Python environment**:
```bash
python3.9 -m venv tts-env
source tts-env/bin/activate
```

4. **Install Python packages**:
```bash
pip install kokoro soundfile pillow
```

5. **Create the app bundle** - see full instructions in repo

## Usage

1. Open the app
2. Paste or type your text
3. Adjust speed slider (default 1.5x)
4. Click "Speak"

## License

MIT
