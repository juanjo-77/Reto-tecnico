"""Días hábiles (lunes a viernes, sin festivos), ambos extremos incluidos."""
from datetime import date, timedelta


def dias_habiles(inicio, fin, festivos):
    """inicio/fin: 'AAAA-MM-DD'; festivos: set de 'AAAA-MM-DD'."""
    d, f, total = date.fromisoformat(inicio), date.fromisoformat(fin), 0
    if f < d:
        raise ValueError("fecha_fin anterior a fecha_inicio")
    while d <= f:
        if d.weekday() < 5 and d.isoformat() not in festivos:
            total += 1
        d += timedelta(days=1)
    return total
