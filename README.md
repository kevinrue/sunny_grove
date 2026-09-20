# Maria Zelda

A calm, full-screen, arrow-key exploration game for young children. Guide an original princess around a pixel-art meadow to collect gems and flowers while practicing counting.

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

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Use the arrow keys to move. Escape or close the window to quit.