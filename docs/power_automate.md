# Flujo Power Automate Desktop (opción A) – construido y probado

Flujo "Automatizador RRHH" (17 acciones), creado en Power Automate Desktop:

1. Variables `ProyectoDir`, `Reporte` (output\reporte_solicitudes.csv) y `LogFlujo` (output\log_flujo.txt).
2. Obtener la fecha y hora actuales -> `CurrentDateTime`.
3. Ejecutar comando DOS: `ejecutar.bat` (corre `python src\main.py`), guarda el código de salida en `CodigoSalida`.
4. Si el archivo `Reporte` existe:
   - Si `CodigoSalida` = 0: escribe "OK" con fecha y hora en `log_flujo.txt` y muestra "Reporte generado correctamente".
   - Si no: escribe "FALLO codigo N" en el log y muestra aviso de fallo.
5. Si el reporte no existe: escribe "FALLO: no se genero el reporte" y muestra aviso.

`ejecutar.bat` escribe además `output\log.txt` y devuelve código 2 si no se generó el reporte.

## Evidencia
- `docs/flujo_pad_captura.png`: flujo ejecutándose con éxito.
- `docs/flujo_pad_fallo.png`: aviso de fallo al renombrar `src\main.py` (CodigoSalida = 2).
- Logs reales de esa prueba: `23/11/2026 6:32:34 p. m. - OK` y `23/11/2026 6:33:45 p. m. - FALLO codigo 2`.

## Limitación
El flujo vive en la cuenta/equipo de Power Automate, no en el repositorio. Para exportarlo: en el diseñador, seleccionar todas las acciones, copiarlas y pegarlas en un .txt.
