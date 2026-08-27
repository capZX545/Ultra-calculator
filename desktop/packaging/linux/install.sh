#!/bin/sh
# Install the frozen Linux build into ~/.local (no root).
set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PREFIX="${PREFIX:-$HOME/.local}"
APPDIR="$PREFIX/share/ultra-calculator"
BINDIR="$PREFIX/bin"
APPNAME="UltraCalculator"

if [ ! -x "$HERE/$APPNAME" ]; then
  echo "Run this script from the extracted UltraCalculator folder." >&2
  exit 1
fi

mkdir -p "$APPDIR" "$BINDIR" \
  "$PREFIX/share/applications" \
  "$PREFIX/share/icons/hicolor/256x256/apps"

# Replace any previous copy.
rm -rf "$APPDIR"
mkdir -p "$APPDIR"
cp -a "$HERE"/. "$APPDIR"/

cat > "$BINDIR/ultra-calculator" <<EOF
#!/bin/sh
exec "$APPDIR/$APPNAME" "\$@"
EOF
chmod +x "$BINDIR/ultra-calculator" "$APPDIR/$APPNAME"

if [ -f "$HERE/icon.png" ]; then
  cp "$HERE/icon.png" "$PREFIX/share/icons/hicolor/256x256/apps/ultra-calculator.png"
fi

cat > "$PREFIX/share/applications/ultra-calculator.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Ultra Calculator
Comment=Calculator, formulas, circuits, sequences
Exec=$BINDIR/ultra-calculator
Icon=ultra-calculator
Terminal=false
Categories=Education;Science;Math;
StartupNotify=true
EOF

echo "Installed to $APPDIR"
echo "Command: $BINDIR/ultra-calculator"
echo "If the menu shortcut does not appear, log out or run: update-desktop-database $PREFIX/share/applications"
