# Kokoro TTS

Fast, local text-to-speech for macOS using Kokoro-82M. Type or paste text, press Cmd+Enter, and hear it spoken with natural pauses.




https://github.com/user-attachments/assets/8b52443c-a6c4-4cf0-9572-a8148a1ad698




## Install

```bash
# Clone the repo
git clone https://github.com/ewernn/TTS-local-macos.git
cd TTS-local-macos

# Install dependencies
brew install espeak-ng
pip install kokoro soundfile

# Run it
python3 speak.py
```

That's it. First run downloads the model (~100MB).

### Optional: Install as macOS App

To add it to your dock/Applications:

```bash
./install.sh
```

## Features

- Fast (1-2s load vs 5-10s for Bark)
- Speed control (0.5x - 2.0x)
- Smart chunking at newlines/paragraphs
- Filters out URLs automatically

## Usage

- Type or paste text
- Cmd+Enter or click "Speak"
- Adjust speed slider as needed
