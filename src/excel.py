"""Reporte en Excel legible para RRHH (el CSV se mantiene para Power Automate)."""
from collections import Counter
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from config import SALIDA

TIPOS = {"VACACIONES": "Vacaciones", "CERTIFICADO_LABORAL": "Certificado laboral", "INCAPACIDAD": "Incapacidad",
         "ACTUALIZACION_DATOS": "Actualización de datos", "OTRO": "Otro"}
# (título, clave en la fila, ancho)
COLS = [("Solicitud", "id_solicitud", 11), ("Cód. empleado", "id_empleado", 14), ("Empleado", "empleado", 20),
        ("Área", "area", 18), ("Tipo de solicitud", "categoria", 24), ("Confianza", "confianza", 11),
        ("Desde", "fecha_inicio", 12), ("Hasta", "fecha_fin", 12), ("Días hábiles", "dias_habiles", 10),
        ("¿Le alcanzan los días?", "saldo_suficiente", 14), ("¿Requiere revisión?", "requiere_revision", 14),
        ("Motivo", "motivo", 48), ("Clasificado por", "fuente", 14)]
AZUL, ROJO, VERDE = "1F3864", "FDE2E1", "E6F4EA"


def _valor(clave, f):
    v = f[clave]
    if clave == "categoria":
        return TIPOS.get(v, v)
    if clave == "confianza":
        return float(v)
    if clave == "saldo_suficiente":
        return {"SI": "Sí", "NO": "No", "N/A": "No aplica"}[v]
    if clave == "requiere_revision":
        return "REVISAR" if v == "SI" else "No"
    if clave == "dias_habiles":
        return v if v != "" else None
    return v or None


def escribir(filas, aciertos):
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"
    ws.append([c[0] for c in COLS])
    for i, (_, _, ancho) in enumerate(COLS, 1):
        ws.column_dimensions[get_column_letter(i)].width = ancho
        celda = ws.cell(1, i)
        celda.font, celda.fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor=AZUL)
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 32
    for f in filas:
        ws.append([_valor(k, f) for _, k, _ in COLS])
        revisar = f["requiere_revision"] == "SI"
        for c in ws[ws.max_row]:
            c.fill = PatternFill("solid", fgColor=ROJO if revisar else VERDE)
            c.alignment = Alignment(vertical="center", wrap_text=True, horizontal="left" if c.column == 12 else "center")
        ws.cell(ws.max_row, 6).number_format = "0%"
        if revisar:
            ws.cell(ws.max_row, 11).font = Font(bold=True, color="C00000")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    r = wb.create_sheet("Resumen")
    revisar = sum(f["requiere_revision"] == "SI" for f in filas)
    for fila in [("Solicitudes procesadas", len(filas)), ("Requieren revisión humana", revisar),
                 ("Se pueden procesar sin revisar", len(filas) - revisar),
                 ("Acierto de la clasificación", f"{aciertos}/{len(filas)}"), (), ("Por tipo de solicitud", "Cantidad")]:
        r.append(fila)
    for tipo, n in Counter(TIPOS.get(f["categoria"], f["categoria"]) for f in filas).most_common():
        r.append((tipo, n))
    r.column_dimensions["A"].width, r.column_dimensions["B"].width = 36, 14
    for celda in (r["A6"], r["B6"]):
        celda.font = Font(bold=True)
    r["B2"].font = Font(bold=True, color="C00000")
    try:
        wb.save(SALIDA / "reporte_solicitudes.xlsx")
    except PermissionError:  # el Excel está abierto y Windows lo bloquea: no perder el resultado
        alterno = SALIDA / f"reporte_solicitudes_{datetime.now():%H%M%S}.xlsx"
        wb.save(alterno)
        print(f"AVISO: cierra el Excel; el reporte se guardó como {alterno.name}")
