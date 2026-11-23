"""Ejecuta sql/consultas.sql y guarda cada resultado en output/consulta_{a,b,c}.csv."""
import csv
import sqlite3

from config import DB, RAIZ, SALIDA


def ejecutar():
    bloques = [b.strip() for b in (RAIZ / "sql" / "consultas.sql").read_text(encoding="utf-8").split(";") if "SELECT" in b]
    con = sqlite3.connect(DB)
    for letra, sql in zip("abc", bloques):
        cur = con.execute(sql)
        with open(SALIDA / f"consulta_{letra}.csv", "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow([c[0] for c in cur.description])
            w.writerows(cur.fetchall())
    con.close()
