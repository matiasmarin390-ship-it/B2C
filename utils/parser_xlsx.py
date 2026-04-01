import pandas as pd
import re


def limpiar(texto):
    if texto is None:
        return ""
    texto = str(texto).replace("\xa0", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def parsear_coordenadas(valor):
    """
    Espera formato: '-34.6926 -58.6293'
    """
    txt = limpiar(valor)
    if not txt:
        return None

    m = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*$", txt)
    if not m:
        return None

    lat = float(m.group(1))
    lon = float(m.group(2))
    return lat, lon


def extraer_eventos_xlsx(file_storage):
    df = pd.read_excel(file_storage, sheet_name="Resultados")

    columnas = {c.lower(): c for c in df.columns}

    col_fecha = columnas.get("fecha")
    col_evento = columnas.get("evento")
    col_coord = columnas.get("coordenadas")
    col_ubicacion = columnas.get("ubicación") or columnas.get("ubicacion")
    col_punto = columnas.get("punto cercano")

    if not col_evento or not col_coord:
        raise ValueError("La solapa Resultados no tiene las columnas Evento y/o Coordenadas.")

    eventos = []

    for _, row in df.iterrows():
        evento = limpiar(row.get(col_evento))
        if not evento:
            continue

        if evento.lower() == "posición" or evento.lower() == "posicion":
            continue

        coords = parsear_coordenadas(row.get(col_coord))
        if not coords:
            continue

        eventos.append({
            "fecha": limpiar(row.get(col_fecha)) if col_fecha else "",
            "evento": evento,
            "coordenadas": coords,
            "ubicacion": limpiar(row.get(col_ubicacion)) if col_ubicacion else "",
            "punto_cercano": limpiar(row.get(col_punto)) if col_punto else "",
        })

    return eventos
