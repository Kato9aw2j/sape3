@echo off
cd /d "%~dp0"
set "PY=C:\Users\LapOne MX\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" SAPE2.py
if errorlevel 1 (
  echo.
  echo SAPE2 termino con error. Revisa el mensaje de arriba.
  pause
)
