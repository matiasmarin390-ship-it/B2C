import math
import re
from urllib.parse import quote


def normalizar(txt):
    if not txt:
        return ""
    txt = str(txt).lower()
    txt = txt.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    txt = txt.replace(".", " ").replace(",", " ").replace(";", " ").replace(":", " ").replace("-", " ")
    txt = " ".join(txt.split())
    return txt.strip()


def link_google_maps_coords(lat, lon):
    return f"https://www.google.com/maps?q={lat},{lon}"


def link_google_maps_direccion(direccion, localidad):
    consulta = f"{direccion}, {localidad}, Buenos Aires, Argentina"
    return f"https://www.google.com/maps/search/?api=1&query={quote(consulta)}"


def extraer_numero(txt):
    m = re.search(r"\d+", txt or "")
    return m.group(0) if m else ""


def score(parada, evento):
    dir_p = normalizar(parada["direccion"])
    loc_p = normalizar(parada["localidad"])

    texto = normalizar(
        (evento.get("ubicacion", "") or "") + " " +
        (evento.get("punto_cercano", "") or "") + " " +
        (evento.get("direccion_inferida", "") or "")
    )

    s = 0

    numero = extraer_numero(dir_p)
    if numero and numero in texto:
        s += 4

    for palabra in dir_p.split():
        if palabra and palabra in texto:
            s += 2

    if loc_p and loc_p in texto:
        s += 3

    return s


def clasificar(score_val):
    if score_val >= 8:
        return "Cumplido exacto"
    elif score_val >= 4:
        return "Pasó cerca"
    else:
        return "No pasó"


def haversine(a, b):
    r = 6371000
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    x = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(x), math.sqrt(1 - x))


def procesar_cruce_completo(hoja, paradas, eventos, track_points):
    exacto = 0
    cerca = 0
    no = 0

    eventos_procesados = []
    for e in eventos:
        item = dict(e)
        coords = item.get("coordenadas")

        if coords and len(coords) == 2:
            item["link_mapa"] = link_google_maps_coords(coords[0], coords[1])
        else:
            item["link_mapa"] = ""

        eventos_procesados.append(item)

    for p in paradas:
        mejor = None
        mejor_score = -1

        for e in eventos_procesados:
            sc = score(p, e)
            if sc > mejor_score:
                mejor_score = sc
                mejor = e

        estado = clasificar(mejor_score)

        if estado == "Cumplido exacto":
            exacto += 1
        elif estado == "Pasó cerca":
            cerca += 1
        else:
            no += 1

        p["evento_mas_cercano"] = mejor
        p["score"] = max(mejor_score, 0)
        p["estado"] = estado
        p["orden"] = mejor["row_index"] if mejor and "row_index" in mejor else 999999
        p["link_direccion"] = link_google_maps_direccion(p["direccion"], p["localidad"])

    paradas.sort(key=lambda x: x["orden"])

    dist = 0
    for i in range(1, len(track_points)):
        if track_points[i - 1].get("coordenadas") and track_points[i].get("coordenadas"):
            dist += haversine(
                track_points[i - 1]["coordenadas"],
                track_points[i]["coordenadas"]
            )

    regreso = None
    regreso_ok = False
    if len(track_points) >= 2 and track_points[0].get("coordenadas") and track_points[-1].get("coordenadas"):
        inicio = track_points[0]["coordenadas"]
        fin = track_points[-1]["coordenadas"]
        regreso = haversine(inicio, fin)
        regreso_ok = regreso < 150

    resumen = {
        "hoja_ruta_nro": hoja,
        "total_paradas": len(paradas),
        "total_eventos": len(eventos_procesados),
        "cumplidos_exactos": exacto,
        "paso_cerca": cerca,
        "no_paso": no,
        "distancia_total_km": round(dist / 1000, 2),
        "regreso_al_inicio": regreso_ok,
        "distancia_inicio_fin_m": round(regreso, 1) if regreso is not None else None
    }

    return resumen, paradas, eventos_procesados
