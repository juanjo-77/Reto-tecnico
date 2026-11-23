"""Une todo: clasifica, calcula días hábiles, aplica reglas y escribe el reporte + métricas."""
import csv
import sqlite3

from clasif_ia import clasificar
from config import DB, SALIDA
from dias import dias_habiles
from revision import evaluar_revision

COLUMNAS = ["id_solicitud", "id_empleado", "empleado", "area", "categoria", "confianza", "fecha_inicio",
            "fecha_fin", "dias_habiles", "saldo_suficiente", "requiere_revision", "motivo", "fuente"]


def procesar(festivos):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    emps = {e["id_empleado"]: e for e in con.execute("SELECT * FROM empleados")}
    filas, aciertos, errores = [], 0, []
    for s in con.execute("SELECT * FROM solicitudes ORDER BY id_solicitud"):
        r = clasificar(s["texto"], s["fecha_recepcion"])
        emp = emps.get(s["id_empleado"])
        dias = None
        if r["categoria"] == "VACACIONES" and r["fecha_inicio"] and r["fecha_fin"]:
            dias = dias_habiles(r["fecha_inicio"], r["fecha_fin"], festivos)
        saldo_ok = emp is not None and dias is not None and dias <= emp["dias_vacaciones"]
        motivos = evaluar_revision(emp, r["categoria"], r["confianza"], dias, saldo_ok)
        if r["categoria"] == s["etiqueta_esperada"]:
            aciertos += 1
        else:
            errores.append(f"{s['id_solicitud']}: esperada {s['etiqueta_esperada']}, obtenida {r['categoria']}")
        filas.append({
            "id_solicitud": s["id_solicitud"], "id_empleado": s["id_empleado"],
            "empleado": emp["nombre"] if emp else "(no existe)", "area": emp["area"] if emp else "",
            "categoria": r["categoria"], "confianza": r["confianza"],
            "fecha_inicio": r["fecha_inicio"] or "", "fecha_fin": r["fecha_fin"] or "",
            "dias_habiles": "" if dias is None else dias,
            "saldo_suficiente": "N/A" if dias is None or emp is None else ("SI" if saldo_ok else "NO"),
            "requiere_revision": "SI" if motivos else "NO", "motivo": "; ".join(motivos), "fuente": r["fuente"]})
    con.close()
    with open(SALIDA / "reporte_solicitudes.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, COLUMNAS)
        w.writeheader()
        w.writerows(filas)
    total = len(filas)
    texto = f"Exactitud: {aciertos}/{total} = {aciertos / total:.0%}\nErrores:\n" + ("\n".join(errores) or "ninguno")
    (SALIDA / "metricas.txt").write_text(texto + "\n", encoding="utf-8")
    return filas, texto
