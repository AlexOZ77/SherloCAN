@echo off
setlocal
cd /d "%~dp0\.."
where py >nul 2>nul || (echo [ERROR] Python launcher not found.& exit /b 1)
py -3.12 -m venv .venv || exit /b 1
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip || exit /b 1
pip install -r backend\requirements-hardware.txt || exit /b 1
echo [OK] SherloCAN Python environment ready.
