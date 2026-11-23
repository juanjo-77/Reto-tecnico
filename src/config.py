"""Rutas y variables de entorno (lee .env sin dependencias extra)."""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"
SALIDA = RAIZ / "output"
DB = SALIDA / "talento_andino.db"
CATEGORIAS = ["VACACIONES", "CERTIFICADO_LABORAL", "INCAPACIDAD", "ACTUALIZACION_DATOS", "OTRO"]
UMBRAL_CONFIANZA = 0.7
ANIO_FESTIVOS = 2026


def cargar_env():
    env = RAIZ / ".env"
    if not env.exists():
        return
    for linea in env.read_text(encoding="utf-8").splitlines():
        if "=" in linea and not linea.startswith("#"):
            k, v = linea.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


cargar_env()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
