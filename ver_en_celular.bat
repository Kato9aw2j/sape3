@echo off
rem Muestra la version movil de SAPE en el celular, sin publicarla en internet.
rem La PC y el celular deben estar en la MISMA red privada (la zona Wi-Fi del
rem celular o el Wi-Fi de casa). No usar en redes publicas.
cd /d "%~dp0"
echo.
echo  S.A.P.E. movil - vista en el celular
echo  ------------------------------------
echo  En el navegador del celular abre una de estas direcciones:
echo.
powershell -NoProfile -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } | ForEach-Object { '     http://' + $_.IPAddress + ':8080' }"
echo.
echo  Si Windows pregunta por el Firewall, permite el acceso a Python.
echo  Para terminar, cierra esta ventana.
echo.
set "PY=C:\Users\LapOne MX\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" -m http.server 8080 --directory movil
echo.
echo  El servidor se detuvo o fallo. Revisa el mensaje de arriba.
echo  Si dice algo de "Address already in use", cierra otras ventanas que
echo  tengan este mismo servidor corriendo, o reinicia la PC.
pause
