@echo off
rem Lo ejecuta Power Automate. Uso: ejecutar.bat [limpio|dudosos]  (sin argumento = limpio)
cd /d "%~dp0"
set CASO=%1
if "%CASO%"=="" set CASO=limpio
python src\main.py data\solicitudes_%CASO%.json > output\ultima_ejecucion.txt 2>&1
set RESULTADO=%ERRORLEVEL%
if %RESULTADO%==0 if not exist output\reporte_solicitudes.csv set RESULTADO=2
if %RESULTADO%==0 (set ESTADO=OK) else (set ESTADO=FALLO codigo %RESULTADO%)
echo %date% %time% - %ESTADO% - caso %CASO% >> output\log.txt
exit /b %RESULTADO%
