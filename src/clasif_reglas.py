"""Clasificador por reglas: respaldo cuando no hay API de IA (o esta falla)."""
import re
from datetime import date, timedelta

MESES = {m: i for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(), 1)}

# (categoría, patrón, confianza); el orden importa: la primera que coincide gana
REGLAS = [
    ("INCAPACIDAD", r"incapacidad", 0.9),
    ("CERTIFICADO_LABORAL", r"certificado laboral|constancia", 0.9),
    ("VACACIONES", r"vacaciones", 0.95),
    ("VACACIONES", r"d[ií]as libres", 0.6),  # ambiguo -> confianza baja
    ("ACTUALIZACION_DATOS", r"actual[ií]c|actualiz", 0.9),
]


def extraer_fechas(texto, recepcion):
    """'del 14 al 18 de diciembre de 2026' o 'desde el 3 de noviembre' -> (inicio, fin|None)."""
    anio = int(recepcion[:4])
    m = re.search(r"del (\d{1,2}) al (\d{1,2}) de (\w+)(?: de (\d{4}))?", texto, re.I)
    if m and m[3].lower() in MESES:
        mes, a = MESES[m[3].lower()], int(m[4] or anio)
        return date(a, mes, int(m[1])).isoformat(), date(a, mes, int(m[2])).isoformat()
    m = re.search(r"desde el (\d{1,2}) de (\w+)", texto, re.I)
    if m and m[2].lower() in MESES:
        ini = date(anio, MESES[m[2].lower()], int(m[1]))
        n = re.search(r"(\d+) d[ií]as", texto)
        fin = ini + timedelta(days=int(n[1]) - 1) if n else None
        return ini.isoformat(), fin.isoformat() if fin else None
    return None, None


def clasificar_reglas(texto, recepcion):
    cat, conf = "OTRO", 0.5
    for c, patron, p in REGLAS:
        if re.search(patron, texto, re.I):
            cat, conf = c, p
            break
    ini, fin = extraer_fechas(texto, recepcion) if cat in ("VACACIONES", "INCAPACIDAD") else (None, None)
    return {"categoria": cat, "confianza": conf, "fecha_inicio": ini, "fecha_fin": fin, "fuente": "reglas"}
