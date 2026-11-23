# Explicación a fondo de cada archivo y cada código

Orden del flujo real: `main.py` → `db.py` → `consultas.py` → `festivos.py` → `reporte.py`
(que usa `clasif_ia.py`, `clasif_reglas.py`, `enmascarar.py`, `dias.py`, `revision.py`).
Todos los archivos de `src/` están en la misma carpeta, por eso se importan por nombre (`import db`).

---
## 1. `src/main.py` – el director
Es lo único que ejecutas: `python src/main.py`.
- `main()` hace los pasos en orden: (1) `db.cargar()` limpia y carga datos y devuelve la lista de acciones de limpieza, que se imprime; (2) `consultas.ejecutar()` guarda las 3 consultas; (3) `obtener_festivos()` trae los festivos; (4) `procesar(festivos)` clasifica y genera el reporte; imprime exactitud y cuántos casos van a revisión.
- El bloque `if __name__ == "__main__"` ejecuta `main()` dentro de `try/except`. Si algo falla imprime `ERROR: ...` y hace `sys.exit(1)`. **Ese código 1 es el que lee `ejecutar.bat`/Power Automate** para saber que falló (0 = éxito).

## 2. `src/config.py` – configuración central
- `RAIZ = Path(__file__).resolve().parent.parent`: carpeta del proyecto, calculada desde la ubicación del archivo, así funciona desde cualquier carpeta y aunque la ruta tenga Ñ.
- `DATOS`, `SALIDA`, `DB`: rutas a `data/`, `output/` y a `output/talento_andino.db`.
- `CATEGORIAS`: las 5 categorías válidas. Se usan para validar la respuesta de la IA.
- `UMBRAL_CONFIANZA = 0.7`: por debajo, la solicitud va a revisión humana.
- `ANIO_FESTIVOS = 2026`.
- `cargar_env()`: lee `.env` a mano (sin librería `python-dotenv`). Por cada línea con `=` que no empiece con `#`, separa clave y valor (`split("=", 1)` para que valores con `=` no se rompan) y usa `os.environ.setdefault` (si la variable ya existe en el sistema, esa gana).
- `GROQ_API_KEY` / `GROQ_MODEL`: se leen del entorno tras cargar `.env`. Sin clave queda `""` y el sistema usa reglas.

## 3. `src/db.py` – Misión 1: base de datos y limpieza
- `ESQUEMA`: SQL que borra y crea las tablas (`DROP TABLE IF EXISTS` → se puede ejecutar muchas veces).
  - `empleados`: `id_empleado` **PRIMARY KEY**; `correo` **UNIQUE**; `dias_vacaciones INTEGER CHECK (>= 0)`; `nombre`, `correo`, `area` **NOT NULL**.
  - `solicitudes`: `id_solicitud` PRIMARY KEY; `id_empleado` **sin FOREIGN KEY** a propósito (hay solicitudes de E009, que no existe; una FK las rechazaría y las necesito para marcarlas a revisión).
- `limpiar_empleados(filas)`: recorre las filas y mantiene un `set` de ids vistos.
  - **Duplicado**: si el id ya se vio, se omite la fila y se anota en el log.
  - **Correo**: `.strip().lower()`; si cambió, se anota.
  - **Área vacía**: se pone `"Sin área"` (no se inventa un área real) y se anota.
  - Devuelve `(filas_limpias, log)`.
- `cargar()`: crea `output/` si no existe; lee el CSV con `csv.DictReader` y encoding **`utf-8-sig`** (tolera el BOM invisible que añade Windows; sin eso la primera columna se llama `﻿id_empleado` y falla); limpia; lee el JSON; abre SQLite; ejecuta el esquema; inserta con `executemany` y **parámetros `?`** (evita inyección SQL y problemas con comillas); convierte días a `int`; hace `commit`; escribe `output/limpieza.md` con el log.

## 4. `sql/consultas.sql` – las 3 consultas
- **(a)** `solicitudes LEFT JOIN empleados` agrupado por categoría y área, con `COALESCE(e.area, 'Empleado inexistente')` para no perder la solicitud de E009. Usa `etiqueta_esperada` como categoría (la que traen los datos).
- **(b)** `LEFT JOIN ... WHERE e.id_empleado IS NULL`: truco clásico para encontrar solicitudes sin empleado correspondiente (resultado: S10/E009).
- **(c)** `WHERE dias_vacaciones < 5`: devuelve E008 (0) y E006 (3). E004 tiene exactamente 5 → no entra.
- Cuidado: **no pongas `;` dentro de los comentarios**, porque `consultas.py` separa las consultas por `;`.

## 5. `src/consultas.py`
- `ejecutar()` lee el `.sql`, lo parte por `;`, se queda con los bloques que contienen `SELECT`, y para cada uno (con `zip("abc", bloques)` → a, b, c) ejecuta y escribe `output/consulta_X.csv`. Los nombres de columna salen de `cursor.description`. Es corto porque reutiliza el SQL en vez de duplicarlo en Python.

## 6. `src/festivos.py` – Misión 2: API REST
- `URL` con `{anio}` y `CO` (Colombia) de Nager.Date. No requiere clave.
- `obtener_festivos(anio, intentos=3, timeout=10)`:
  - Bucle `for n in range(1, intentos+1)` con `try`: `urlopen` con **timeout 10 s**; si responde, guarda la respuesta en `data/festivos_CO_2026.json` (**respaldo**) y hace `break`.
  - `except Exception`: imprime el fallo, espera `n` segundos (**espera creciente**: 1, 2, 3) y reintenta.
  - `for ... else`: el `else` solo corre si el bucle terminó **sin break** (los 3 intentos fallaron). Entonces: si existe el respaldo, lo usa; si no, lanza `RuntimeError` con mensaje claro.
  - Devuelve un `set` de fechas `"AAAA-MM-DD"` (rápido de consultar con `in`).

## 7. `src/dias.py` – días hábiles
- `dias_habiles(inicio, fin, festivos)`: convierte los textos ISO a `date`; si `fin < inicio` lanza `ValueError`; recorre día por día (ambos extremos incluidos) y suma si `weekday() < 5` (lunes=0 … viernes=4) **y** la fecha no está en festivos. Verificado: S01=5, S05=4 (8-dic festivo), S06=8 (25-dic festivo).

## 8. `src/enmascarar.py` – protección de datos
- `_REGLAS`: lista de pares (regex compilada, etiqueta). **El orden importa**:
  1. Correo `[\w.+-]+@[\w-]+(\.[\w-]+)+` → `[CORREO]`.
  2. Celular colombiano `\b3\d{9}\b` (empieza en 3, 10 dígitos) → `[CELULAR]`.
  3. Documento `\b\d{6,10}\b` → `[DOCUMENTO]`. Va último porque si fuera antes, se comería los celulares.
- `enmascarar(texto)` aplica cada regla con `.sub`. Se llama **antes** de enviar cualquier texto a Groq. Los años (4 dígitos) no se tocan.

## 9. `src/clasif_reglas.py` – clasificador sin IA (plan B)
- `MESES`: diccionario nombre → número, construido con `enumerate(..., 1)`.
- `REGLAS`: lista `(categoría, regex, confianza)`; **gana la primera que coincide**, por eso INCAPACIDAD va antes de VACACIONES. "días libres" tiene confianza 0.6 (ambiguo) para que caiga en revisión. `actual[ií]c` acepta con y sin tilde (bug real que corregí en S11).
- `extraer_fechas(texto, recepcion)`:
  - Patrón `del 14 al 18 de diciembre de 2026` (año opcional; si falta usa el de la fecha de recepción).
  - Patrón `desde el 3 de noviembre` + `N días` → fin = inicio + N − 1.
  - Si no hay fechas devuelve `(None, None)`.
- `clasificar_reglas(texto, recepcion)`: por defecto `OTRO` con 0.5; recorre las reglas; solo extrae fechas para VACACIONES e INCAPACIDAD; devuelve un dict con la misma forma que la IA y `fuente: "reglas"`.

## 10. `src/clasif_ia.py` – Misión 3: IA (Groq)
- `URL`: endpoint de Groq compatible con OpenAI (`/openai/v1/chat/completions`).
- `PROMPT`: pide **solo JSON** con `categoria`, `confianza`, `fecha_inicio`, `fecha_fin`, indica la lista de categorías y la fecha de recepción (para resolver años faltantes).
- `validar(obj)`: el contrato. Lanza `ValueError` si la categoría no está en `CATEGORIAS`, si la confianza no es número entre 0 y 1, o si una fecha no es ISO válida (`date.fromisoformat`). Devuelve solo las 4 claves esperadas (descarta extras). Nunca se usa la salida del modelo sin pasar por aquí.
- `_llamar_groq(texto, recepcion)`: arma el cuerpo: `model`, `temperature: 0` (respuestas estables), `response_format: json_object` (obliga JSON) y el mensaje. Cabeceras: `Authorization: Bearer <clave>` y un `User-Agent` propio (Groq/Cloudflare rechaza el de urllib por defecto). `timeout=30`. Lee `choices[0].message.content` y lo convierte con `json.loads`.
- `clasificar(texto, recepcion)`: si hay clave → llama a Groq con el **texto enmascarado** y valida; éxito → `fuente: "groq"`. Cualquier error (red, 404, JSON malo, validación) se imprime y se **cae a reglas**: el sistema nunca se detiene por la IA.

## 11. `src/revision.py` – reglas de revisión humana
`evaluar_revision(empleado, cat, confianza, dias, saldo_ok)` devuelve una **lista de motivos** (vacía = no requiere revisión):
1. Empleado inexistente.
2. Confianza < 0.7 (el motivo incluye el valor).
3. Si es VACACIONES: sin días calculados → "sin fechas"; o saldo insuficiente → "Pide X días hábiles y solo tiene Y".
Puede haber varios motivos a la vez (S09: confianza baja + sin fechas). Se separan con `;` en el reporte.

## 12. `src/reporte.py` – el motor que une todo
- `COLUMNAS`: orden de columnas del CSV pedido por el reto.
- `procesar(festivos)`:
  - Abre la base con `row_factory = sqlite3.Row` (acceso por nombre de columna) y carga empleados en un dict por id.
  - Por cada solicitud: clasifica → busca empleado → si es VACACIONES con ambas fechas, calcula días hábiles → `saldo_ok = empleado existe y días <= saldo` → evalúa revisión → compara con `etiqueta_esperada` (aciertos/errores).
  - Arma la fila: `saldo_suficiente` es `SI/NO` solo cuando aplica, si no `N/A`; `requiere_revision` `SI/NO`; `motivo`; `fuente` (groq o reglas).
  - Escribe `output/reporte_solicitudes.csv` con encoding **`utf-8-sig`** (para que Excel muestre bien las tildes).
  - Escribe `output/metricas.txt`: exactitud (aciertos/total) y la lista de errores. Devuelve filas y texto de métricas.

## 13. `tests/test_reto.py` – pruebas (pytest)
- Agrega `src/` al `sys.path` para poder importar los módulos.
- `test_dias_habiles`: parametrizada con los 3 casos del reto (5, 4, 8).
- `test_enmascarar_datos_personales`: comprueba que cédula, celular y `@` desaparecen y que están las 3 etiquetas.
- `test_revision_dias_mayores_al_saldo`: saldo 0 con 8 días → motivo; saldo suficiente → sin motivo.
- `test_revision_empleado_inexistente_y_sin_fechas`.
- `test_json_invalido_del_modelo_se_rechaza`: categoría inventada → `ValueError`.
Total: 7 pruebas (la parametrizada cuenta 3). Ejecutar: `python -m pytest -q`.

## 14. Archivos de datos (`data/`)
- `empleados.csv`, `solicitudes.json`: datos ficticios del reto, con las trampas (duplicado, correo sucio, área vacía, empleado inexistente).
- `festivos_CO_2026.json`: se crea solo, es la última respuesta buena de la API (respaldo).

## 15. Archivos de configuración y soporte
- `.env`: tu clave real de Groq. **Nunca se sube** (está en `.gitignore`).
- `.env.example`: plantilla sin clave, sí se sube.
- `.gitignore`: ignora `.env`, `__pycache__/`, `.pytest_cache/`, `*.db`.
- `requirements.txt`: solo `pytest` (todo lo demás es librería estándar de Python).
- `ejecutar.bat`: ejecuta `python src\main.py`, redirige la salida a `output\ultima_ejecucion.txt`, lee el código de salida (`ERRORLEVEL`), comprueba que exista el reporte (si no, código 2), y agrega a `output\log.txt` fecha, hora y OK/FALLO. Termina con `exit /b` con ese código para que Power Automate lo lea. `%~dp0` = carpeta del .bat, así funciona desde cualquier lugar.
- `.github/workflows/tests.yml`: GitHub Actions; en cada `push` instala Python 3.11, `pytest` y corre las pruebas (bonus).

## 16. Documentación
- `README.md`: instalar, ejecutar, decisiones, limitaciones (lo que lee quien evalúa).
- `FICHA_INVENTARIO.md`: nombre, disparador, entradas, salidas, responsable, riesgos y monitoreo.
- `docs/power_automate.md`: pasos para armar el flujo de escritorio.
- `GUIA_DECISIONES.md`: tecnologías y por qué de cada decisión.
- `EXPLICACION_ARCHIVOS.md`: este archivo.

## 17. Carpeta `output/` (se genera sola)
`reporte_solicitudes.csv` (entregable), `metricas.txt`, `consulta_a/b/c.csv`, `limpieza.md`, `log.txt`, `ultima_ejecucion.txt`, `talento_andino.db`.

---
## Cómo se conecta todo (resumen para explicar en la demo)
CSV/JSON → **db.py** limpia y guarda en SQLite → **festivos.py** trae festivos →
por cada solicitud, **enmascarar.py** oculta datos → **clasif_ia.py** (Groq, o **clasif_reglas.py** si falla) clasifica →
**dias.py** calcula días hábiles → **revision.py** decide si va a humano → **reporte.py** escribe el CSV y la exactitud →
**ejecutar.bat**/Power Automate lo lanza, verifica y registra el log.
