@echo off
rem Lo ejecuta Power Automate: corre el pipeline, verifica el reporte y escribe el log.
cd /d "%~dp0"
python src\main.py > output\ultima_ejecucion.txt 2>&1
set RESULTADO=%ERRORLEVEL%
if %RESULTADO%==0 if not exist output\reporte_solicitudes.csv set RESULTADO=2
if %RESULTADO%==0 (set ESTADO=OK) else (set ESTADO=FALLO codigo %RESULTADO%)
echo %date% %time% - %ESTADO% >> output\log.txt
exit /b %RESULTADO%
