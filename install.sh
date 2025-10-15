#!/bin/bash

# Install script for Kokoro TTS macOS app

set -e

echo "Installing Kokoro TTS as macOS app..."

# Get the repo directory
REPO_PATH="$(cd "$(dirname "$0")" && pwd)"

# Create app bundle structure
echo "Creating app bundle..."
mkdir -p ~/Applications/TextToSpeech.app/Contents/{MacOS,Resources}

# Create launcher script
echo "Creating launcher..."
cat > ~/Applications/TextToSpeech.app/Contents/MacOS/TextToSpeech << EOF
#!/bin/bash
cd "$REPO_PATH"
python3 speak.py
EOF

chmod +x ~/Applications/TextToSpeech.app/Contents/MacOS/TextToSpeech

# Create Info.plist
echo "Creating Info.plist..."
cat > ~/Applications/TextToSpeech.app/Contents/Info.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>TextToSpeech</string>
    <key>CFBundleName</key>
    <string>Text to Speech</string>
    <key>CFBundleIdentifier</key>
    <string>com.local.texttospeech</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>
EOF

echo "✓ App installed to ~/Applications/TextToSpeech.app"
echo ""
echo "To launch:"
echo "  open ~/Applications/TextToSpeech.app"
echo ""
echo "Or drag it to your dock!"
