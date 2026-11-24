"""Misión 1: carga CSV/JSON a SQLite, limpia y documenta cada caso."""
import csv
import json
import sqlite3
from pathlib import Path

from config import DATOS, DB, SALIDA

ESQUEMA = """
DROP TABLE IF EXISTS empleados;
DROP TABLE IF EXISTS solicitudes;
CREATE TABLE empleados (
  id_empleado TEXT PRIMARY KEY,
  nombre TEXT NOT NULL,
  correo TEXT NOT NULL UNIQUE,
  area TEXT NOT NULL,
  cargo TEXT,
  fecha_ingreso TEXT,
  dias_vacaciones INTEGER NOT NULL CHECK (dias_vacaciones >= 0),
  documento TEXT
);
CREATE TABLE solicitudes (
  id_solicitud TEXT PRIMARY KEY,
  id_empleado TEXT NOT NULL,   -- sin FK a propósito: hay empleados inexistentes
  fecha_recepcion TEXT,
  canal TEXT,
  texto TEXT NOT NULL,
  etiqueta_esperada TEXT
);
"""


def limpiar_empleados(filas):
    """Devuelve (filas limpias, lista de acciones de limpieza)."""
    vistos, limpias, log = set(), [], []
    for f in filas:
        if f["id_empleado"] in vistos:
            log.append(f"Duplicado {f['id_empleado']} ({f['nombre']}): se descartó la segunda fila.")
            continue
        vistos.add(f["id_empleado"])
        correo = f["correo"].strip().lower()
        if correo != f["correo"]:
            log.append(f"{f['id_empleado']}: correo '{f['correo']}' -> '{correo}' (minúsculas y sin espacios).")
        f["correo"] = correo
        if not f["area"].strip():
            f["area"] = "Sin área"
            log.append(f"{f['id_empleado']}: área vacía -> 'Sin área' (pendiente que RRHH la confirme).")
        limpias.append(f)
    return limpias, log


def cargar(ruta_solicitudes=None):
    SALIDA.mkdir(exist_ok=True)
    with open(DATOS / "empleados.csv", encoding="utf-8-sig", newline="") as fh:  # utf-8-sig tolera el BOM de Excel/Windows
        emp, log = limpiar_empleados(list(csv.DictReader(fh)))
    sol = json.loads(Path(ruta_solicitudes or DATOS / "solicitudes_limpio.json").read_text(encoding="utf-8-sig"))
    con = sqlite3.connect(DB)
    con.executescript(ESQUEMA)
    con.executemany(
        "INSERT INTO empleados VALUES (?,?,?,?,?,?,?,?)",
        [(e["id_empleado"], e["nombre"], e["correo"], e["area"], e["cargo"],
          e["fecha_ingreso"], int(e["dias_vacaciones_disponibles"]), e["documento"]) for e in emp])
    con.executemany(
        "INSERT INTO solicitudes VALUES (:id_solicitud,:id_empleado,:fecha_recepcion,:canal,:texto,:etiqueta_esperada)", sol)
    con.commit()
    con.close()
    (SALIDA / "limpieza.md").write_text("# Limpieza de datos\n\n" + "\n".join(f"- {l}" for l in log) + "\n", encoding="utf-8")
    return log
