@echo off
start "SherloCAN Backend" cmd /k "%~dp0run_backend.bat"
timeout /t 3 /nobreak >nul
start "SherloCAN Frontend" cmd /k "%~dp0run_frontend.bat"
timeout /t 3 /nobreak >nul
start http://127.0.0.1:5173
