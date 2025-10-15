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

5. **Create the app bundle**:
```bash
# Create directories
mkdir -p ~/Applications/TextToSpeech.app/Contents/MacOS
mkdir -p ~/Applications/TextToSpeech.app/Contents/Resources

# Copy speak.py to the app (adjust path to your script location)
cp speak.py ~/Applications/TextToSpeech.app/Contents/MacOS/

# Create launcher script
cat > ~/Applications/TextToSpeech.app/Contents/MacOS/TextToSpeech << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
/path/to/your/tts-env/bin/python3 speak.py
EOF

# Make executable
chmod +x ~/Applications/TextToSpeech.app/Contents/MacOS/TextToSpeech

# Create Info.plist
cat > ~/Applications/TextToSpeech.app/Contents/Info.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>TextToSpeech</string>
    <key>CFBundleName</key>
    <string>TextToSpeech</string>
    <key>CFBundleIdentifier</key>
    <string>com.local.texttospeech</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
</dict>
</plist>
EOF
```

6. **Launch the app**:
```bash
open ~/Applications/TextToSpeech.app
```

## Usage

1. Open the app
2. Paste or type your text in the text box
3. Adjust speed slider if desired (default 1.2x)
4. Click "Speak" or press Cmd+Enter
5. The app will read your text with natural pauses at line breaks

## How It Works

- **Filters** out words >20 characters (URLs, long tokens)
- **Chunks** text at newlines and every ~200 characters
- **Generates** audio for each chunk using Kokoro TTS
- **Plays** chunks sequentially with the next one pre-generated during playback

## Troubleshooting

**"Module not found" error**: Make sure you're using the Python from your virtual environment in the launcher script.

**No sound**: Check that `afplay` works in terminal: `afplay /System/Library/Sounds/Glass.aiff`

**First launch is slow**: The Kokoro model downloads on first run (~100MB). Subsequent launches are fast.

## Tech Stack

- **Kokoro-82M**: Fast, high-quality TTS model
- **tkinter**: GUI framework
- **soundfile**: Audio file handling
- **espeak-ng**: Phoneme processing

## License

MIT
