"""Misión 3: clasificación con Groq (API compatible con OpenAI) (JSON validado). Si falla, cae a reglas."""
import json
import urllib.request
from datetime import date

from clasif_reglas import clasificar_reglas
from config import CATEGORIAS, GROQ_API_KEY, GROQ_MODEL
from enmascarar import enmascarar

URL = "https://api.groq.com/openai/v1/chat/completions"
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


def _llamar_groq(texto, recepcion):
    cuerpo = {"model": GROQ_MODEL, "temperature": 0, "response_format": {"type": "json_object"},
              "messages": [{"role": "user", "content": PROMPT.format(cats=CATEGORIAS, rec=recepcion, texto=texto)}]}
    req = urllib.request.Request(URL, json.dumps(cuerpo).encode(), {
        "Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}",
        "User-Agent": "automatizador-rrhh/1.0"})  # Groq (Cloudflare) rechaza el UA por defecto de urllib
    with urllib.request.urlopen(req, timeout=30) as r:
        salida = json.load(r)
    return json.loads(salida["choices"][0]["message"]["content"])


def clasificar(texto, recepcion):
    if GROQ_API_KEY:
        try:
            res = validar(_llamar_groq(enmascarar(texto), recepcion))  # solo texto enmascarado sale del equipo
            return {**res, "fuente": "groq"}
        except Exception as e:
            print(f"[ia] falló ({e}); uso reglas")
    return clasificar_reglas(texto, recepcion)
