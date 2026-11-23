"""Reglas de revisión humana: la IA nunca decide sola."""
from config import UMBRAL_CONFIANZA


def evaluar_revision(empleado, cat, confianza, dias, saldo_ok):
    """Devuelve la lista de motivos; vacía = no requiere revisión."""
    motivos = []
    if empleado is None:
        motivos.append("Empleado inexistente en la nómina")
    if confianza < UMBRAL_CONFIANZA:
        motivos.append(f"Confianza baja ({confianza:.2f} < {UMBRAL_CONFIANZA})")
    if cat == "VACACIONES":
        if dias is None:
            motivos.append("Vacaciones sin fechas")
        elif empleado is not None and not saldo_ok:
            motivos.append(f"Pide {dias} días hábiles y solo tiene {empleado['dias_vacaciones']}")
    return motivos
