import math
from urllib.parse import quote

ZONAS = {
    "La Boca": (-34.6347, -58.3648),
    "Capital Federal": (-34.6037, -58.3816),
    "San Cristóbal": (-34.6220, -58.4008),
    "San Cristobal": (-34.6220, -58.4008),
    "Almagro": (-34.6098, -58.4219),
    "Villa Santa Rit": (-34.6200, -58.4900),
    "Villa Santa Rita": (-34.6200, -58.4900),
    "Villa Crespo": (-34.5990, -58.4370),
    "Parque Chas": (-34.5878, -58.4846),
    "Belgrano": (-34.5621, -58.4563),
    "Flores": (-34.6283, -58.4630),
    "Velez Sarsfield": (-34.6328, -58.4928),
    "Vélez Sarsfield": (-34.6328, -58.4928),
    "Caballito": (-34.6186, -58.4424),
    "Devoto": (-34.6026, -58.5107),
    "Ciudad Autónoma": (-34.6037, -58.3816),
    "Ciudad Autonoma": (-34.6037, -58.3816),
    "Palermo": (-34.5733, -58.4300),
}

def haversine_km(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    r = 6371.0

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    y = 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))
    return r * y

def coords_de_parada(parada):
    loc = parada.get("localidad")
    if loc in ZONAS:
        return ZONAS[loc], True
    return None, False

def generar_link_individual(texto):
    return f"https://www.google.com/maps/search/?api=1&query={quote(texto)}"

def optimizar_ruta_basica(origen_coords, paradas):
    encontradas = []
    no_encontradas = []

    for p in paradas:
        item = dict(p)
        coords, ok = coords_de_parada(item)
        item["coords"] = coords
        item["encontrada"] = ok
        if ok:
            encontradas.append(item)
        else:
            no_encontradas.append(item)

    ruta = []
    actual = origen_coords
    distancia_total = 0.0

    while encontradas:
        siguiente = min(encontradas, key=lambda x: haversine_km(actual, x["coords"]))
        tramo = haversine_km(actual, siguiente["coords"])
        distancia_total += tramo

        siguiente["distancia_desde_anterior_km"] = round(tramo, 2)
        siguiente["link_individual"] = generar_link_individual(siguiente["direccion_mapa"])
        ruta.append(siguiente)

        actual = siguiente["coords"]
        encontradas.remove(siguiente)

    for item in no_encontradas:
        item["distancia_desde_anterior_km"] = "-"
        item["link_individual"] = generar_link_individual(item["direccion_mapa"])
        ruta.append(item)

    for i, p in enumerate(ruta, start=1):
        p["orden"] = i

    tiempo_total_min = round((distancia_total / 25) * 60) if distancia_total > 0 else 0
    return ruta, round(distancia_total, 2), tiempo_total_min

def generar_link_maps(origen_texto, ruta):
    if not ruta:
        return None

    validas = [r for r in ruta if r.get("encontrada")]
    if not validas:
        return None

    destino = validas[-1]["direccion_mapa"]
    intermedios = [r["direccion_mapa"] for r in validas[:-1]]

    url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={quote(origen_texto)}"
        f"&destination={quote(destino)}"
        f"&travelmode=driving"
    )

    if intermedios:
        url += f"&waypoints={quote('|'.join(intermedios))}"

    return url
