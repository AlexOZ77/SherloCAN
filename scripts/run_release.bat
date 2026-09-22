@echo off
setlocal
cd /d "%~dp0\.."
if not exist .venv\Scripts\python.exe (echo Run scripts\setup_windows.bat first.& pause& exit /b 1)
start "" http://127.0.0.1:8000
cd backend
"..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
