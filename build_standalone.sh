#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# SHITCOINER — build standalone native executable
# Run from the project directory:  ./build_standalone.sh
#
# Output:
#   macOS   → dist/SHITCOINER.app  (double-click to open)
#   Linux   → dist/SHITCOINER      (./dist/SHITCOINER)
#   Windows → dist/SHITCOINER.exe  (double-click)
# ─────────────────────────────────────────────────────────────────

# No set -e — we handle every error explicitly so you see what failed
cd "$(dirname "$0")"

echo ""
echo "  ⚡  SHITCOINER BUILD"
echo "  ──────────────────────────────────"
echo ""

# ── Detect OS ──────────────────────────────────────────────────────
OS="$(uname -s 2>/dev/null || echo Windows_NT)"
case "$OS" in
  Darwin*)               PLATFORM="macos"   ;;
  Linux*)                PLATFORM="linux"   ;;
  MINGW*|MSYS*|CYGWIN*)  PLATFORM="windows" ;;
  *)                     PLATFORM="linux"   ;;
esac
echo "  Platform detected: $PLATFORM"

# ── Detect Python 3.10+ ────────────────────────────────────────────
PYTHON=""
for cmd in python3 python3.12 python3.11 python3.10 python; do
  if command -v "$cmd" &>/dev/null; then
    if "$cmd" -c "import sys; assert sys.version_info >= (3,10)" 2>/dev/null; then
      PYTHON="$cmd"
      VER=$("$cmd" --version 2>&1)
      echo "  Python detected: $cmd  ($VER)"
      break
    fi
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo ""
  echo "  ERROR: Python 3.10 or newer not found."
  echo "  Install from https://python.org and try again."
  exit 1
fi

# ── Create venv ────────────────────────────────────────────────────
if [[ ! -d .venv ]]; then
  echo "  Creating virtual environment…"
  "$PYTHON" -m venv .venv
  if [[ $? -ne 0 ]]; then
    echo ""
    echo "  ERROR: Could not create .venv"
    echo "  On Ubuntu/Debian:  sudo apt install python3-venv"
    echo "  On Fedora:         sudo dnf install python3-venv"
    echo "  Or install deps globally and skip the venv:"
    echo "    pip install requests PyQt6 python-dotenv pyinstaller"
    echo "    pyinstaller --onefile --name SHITCOINER app.py"
    exit 1
  fi
fi

# ── Venv paths ─────────────────────────────────────────────────────
if [[ "$PLATFORM" == "windows" ]]; then
  VPYTHON=".venv/Scripts/python"
  VPIP=".venv/Scripts/pip"
  VPI=".venv/Scripts/pyinstaller"
else
  VPYTHON=".venv/bin/python"
  VPIP=".venv/bin/pip"
  VPI=".venv/bin/pyinstaller"
fi

# ── Install deps ───────────────────────────────────────────────────
echo ""
echo "  Installing dependencies (this takes a minute first time)…"
echo ""

"$VPIP" install --upgrade pip --quiet
"$VPIP" install \
  "requests>=2.28.0" \
  "PyQt6>=6.6.0" \
  "python-dotenv>=1.0.0" \
  "pyinstaller>=5.13"

if [[ $? -ne 0 ]]; then
  echo ""
  echo "  ERROR: Dependency installation failed."
  echo "  Check your internet connection and try again."
  exit 1
fi

echo ""
echo "  ── Running PyInstaller ────────────────────────────────"
echo ""

# Common flags
# --collect-binaries + --collect-data is more reliable than --collect-all for PyQt6
COMMON=(
  --noconfirm
  --clean
  --name "SHITCOINER"
  --collect-binaries "PyQt6"
  --collect-data "PyQt6"
  --hidden-import=PyQt6
  --hidden-import=PyQt6.QtCore
  --hidden-import=PyQt6.QtWidgets
  --hidden-import=PyQt6.QtGui
  --hidden-import=requests
  --hidden-import=requests.adapters
  --hidden-import=urllib3
  --hidden-import=dotenv
  --hidden-import=analysis
  --hidden-import=market_data
  --hidden-import=config
  --hidden-import=explainer
  --hidden-import=ai_commentary
)

if [[ "$PLATFORM" == "macos" ]]; then
  "$VPI" "${COMMON[@]}" --windowed --osx-bundle-identifier "com.shitcoiner.app" app.py
elif [[ "$PLATFORM" == "windows" ]]; then
  "$VPI" "${COMMON[@]}" --onefile --windowed app.py
else
  "$VPI" "${COMMON[@]}" --onefile app.py
fi

BUILD_EXIT=$?
echo ""

if [[ $BUILD_EXIT -eq 0 ]]; then
  echo "  ✓  BUILD SUCCESSFUL"
  echo ""
  if [[ "$PLATFORM" == "macos" ]]; then
    echo "  Output: dist/SHITCOINER.app"
    echo "  Run:    open dist/SHITCOINER.app"
    echo "  Note:   First launch → right-click → Open (to bypass Gatekeeper)"
  elif [[ "$PLATFORM" == "windows" ]]; then
    echo "  Output: dist/SHITCOINER.exe"
    echo "  Run:    double-click dist/SHITCOINER.exe"
  else
    chmod +x dist/SHITCOINER 2>/dev/null
    echo "  Output: dist/SHITCOINER"
    echo "  Run:    ./dist/SHITCOINER"
  fi
  echo ""
  echo "  Config: ~/.shitcoiner/"
else
  echo "  ✗  BUILD FAILED  (exit code $BUILD_EXIT)"
  echo ""
  echo "  Common fixes:"
  echo ""
  echo "  Linux — missing Qt system libs:"
  echo "    sudo apt install libgl1 libegl1 libxkbcommon0 libdbus-1-3"
  echo ""
  echo "  macOS — Gatekeeper blocking:"
  echo "    Right-click the .app → Open"
  echo ""
  echo "  All platforms — skip the build and just run directly:"
  echo "    $VPYTHON app.py"
  echo ""
  echo "  Paste the error above if you need more help."
  exit 1
fi
