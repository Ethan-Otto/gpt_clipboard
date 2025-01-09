#!/bin/bash

# Create the app bundle structure
APP_NAME="GPT Clipboard.app"
mkdir -p "$APP_NAME/Contents/"{MacOS,Resources}

# Create Info.plist
cat > "$APP_NAME/Contents/Info.plist" << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher.sh</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.gptclipboard</string>
    <key>CFBundleName</key>
    <string>GPT Clipboard</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
</dict>
</plist>
EOL

# Create the launcher script
cat > "$APP_NAME/Contents/MacOS/launcher.sh" << EOL
#!/bin/bash
cd "\$(dirname "\$0")"
cd ../../../
python3 main.py
EOL

# Make the launcher script executable
chmod +x "$APP_NAME/Contents/MacOS/launcher.sh"

# Convert SVG to ICNS
# First convert SVG to PNG
sips -s format png icon.svg --out icon.png

# Create IconSet
mkdir icon.iconset
sips -z 16 16   icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32   icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32   icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64   icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128 icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256 icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256 icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512 icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512 icon.png --out icon.iconset/icon_512x512.png

# Create ICNS file
iconutil -c icns icon.iconset

# Move icon to Resources
mv icon.icns "$APP_NAME/Contents/Resources/"

# Clean up
rm -rf icon.iconset icon.png
