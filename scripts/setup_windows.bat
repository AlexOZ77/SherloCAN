@echo off
setlocal
cd /d "%~dp0\.."
where py >nul 2>nul || (echo [ERROR] Python launcher not found.& exit /b 1)

set PYSEL=-3.12
if /I "%~1"=="x86" set PYSEL=-3.12-32

echo [INFO] Creating SherloCAN environment with: py %PYSEL%
py %PYSEL% -m venv .venv || (
  echo [ERROR] Requested Python runtime is not installed.
  echo         Default: Python 3.12.  For a 32-bit J2534 DLL use: setup_windows.bat x86
  exit /b 1
)
call .venv\Scripts\activate.bat

if exist vendor\ (
  echo [INFO] Installing verified offline wheels from vendor\
  pip install --no-index --find-links vendor -r backend\requirements.txt || exit /b 1
  pip install --no-index --find-links vendor "j2534-api==2.0.0" "python-can>=4.6,<5" "cantools>=40,<41" || exit /b 1
) else (
  echo [WARN] vendor\ not found. Falling back to online installation.
  pip install -r backend\requirements-hardware.txt || exit /b 1
)

python -c "import struct; print('[INFO] Python architecture:', struct.calcsize('P')*8, 'bit')"
python -c "import J2534, can, cantools; print('[OK] J2534/python-can/cantools imports')" || exit /b 1
echo [OK] SherloCAN Python environment ready.
echo [INFO] If OpenPort DLL architecture does not match Python, rerun:
echo        scripts\setup_windows.bat x86
