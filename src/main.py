"""Punto de entrada: python src/main.py"""
import sys

import consultas
import db
from festivos import obtener_festivos
from reporte import procesar


def main():
    print("1) Datos limpios:")
    for linea in db.cargar():
        print("  -", linea)
    consultas.ejecutar()
    print("2) Festivos...")
    festivos = obtener_festivos()
    print("3) Clasificando y generando reporte...")
    filas, metricas = procesar(festivos)
    print(metricas)
    print(f"Revisión humana: {sum(f['requiere_revision'] == 'SI' for f in filas)} de {len(filas)}")
    print("Reporte: output/reporte_solicitudes.csv")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)  # el código de salida lo lee Power Automate
