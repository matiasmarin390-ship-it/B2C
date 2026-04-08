import pandas as pd
import re


def parse_coords(txt):
    if not isinstance(txt, str):
        return None

    m = re.match(r"(-?\d+\.\d+)\s+(-?\d+\.\d+)", txt)
    if not m:
        return None

    return float(m.group(1)), float(m.group(2))


def extraer_datos_xlsx(file):
    xls = pd.ExcelFile(file)

    df = pd.read_excel(xls, "Resultados")

    eventos = []
    track = []

    for i, row in df.iterrows():
        coords = parse_coords(row.get("Coordenadas"))
        if not coords:
            continue

        base = {
            "row_index": i,
            "evento": str(row.get("Evento", "")),
            "fecha": str(row.get("Fecha", "")),
            "coordenadas": coords,
            "ubicacion": str(row.get("Ubicación", "")),
            "punto_cercano": str(row.get("Punto cercano", "")),
            "direccion_inferida": ""
        }

        track.append(base)

        if base["evento"].lower() != "posición":
            eventos.append(base)

    return {
        "eventos": eventos,
        "track_points": track
    }
