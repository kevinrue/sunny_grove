# Sunny Grove

A calm, full-screen, arrow-key exploration game for young children. Guide an original princess around a pixel-art meadow to collect gems and flowers while practicing counting. Each new level generates fresh terrain and item positions; collect everything, follow the colorful exit arrow through the opened wooden gate, and explore the next map.

Sunny Grove uses Python 3.13.5 and is tested on Windows, Ubuntu, and macOS.

## Run on Windows

```powershell
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

If `.venv` has not been created yet, create it with the project's pinned Python version and then install the dependencies:

```powershell
pyenv exec python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

VS Code selects `.venv` automatically. Its integrated terminals activate it as well; for an external terminal, use the explicit `.\.venv\Scripts\python.exe` commands above.

## Run on Ubuntu

Install Python's virtual-environment support, then create the environment and install the project dependencies:

```bash
sudo apt update
sudo apt install python3-venv
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

## Run on macOS

Create the virtual environment and install the project dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest
```

On Ubuntu and macOS:

```bash
.venv/bin/python -m pytest
```

Use the arrow keys to move. Escape or close the window to quit.
