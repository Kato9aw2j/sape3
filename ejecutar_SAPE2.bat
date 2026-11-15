@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" SAPE2.py
if errorlevel 1 (
  echo.
  echo SAPE2 termino con error. Revisa el mensaje de arriba.
  pause
)
