# HOW TO INSTALL SHITCOINER

## What you need first

- Python 3.10 or newer → https://python.org/downloads
  - Windows: check "Add Python to PATH" during install
  - macOS: or use `brew install python`
  - Linux: `sudo apt install python3 python3-pip python3-venv`

---

## Option A — Run from source (easiest)

1. Put all the files in one folder, e.g. `shitcoiner/`
2. Open a terminal in that folder
3. Install dependencies:

```bash
pip install requests PyQt6 python-dotenv
```

4. Run it:

```bash
python app.py
```

Done. A window opens. That's the whole app.

---

## Option B — Build a standalone executable (for sharing)

This creates a single double-clickable file with no Python required.

```bash
./build_standalone.sh
```

- **macOS** → `dist/SHITCOINER.app` — drag to Applications or double-click
- **Linux** → `dist/SHITCOINER` — run with `./dist/SHITCOINER`
- **Windows** → `dist/SHITCOINER.exe` — double-click

The build takes 2–5 minutes the first time (it's downloading and packaging everything).

**Windows note:** Run the script in Git Bash or WSL, not Command Prompt.
**macOS note:** First launch → right-click → Open (to bypass Gatekeeper warning).

---

## If something breaks during install

**"PyQt6 not found" or display errors on Linux:**
```bash
sudo apt install libgl1 libegl1 libxkbcommon0 libdbus-1-3
```

**"pip not found":**
```bash
python -m pip install requests PyQt6 python-dotenv
```

**Python version too old:**
Download Python 3.10+ from https://python.org and reinstall.

---

## Where does it store data?

Everything lives in `~/.shitcoiner/` — created automatically on first run.

- `~/.shitcoiner/.env` — your API keys (AI, exchange)
- `~/.shitcoiner/watchlist.json` — your saved coins and positions
