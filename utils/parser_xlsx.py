import pandas as pd
import re
import math
import time
from functools import lru_cache
from geopy.geocoders import Nominatim


geolocator = Nominatim(user_agent="auditoria_ruta_historico")


def limpiar(texto):
    if texto is None or (isinstance(texto, float) and math.isnan(texto)):
        return ""
    texto = str(texto).replace("\xa0", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def parsear_coordenadas(valor):
    txt = limpiar(valor)
    if not txt:
        return None

    match = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*$", txt)
    if not match:
        return None

    lat = float(match.group(1))
    lon = float(match.group(2))
    return lat, lon


def distancia_cuadrada(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


@lru_cache(maxsize=2000)
def reverse_geocode(lat, lon):
    """
    Convierte coordenadas a dirección textual usando Nominatim.
    Tiene cache para no repetir búsquedas.
    """
    try:
        time.sleep(1)  # para no saturar Nominatim
        location = geolocator.reverse(
            (lat, lon),
            exactly_one=True,
            language="es",
            timeout=15
        )
        if not location:
            return ""
        return str(location.address)
    except Exception:
        return ""


def extraer_datos_xlsx(file_storage):
    xls = pd.ExcelFile(file_storage)

    if "Resultados" not in xls.sheet_names:
        raise ValueError("El Excel histórico no contiene la solapa Resultados.")

    df_res = pd.read_excel(xls, sheet_name="Resultados")
    columnas_res = {str(c).strip().lower(): c for c in df_res.columns}

    col_fecha = columnas_res.get("fecha")
    col_evento = columnas_res.get("evento")
    col_coord = columnas_res.get("coordenadas")
    col_ubicacion = columnas_res.get("ubicación") or columnas_res.get("ubicacion")
    col_punto = columnas_res.get("punto cercano")

    if not col_evento or not col_coord:
        raise ValueError("La solapa Resultados no tiene las columnas Evento y/o Coordenadas.")

    detenciones = []
    if "Detenciones" in xls.sheet_names:
        df_det = pd.read_excel(xls, sheet_name="Detenciones")
        columnas_det = {str(c).strip().lower(): c for c in df_det.columns}

        col_det_coord = columnas_det.get("coordenadas")
        col_det_dir = columnas_det.get("dirección") or columnas_det.get("direccion")

        if col_det_coord and col_det_dir:
            for _, row in df_det.iterrows():
                coords = parsear_coordenadas(row.get(col_det_coord))
                direccion = limpiar(row.get(col_det_dir))
                if coords and direccion:
                    detenciones.append({
                        "coordenadas": coords,
                        "direccion": direccion
                    })

    eventos = []
    track_points = []

    for idx, row in df_res.iterrows():
        evento = limpiar(row.get(col_evento))
        coords = parsear_coordenadas(row.get(col_coord))
        fecha = limpiar(row.get(col_fecha)) if col_fecha else ""

        if not coords:
            continue

        lat, lon = coords

        base = {
            "row_index": idx,
            "fecha": fecha,
            "evento": evento,
            "coordenadas": coords,
            "ubicacion": limpiar(row.get(col_ubicacion)) if col_ubicacion else "",
            "punto_cercano": limpiar(row.get(col_punto)) if col_punto else "",
            "direccion_inferida": "",
        }

        # 1) Si existe Detenciones, usar la dirección más cercana
        if detenciones:
            mejor = min(detenciones, key=lambda d: distancia_cuadrada(coords, d["coordenadas"]))
            base["direccion_inferida"] = mejor["direccion"]

        # 2) Si no encontró nada útil, usar reverse geocoding
        if not base["direccion_inferida"]:
            base["direccion_inferida"] = reverse_geocode(lat, lon)

        track_points.append(dict(base))

        if evento and evento.lower() not in ("posición", "posicion"):
            eventos.append(dict(base))

    return {
        "eventos": eventos,
        "track_points": track_points
    }
