import math


def normalizar_texto(txt):
    if not txt:
        return ""
    txt = str(txt).lower()
    txt = txt.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    txt = txt.replace(".", "").replace(",", "")
    return txt.strip()


def link_google_maps_coords(lat, lon):
    return f"https://www.google.com/maps?q={lat},{lon}"


def score_match(parada, evento):
    direccion = normalizar_texto(parada["direccion"])
    localidad = normalizar_texto(parada["localidad"])

    texto_evento = normalizar_texto(evento.get("ubicacion", "")) + " " + normalizar_texto(evento.get("punto_cercano", ""))

    score = 0

    # coincidencia por calle
    for palabra in direccion.split():
        if palabra in texto_evento:
            score += 2

    # coincidencia por localidad
    if localidad and localidad in texto_evento:
        score += 3

    return score


def buscar_evento_mas_relevante(parada, eventos):
    mejor = None
    mejor_score = 0

    for ev in eventos:
        s = score_match(parada, ev)
        if s > mejor_score:
            mejor_score = s
            mejor = ev

    return mejor, mejor_score


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

    for idx, parada in enumerate(paradas, start=1):
        item = dict(parada)
        item["orden"] = idx

        evento, score = buscar_evento_mas_relevante(item, eventos_procesados)

        item["evento_mas_cercano"] = evento
        item["score"] = score

        if evento and score >= 3:
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
    }

    return resumen, paradas_procesadas, eventos_procesados
