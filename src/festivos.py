"""Misión 2: festivos de Colombia desde Nager.Date, con reintentos y respaldo local."""
import json
import time
import urllib.request

from config import ANIO_FESTIVOS, DATOS

URL = "https://date.nager.at/api/v3/PublicHolidays/{anio}/CO"


def obtener_festivos(anio=ANIO_FESTIVOS, intentos=3, timeout=10):
    """Set de fechas ISO festivas. Si la API falla, usa la última respuesta guardada."""
    respaldo = DATOS / f"festivos_CO_{anio}.json"
    for n in range(1, intentos + 1):
        try:
            with urllib.request.urlopen(URL.format(anio=anio), timeout=timeout) as r:
                datos = json.load(r)
            respaldo.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
            break
        except Exception as e:  # red caída, timeout, JSON inválido...
            print(f"[festivos] intento {n}/{intentos} falló: {e}")
            time.sleep(n)  # espera creciente
    else:
        if not respaldo.exists():
            raise RuntimeError("API de festivos caída y no hay respaldo local")
        print("[festivos] usando respaldo local")
        datos = json.loads(respaldo.read_text(encoding="utf-8"))
    return {d["date"] for d in datos}
