def normalizar_texto(txt):
    if not txt:
        return ""

    txt = str(txt).lower()
    txt = txt.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    txt = txt.replace(".", " ").replace(",", " ").replace(";", " ").replace(":", " ")
    txt = " ".join(txt.split())
    return txt.strip()


def link_google_maps_coords(lat, lon):
    return f"https://www.google.com/maps?q={lat},{lon}"


def palabras_relevantes_direccion(direccion):
    texto = normalizar_texto(direccion)

    sacar = {
        "calle", "avenida", "av", "pasaje", "pje", "sn", "s/n"
    }

    tokens = []
    for token in texto.split():
        if token in sacar:
            continue
        tokens.append(token)

    return tokens


def score_match(parada, evento):
    direccion = normalizar_texto(parada.get("direccion", ""))
    localidad = normalizar_texto(parada.get("localidad", ""))

    texto_evento = " ".join([
        normalizar_texto(evento.get("ubicacion", "")),
        normalizar_texto(evento.get("punto_cercano", "")),
        normalizar_texto(evento.get("evento", "")),
    ]).strip()

    if not texto_evento:
        return 0

    score = 0

    for palabra in palabras_relevantes_direccion(direccion):
        if palabra and palabra in texto_evento:
            score += 2

    if localidad and localidad in texto_evento:
        score += 3

    # bonus si aparece el número exacto
    for token in direccion.split():
        if token.isdigit() and token in texto_evento:
            score += 3

    return score


def buscar_evento_mas_relevante(parada, eventos):
    mejor = None
    mejor_score = 0

    for evento in eventos:
        score = score_match(parada, evento)
        if score > mejor_score:
            mejor_score = score
            mejor = evento

    return mejor, mejor_score


def procesar_cruce_completo(hoja_ruta_nro, paradas, eventos):
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
