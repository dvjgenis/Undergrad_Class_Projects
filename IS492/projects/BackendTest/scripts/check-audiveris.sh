#!/usr/bin/env bash
#
# Check if Audiveris is installed and usable for PDF → MusicXML conversion.
# Run from project root: ./scripts/check-audiveris.sh
#
set -e

AUDIVERIS_APP="/Applications/Audiveris.app"
AUDIVERIS_EXE="${AUDIVERIS_APP}/Contents/MacOS/Audiveris"

echo "Checking Audiveris installation..."
echo ""

if command -v audiveris &>/dev/null; then
  echo "  ✓ audiveris found in PATH: $(command -v audiveris)"
  audiveris -batch -help 2>&1 | head -3 || true
  echo ""
  exit 0
fi

if [ -f "$AUDIVERIS_EXE" ]; then
  echo "  ✓ Audiveris.app found at $AUDIVERIS_APP"
  "$AUDIVERIS_EXE" -batch -help 2>&1 | head -3 || true
  echo ""
  exit 0
fi

echo "  ✗ Audiveris not found"
echo ""
echo "  Install with: ./scripts/install-audiveris.sh"
echo "  Or manually: https://github.com/Audiveris/audiveris/releases"
echo ""
exit 1
