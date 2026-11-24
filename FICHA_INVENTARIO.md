# Ficha de inventario de la automatización

| Campo | Valor |
|---|---|
| Nombre | Automatizador de solicitudes de empleados |
| Disparador | Flujo de Power Automate Desktop (manual o programado, p. ej. diario 7:00) |
| Entradas | `data/empleados.csv`, `data/solicitudes_limpio.json` o `data/solicitudes_dudosos.json`, API Nager.Date, API Groq (texto enmascarado) |
| Salidas | `output/reporte_solicitudes.csv`, `metricas.txt`, `consulta_*.csv`, `log.txt` |
| Responsable | (tu nombre) – dueño funcional: Recursos Humanos |
| Riesgos | Datos personales (se enmascaran antes de la IA); clasificación errónea (revisión humana y umbral 0.7); API caída (respaldo local); clave expuesta (`.env` fuera de git) |
| Monitoreo | `output/log.txt` (fecha, hora, resultado), aviso en pantalla si falla, `metricas.txt` con exactitud y casos a revisión |
