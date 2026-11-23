# Guía completa: qué se hizo y por qué (para ti, para la entrevista)

## 1. Qué hace el proyecto en una frase
Lee empleados y solicitudes → limpia y guarda en SQLite → trae festivos de Colombia por API →
clasifica cada solicitud (IA Groq, o reglas si no hay clave) → calcula días hábiles →
aplica reglas de revisión humana → escribe `output/reporte_solicitudes.csv`.

## 2. Tecnologías y dependencias (todo gratis)
| Pieza | Qué es | Por qué |
|---|---|---|
| **Python 3.11** | Lenguaje | Lo pide el reto; tiene todo incluido |
| **SQLite** (módulo `sqlite3`) | Base de datos en un archivo | Viene con Python, cero instalación |
| **urllib** (stdlib) | Llamadas HTTP | Evité `requests`: una dependencia menos |
| **csv / json / re / datetime** (stdlib) | Leer datos, regex, fechas | Suficiente para todo |
| **pytest** | Pruebas | ÚNICA dependencia externa (`requirements.txt`) |
| **Nager.Date API** | Festivos de Colombia | Pedida en Misión 2, sin clave |
| **Groq API** (REST) | Modelo de IA | Nivel gratis; se llama con HTTP simple, sin SDK |
| **Power Automate Desktop** | Orquestación | Misión 4, opción A (gratis en Windows) |
| **GitHub Actions** | Corre pytest en cada push | Bonus |
| **Git** | Control de versiones | Misión 5 |

**No se usó ningún framework** (ni Django, Flask, pandas, SDK de Google…). Fue decisión deliberada:
proyecto pequeño, fácil de explicar línea por línea en la entrevista.

## 3. Estructura de archivos (cada uno corto, una sola responsabilidad)
```
data/            empleados.csv, solicitudes.json (datos del reto) + festivos_CO_2026.json (respaldo API)
sql/consultas.sql  las 3 consultas de la Misión 1
src/config.py      rutas, umbral de confianza, lee .env a mano
src/db.py          crea esquema, limpia y carga (Misión 1)
src/consultas.py   ejecuta el .sql y guarda CSV
src/festivos.py    API Nager con timeout, reintentos y respaldo (Misión 2)
src/dias.py        cálculo de días hábiles
src/enmascarar.py  oculta correo, celular y documento
src/clasif_reglas.py  clasificador sin IA (también es el plan B)
src/clasif_ia.py   Groq + validación del JSON
src/revision.py    reglas de revisión humana
src/reporte.py     une todo y genera reporte + métricas
src/main.py        punto de entrada
tests/test_reto.py  7 pruebas
ejecutar.bat       lo que llama Power Automate
output/            todo lo generado (reporte, consultas, log, limpieza)
```

## 4. Decisiones por misión
### Misión 1 – Datos
- **Esquema**: `empleados.id_empleado` PRIMARY KEY, `correo` UNIQUE, `dias_vacaciones` INTEGER ≥ 0.
  `solicitudes` **sin llave foránea** a propósito: hay solicitudes de empleados inexistentes (E009) y
  una FK las rechazaría; las necesito cargadas para marcarlas a revisión.
- **Trampas encontradas**: E003 duplicado (se descarta la 2ª fila), correo de E002 con mayúsculas y
  espacio (se normaliza), E004 sin área (se pone "Sin área", no se inventa). Queda en `output/limpieza.md`.
- **Consulta (a)** usa `etiqueta_esperada` como categoría porque es la que viene en los datos;
  la clasificación de la IA se evalúa aparte. LEFT JOIN para no perder al empleado inexistente.
- Leo el CSV con `utf-8-sig` porque Windows/Excel a veces agregan un BOM invisible que rompe el nombre de la primera columna (me pasó).

### Misión 2 – Días hábiles
- Cuenta lunes–viernes que no estén en festivos, **incluyendo inicio y fin**.
- Verificado con el reto: S01=5, S05=4, S06=8 (están como pruebas).
- Errores: timeout 10 s, 3 intentos con espera creciente, y si todo falla usa
  `data/festivos_CO_2026.json` (la última respuesta buena). Si tampoco existe, falla con mensaje claro.

### Misión 3 – IA
- Groq por REST, `response_format: json_object`, `temperature: 0` (respuestas estables).
- **Validación**: categoría ∈ 5 válidas, confianza 0–1, fechas ISO reales. Si no cumple → se descarta y se usan reglas.
- **Enmascarado antes de enviar**: correo → `[CORREO]`, celular (3 + 9 dígitos) → `[CELULAR]`, documento (6–10 dígitos) → `[DOCUMENTO]`. El orden importa: primero correo y celular, luego documento.
- La clave va en header `Authorization: Bearer` (no en la URL, para que no quede en logs) y se lee de `.env`.
- **Sin clave funciona igual** con reglas (plan B). En el reporte la columna `fuente` dice `Groq` o `reglas`.
  *Importante*: el máximo de 12 pts aplica si NO usas API de IA; para los 25 pts crea tu clave gratis en
  https://console.groq.com/keys, ponla en `.env` y ejecuta de nuevo.
- **Exactitud**: se compara con `etiqueta_esperada`; sale en `output/metricas.txt` con la lista de errores.
  Las reglas fallaron primero en S11 ("actualícenlo" con tilde); lo corregí con regex `actual[ií]c`.
- **Revisión humana** (`revision.py`): empleado inexistente, confianza < 0.7, vacaciones sin fechas,
  días > saldo. Cada caso guarda su motivo. Resultado esperado: S06, S08, S09, S10 a revisión.

### Misión 4 – Power Automate (opción A)
Ver `docs/power_automate.md`. Python devuelve código de salida ≠ 0 si falla; `ejecutar.bat` escribe el log.
**Esto no lo puedo hacer yo**: el flujo se construye en la interfaz de Power Automate y debes tomar capturas.

### Misión 5 – Calidad
- 7 pruebas pytest (días hábiles x3, enmascarado, 2 de revisión, JSON inválido).
- `.env` en `.gitignore`; `.env.example` sin clave. Revisa `git log -p` antes de subir: no debe haber claves.
- README + `FICHA_INVENTARIO.md`. Debes indicar en el README que usaste asistente de IA (ya está).
- Bonus: GitHub Actions (`.github/workflows/tests.yml`). Faltan tablero y video.

## 5. Limitaciones (di esto en la entrevista, se valora)
- Fechas por regex: solo entiende "del X al Y de mes" y "desde el X de mes".
- Reglas de clasificación son por palabras clave; frágiles ante textos nuevos.
- Cada solicitud va a Groq una por una (sin lotes); con el límite gratuito puede fallar y cae a reglas.
- Saldo de vacaciones no se descuenta ni considera solicitudes previas del mismo empleado.
- Reporte CSV; no hay tablero. Datos personales en la base local sin cifrar.
- Para producción con TI: base real (SQL Server/Postgres), secretos en un gestor (Key Vault), ejecución programada, monitoreo/alertas, acuerdo de datos con el proveedor de IA.

## 6. Cómo ejecutar
```powershell
pip install -r requirements.txt
python src\main.py
python -m pytest -q
```

## 7. Pendientes tuyos
1. Crear clave Groq y ponerla en `.env` (para puntaje completo de IA).
2. Construir el flujo en Power Automate Desktop + capturas en `docs/`.
3. Crear repo en GitHub y hacer `git remote add origin ...` + `git push`.
4. (Opcional) video de 3 min.
