#!/usr/bin/env bash
# FileSage — macOS build script
# Builds a standalone FileSage.app using PyInstaller

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "✦ FileSage — macOS App Builder"
echo "─────────────────────────────────"

# ── 1. Find Python ─────────────────────────────────────────────────────────────
PYTHON=""
for candidate in python3.12 python3.11 python3.10 python3; do
  if command -v "$candidate" &>/dev/null; then
    PYTHON="$candidate"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "❌  Python 3 not found. Install it with: brew install python"
  exit 1
fi

PYTHON_VERSION=$("$PYTHON" --version 2>&1)
echo "✓  Using $PYTHON_VERSION"

# ── 2. Set up virtual environment ─────────────────────────────────────────────
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "→  Creating virtual environment…"
  "$PYTHON" -m venv "$VENV_DIR" || { echo "❌  Failed to create venv"; exit 1; }
fi

VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

echo "→  Upgrading pip…"
"$VENV_PIP" install --quiet --upgrade pip

# ── 3. Install dependencies ───────────────────────────────────────────────────
echo "→  Installing PyQt6, requests, pyinstaller…"
"$VENV_PIP" install --quiet PyQt6 requests pyinstaller || {
  echo "❌  pip install failed. Try running manually:"
  echo "    source .venv/bin/activate"
  echo "    pip install PyQt6 requests pyinstaller"
  exit 1
}
echo "✓  Dependencies installed"

# ── 4. Clean previous build ───────────────────────────────────────────────────
echo "→  Cleaning previous build artifacts…"
rm -rf "$SCRIPT_DIR/dist" "$SCRIPT_DIR/build" "$SCRIPT_DIR/FileSage.spec"

# ── 5. Run PyInstaller ────────────────────────────────────────────────────────
PYINSTALLER="$VENV_DIR/bin/pyinstaller"
echo "→  Running PyInstaller…"
echo ""

"$PYINSTALLER" \
  --name "FileSage" \
  --windowed \
  --onedir \
  --noconfirm \
  --clean \
  --add-data "core.py:." \
  --add-data "workers.py:." \
  --hidden-import "PyQt6" \
  --hidden-import "PyQt6.QtCore" \
  --hidden-import "PyQt6.QtWidgets" \
  --hidden-import "PyQt6.QtGui" \
  --hidden-import "PyQt6.sip" \
  "$SCRIPT_DIR/main.py"

# ── 6. Verify and report ──────────────────────────────────────────────────────
APP="$SCRIPT_DIR/dist/FileSage.app"

if [ -d "$APP" ]; then
  SIZE=$(du -sh "$APP" | cut -f1)
  echo ""
  echo "─────────────────────────────────"
  echo "✦ Build successful!"
  echo "   App:  $APP"
  echo "   Size: $SIZE"
  echo ""
  echo "To install:"
  echo "   cp -r dist/FileSage.app /Applications/"
  echo ""
  echo "Or open directly:"
  echo "   open dist/FileSage.app"
  echo ""

  # Ask to open immediately
  read -p "Open FileSage.app now? [y/N] " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    open "$APP"
  fi
else
  echo ""
  echo "❌  Build failed — dist/FileSage.app was not created."
  echo ""
  echo "Check the output above for errors."
  echo "Common fixes:"
  echo "  • Make sure Xcode Command Line Tools are installed: xcode-select --install"
  echo "  • Try the simple launcher instead: ./run.sh"
  exit 1
fi
