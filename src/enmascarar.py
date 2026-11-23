"""Enmascara datos personales ANTES de enviar texto a un modelo de IA."""
import re

_REGLAS = [
    (re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+"), "[CORREO]"),
    (re.compile(r"\b3\d{9}\b"), "[CELULAR]"),      # celular colombiano
    (re.compile(r"\b\d{6,10}\b"), "[DOCUMENTO]"),  # cédula / documento
]


def enmascarar(texto):
    for patron, etiqueta in _REGLAS:
        texto = patron.sub(etiqueta, texto)
    return texto
