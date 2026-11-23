# Automatizador de solicitudes – Talento Andino S.A.S. (reto técnico)

Clasifica solicitudes de empleados, valida reglas de negocio y genera un reporte para RRHH.
La IA nunca decide sola: casos dudosos pasan a revisión humana con motivo.

## Instalar y ejecutar
```
pip install -r requirements.txt
copy .env.example .env     # opcional: pega tu GEMINI_API_KEY
python src/main.py
python -m pytest -q
```
Sin clave de Gemini usa un clasificador por reglas (columna `fuente` del reporte).

## Salidas (`output/`)
`reporte_solicitudes.csv`, `metricas.txt` (exactitud), `consulta_a/b/c.csv`, `limpieza.md`, `log.txt`.
La base SQLite se recrea en `output/talento_andino.db`.

## Decisiones técnicas
Solo librería estándar + pytest. SQLite sin FK en solicitudes (hay empleados inexistentes).
Datos personales enmascarados antes de llamar a Gemini. JSON del modelo validado.
Festivos: API Nager.Date con timeout, 3 reintentos y respaldo local. Detalle completo en `GUIA_DECISIONES.md`.

## Limitaciones conocidas
Fechas por regex, reglas de palabras clave, sin lotes en IA, saldo no se descuenta entre solicitudes, sin tablero.

## Power Automate
Ver `docs/power_automate.md` y `FICHA_INVENTARIO.md`.

## Uso de IA
Se usó un asistente de IA (Claude) para programar; el autor debe poder explicar cada parte.

## Seguridad
`.env` está en `.gitignore`. Si se sube una clave por error: revocarla de inmediato y anotarlo aquí.
