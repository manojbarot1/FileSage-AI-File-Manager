#!/usr/bin/env bash
# FileSage launcher
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "✦ FileSage — AI File Intelligence"
echo "──────────────────────────────────"

# ── Find Python 3.9+ ──────────────────────────────────────────────────────────
PYTHON=""
for candidate in python3.12 python3.11 python3.10 python3.9 python3; do
  if command -v "$candidate" &>/dev/null; then
    if "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  echo "❌  Python 3.9+ not found. Install with: brew install python"
  exit 1
fi
echo "✓  $("$PYTHON" --version)"

# ── Virtual environment ───────────────────────────────────────────────────────
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "→  Creating virtual environment…"
  "$PYTHON" -m venv "$VENV_DIR" || { echo "❌  Failed to create venv"; exit 1; }
fi

PIP="$VENV_DIR/bin/pip"
PY="$VENV_DIR/bin/python"

# ── Dependencies ──────────────────────────────────────────────────────────────
echo "→  Checking dependencies…"
"$PIP" install --quiet --upgrade pip 2>/dev/null
"$PIP" install --quiet PyQt6 requests 2>/dev/null
echo "✓  Dependencies ready"

# ── Launch ────────────────────────────────────────────────────────────────────
echo "→  Launching FileSage…"
echo ""

# Suppress known harmless warnings at the env level too
export PYTHONWARNINGS="ignore::DeprecationWarning,ignore::UserWarning"
exec "$PY" -W ignore main.py
