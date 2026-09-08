# MLBot — My Lands Steam AI Agent

Windows desktop prototype for observing the My Lands Steam client and assisting with gameplay.

## Current prototype
- Select and inspect a game window.
- Live screenshot preview.
- Configurable capture interval.
- OCR-ready architecture.
- Safe mode: observation only until actions are explicitly enabled.
- SQLite state/memory layer.
- Action planner separated from mouse/keyboard execution.

## Build
Requirements: Windows 10/11, Python 3.11+.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

To build a standalone EXE:

```powershell
pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --name MLBot main.py
```

The executable will be in `dist\MLBot\MLBot.exe`.

## Safety
The first build is deliberately observation-first. It does not automatically send game actions. Action execution will be enabled after the Steam UI has been calibrated against screenshots from the user's client.
