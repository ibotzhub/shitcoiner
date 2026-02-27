# HOW TO RUN SHITCOINER

## Quickest way — just run it

Open a terminal in the shitcoiner folder and type:

```bash
python app.py
```

A window opens. You're running.

---

## If you built the standalone executable

- **macOS:** Double-click `SHITCOINER.app`
  - First time only: right-click → Open (macOS security thing, only once)
- **Windows:** Double-click `SHITCOINER.exe`
- **Linux:** `./dist/SHITCOINER` in your terminal

---

## Using the run script

If you're on macOS or Linux there's a shortcut:

```bash
./run.sh
```

Same as `python app.py`, just faster to type.

---

## Running from a different directory

The app doesn't care where you run it from — all data is stored in
`~/.shitcoiner/` in your home folder, not next to the files.

---

## To stop the app

Close the window, or press Ctrl+C in the terminal if you ran it from there.

---

## Running at startup (optional)

**macOS:** Drag `SHITCOINER.app` to System Settings → General → Login Items

**Windows:** Put a shortcut to `SHITCOINER.exe` in:
`C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

**Linux:** Add `python /path/to/shitcoiner/app.py` to your startup applications.
