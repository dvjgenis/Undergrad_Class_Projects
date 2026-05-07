#!/usr/bin/env bash
#
# Install Audiveris for PDF → MusicXML conversion (macOS).
# Run from project root: ./scripts/install-audiveris.sh
#
# Note: Run in a normal Terminal (not Cursor sandbox) if hdiutil attach fails.
#
set -e

AUDIVERIS_VERSION="5.9.0"
ARCH=$(uname -m)
case "$ARCH" in
  arm64|aarch64) DMG_ARCH="arm64" ;;
  x86_64)        DMG_ARCH="x86_64" ;;
  *)             echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

DMG_NAME="Audiveris-${AUDIVERIS_VERSION}-macosx-${DMG_ARCH}.dmg"
DOWNLOAD_URL="https://github.com/Audiveris/audiveris/releases/download/${AUDIVERIS_VERSION}/${DMG_NAME}"
APPS_DIR="/Applications"
AUDIVERIS_APP="${APPS_DIR}/Audiveris.app"

echo "Installing Audiveris ${AUDIVERIS_VERSION} for ${DMG_ARCH}..."

# Download DMG
TMP_DMG=$(mktemp -t Audiveris-XXXXXX.dmg)
echo "Downloading ${DMG_NAME}..."
curl -sL -o "$TMP_DMG" "$DOWNLOAD_URL"

# Mount and copy
echo "Mounting installer..."
ATTACH_OUT=$(hdiutil attach -nobrowse -readonly "$TMP_DMG" 2>&1) || true
MOUNT_POINT=$(echo "$ATTACH_OUT" | grep -E "/Volumes/" | tail -1 | awk '{print $NF}')
if [ -z "$MOUNT_POINT" ] || [ ! -d "$MOUNT_POINT" ]; then
  echo ""
  echo "Error: Could not mount DMG. Try running this script in a normal Terminal:"
  echo "  cd $(pwd) && ./scripts/install-audiveris.sh"
  echo ""
  echo "Or install manually:"
  echo "  1. Download: $DOWNLOAD_URL"
  echo "  2. Open the DMG and drag Audiveris.app to Applications"
  echo ""
  rm -f "$TMP_DMG"
  exit 1
fi
trap "hdiutil detach -quiet '$MOUNT_POINT' 2>/dev/null; rm -f '$TMP_DMG'" EXIT

AUDIVERIS_APP_SRC=$(find "$MOUNT_POINT" -maxdepth 3 -name "Audiveris.app" -type d 2>/dev/null | head -1)
if [ -z "$AUDIVERIS_APP_SRC" ] || [ ! -d "$AUDIVERIS_APP_SRC" ]; then
  echo "Error: Audiveris.app not found in DMG (searched $MOUNT_POINT)"
  ls -la "$MOUNT_POINT" 2>/dev/null || true
  exit 1
fi

echo "Copying to ${APPS_DIR}..."
sudo cp -R "$AUDIVERIS_APP_SRC" "$APPS_DIR/"
hdiutil detach -quiet "$MOUNT_POINT" 2>/dev/null || true

echo ""
echo "Audiveris installed to ${AUDIVERIS_APP}"
echo ""
echo "Note: macOS may block the app (unidentified developer). To allow:"
echo "  1. Try opening Audiveris from Applications"
echo "  2. Go to System Settings → Privacy & Security → click 'Open Anyway'"
echo ""
echo "For HarmonyForge PDF conversion, the backend will use:"
echo "  ${AUDIVERIS_APP}/Contents/MacOS/Audiveris"
echo ""
