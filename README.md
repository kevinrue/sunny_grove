# Maria Zelda

A calm, arrow-key exploration game for young children. Guide an original princess around a pixel-art meadow to collect gems and flowers while practicing counting.

## Run on Windows

```powershell
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

If `.venv` has not been created yet, create it with an installed Python interpreter:

```powershell
python -m venv .venv
```

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Use the arrow keys to move. Escape or close the window to quit.