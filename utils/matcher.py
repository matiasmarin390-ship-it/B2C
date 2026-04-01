import math
from urllib.parse import quote

from utils.geocode_osm import geocodificar_direccion


def haversine_metros(a, b):
    lat1, lon1 = a
    lat2, lon2 = b

    r = 6371000.0

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    y = 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))
    return r * y


def link_google_maps_coords(lat, lon):
    return f"https://www.google.com/maps?q={lat},{lon}"


def buscar_evento_mas_cercano(destino_coords, eventos):
    mejor = None
    mejor_dist = None

    for ev in eventos:
        dist = haversine_metros(destino_coords, ev["coordenadas"])
        if mejor_dist is None or dist < mejor_dist:
            mejor_dist = dist
            mejor = ev

    return mejor, mejor_dist


def procesar_cruce_completo(hoja_ruta_nro, paradas, eventos, margen_metros=50):
    eventos_procesados = []
    for ev in eventos:
        lat, lon = ev["coordenadas"]
        item = dict(ev)
        item["link_mapa"] = link_google_maps_coords(lat, lon)
        eventos_procesados.append(item)

    paradas_procesadas = []
    cumplidos = 0
    no_cumplidos = 0
    sin_coord = 0

    for idx, parada in enumerate(paradas, start=1):
        item = dict(parada)
        item["orden"] = idx

        geo = geocodificar_direccion(item["direccion"], item["localidad"])
        if not geo:
            item["destino_coords"] = None
            item["destino_link"] = None
            item["estado"] = "Sin coordenadas de destino"
            item["distancia_evento_mas_cercano_m"] = None
            item["evento_mas_cercano"] = None
            item["consulta_usada"] = None
            sin_coord += 1
            paradas_procesadas.append(item)
            continue

        item["destino_coords"] = (geo["lat"], geo["lon"])
        item["destino_link"] = link_google_maps_coords(geo["lat"], geo["lon"])
        item["consulta_usada"] = geo["consulta_usada"]

        evento_cercano, distancia_m = buscar_evento_mas_cercano(item["destino_coords"], eventos_procesados)

        item["distancia_evento_mas_cercano_m"] = round(distancia_m, 1) if distancia_m is not None else None
        item["evento_mas_cercano"] = evento_cercano

        if evento_cercano and distancia_m is not None and distancia_m <= margen_metros:
            item["estado"] = "Cumplido"
            cumplidos += 1
        else:
            item["estado"] = "No cumplido"
            no_cumplidos += 1

        paradas_procesadas.append(item)

    resumen = {
        "hoja_ruta_nro": hoja_ruta_nro,
        "total_paradas": len(paradas_procesadas),
        "total_eventos": len(eventos_procesados),
        "cumplidos": cumplidos,
        "no_cumplidos": no_cumplidos,
        "sin_coord": sin_coord,
        "margen_metros": margen_metros
    }

    return resumen, paradas_procesadas, eventos_procesados
