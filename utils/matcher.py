import math
import re


def normalizar(txt):
    if not txt:
        return ""
    txt = txt.lower()
    txt = txt.replace(".", " ")
    return txt


def extraer_numero(txt):
    m = re.search(r"\d+", txt or "")
    return m.group(0) if m else ""


def score(parada, evento):
    dir_p = normalizar(parada["direccion"])
    loc_p = normalizar(parada["localidad"])

    texto = normalizar(
        evento["ubicacion"] +
        evento["punto_cercano"]
    )

    s = 0

    if extraer_numero(dir_p) in texto:
        s += 4

    for palabra in dir_p.split():
        if palabra in texto:
            s += 2

    if loc_p in texto:
        s += 3

    return s


def clasificar(score):
    if score >= 8:
        return "Cumplido exacto"
    elif score >= 4:
        return "Pasó cerca"
    else:
        return "No pasó"


def haversine(a, b):
    R = 6371000
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    x = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(x), math.sqrt(1-x))


def procesar_cruce_completo(hoja, paradas, eventos, track_points):

    exacto = 0
    cerca = 0
    no = 0

    for p in paradas:
        mejor = None
        mejor_score = -1

        for e in eventos:
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
        p["score"] = mejor_score
        p["estado"] = estado
        p["orden"] = mejor["row_index"] if mejor else 999999

    paradas.sort(key=lambda x: x["orden"])

    dist = 0
    for i in range(1, len(track_points)):
        dist += haversine(
            track_points[i-1]["coordenadas"],
            track_points[i]["coordenadas"]
        )

    inicio = track_points[0]["coordenadas"]
    fin = track_points[-1]["coordenadas"]
    regreso = haversine(inicio, fin)

    return {
        "hoja_ruta_nro": hoja,
        "total_paradas": len(paradas),
        "total_eventos": len(eventos),
        "cumplidos_exactos": exacto,
        "paso_cerca": cerca,
        "no_paso": no,
        "distancia_total_km": round(dist/1000, 2),
        "regreso_al_inicio": regreso < 150,
        "distancia_inicio_fin_m": round(regreso, 1)
    }, paradas, eventos
