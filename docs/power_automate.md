# Flujo Power Automate Desktop (opción A)

Crea un flujo nuevo "Automatizador RRHH" con estas acciones (ajusta la ruta a tu carpeta):

1. **Ejecutar aplicación** → `C:\Users\JUAN JOSE PEÑA\Desktop\reto tecnico\ejecutar.bat`, "Esperar a que se complete la aplicación", guardar código en `%CodigoSalida%`.
2. **Si archivo existe** → `...\output\reporte_solicitudes.csv` (guardar resultado en `%Existe%`).
3. **Si** `%CodigoSalida%` = 0 **y** `%Existe%` = Verdadero:
   - **Escribir texto en archivo** (agregar) en `...\output\log_flujo.txt`: `%CurrentDateTime% - OK`
   - **Mostrar mensaje**: "Reporte generado".
4. **Si no**:
   - **Escribir texto en archivo** (agregar): `%CurrentDateTime% - FALLO (código %CodigoSalida%)`
   - **Mostrar mensaje**: "La automatización falló, revisa output\ultima_ejecucion.txt".
5. Envuelve todo en **Bloque On block error** → mostrar mensaje de error.

`ejecutar.bat` ya escribe también `output\log.txt` con fecha, hora y resultado.
Toma capturas del flujo y de una ejecución exitosa y otra fallida (renombra `src\main.py` para provocar el fallo) y guárdalas en `docs/`.
