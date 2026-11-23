"""Misión 3: clasificación con Gemini (JSON validado). Si falla, cae a reglas."""
import json
import urllib.request
from datetime import date

from clasif_reglas import clasificar_reglas
from config import CATEGORIAS, GEMINI_API_KEY, GEMINI_MODEL
from enmascarar import enmascarar

URL = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
PROMPT = """Clasifica la solicitud de un empleado. Responde SOLO un JSON con las claves:
categoria (una de {cats}), confianza (número 0 a 1), fecha_inicio y fecha_fin (AAAA-MM-DD o null).
Si no hay fechas exactas usa null. Fecha de recepción: {rec}.
Solicitud: {texto}"""


def validar(obj):
    """Lanza ValueError si el JSON del modelo no cumple el contrato."""
    if obj.get("categoria") not in CATEGORIAS:
        raise ValueError(f"categoría inválida: {obj.get('categoria')}")
    conf = obj.get("confianza")
    if not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
        raise ValueError(f"confianza inválida: {conf}")
    for k in ("fecha_inicio", "fecha_fin"):
        if obj.get(k) is not None:
            date.fromisoformat(obj[k])
    return {k: obj.get(k) for k in ("categoria", "confianza", "fecha_inicio", "fecha_fin")}


def _llamar_gemini(texto, recepcion):
    cuerpo = {"contents": [{"parts": [{"text": PROMPT.format(cats=CATEGORIAS, rec=recepcion, texto=texto)}]}],
              "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
    req = urllib.request.Request(URL.format(m=GEMINI_MODEL), json.dumps(cuerpo).encode(),
                                 {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        salida = json.load(r)
    return json.loads(salida["candidates"][0]["content"]["parts"][0]["text"])


def clasificar(texto, recepcion):
    if GEMINI_API_KEY:
        try:
            res = validar(_llamar_gemini(enmascarar(texto), recepcion))  # solo texto enmascarado sale del equipo
            return {**res, "fuente": "gemini"}
        except Exception as e:
            print(f"[ia] falló ({e}); uso reglas")
    return clasificar_reglas(texto, recepcion)
