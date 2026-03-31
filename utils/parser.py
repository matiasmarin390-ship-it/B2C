import pdfplumber
import re

LOCALIDADES = [
    "La Boca",
    "CAPITAL FEDERAL",
    "Capital Federal",
    "San Cristóbal",
    "San Cristobal",
    "Almagro",
    "Villa Santa Rit",
    "Villa Santa Rita",
    "Villa Crespo",
    "Parque Chas",
    "Belgrano",
    "Flores",
    "Velez Sarsfield",
    "Vélez Sarsfield",
    "Caballito",
    "Devoto",
    "Ciudad Autónoma",
    "Ciudad Autonoma",
    "Palermo",
]

def limpiar(texto: str) -> str:
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

def extraer_nro_hoja(texto: str):
    m = re.search(r"Impresi[oó]n de Hoja de Ruta Nro\.\s*:\s*(\d+)", texto, re.IGNORECASE)
    if m:
        return m.group(1)
    return None

def detectar_localidad_en_linea(linea: str):
    for loc in sorted(LOCALIDADES, key=len, reverse=True):
        if loc.lower() in linea.lower():
            return loc
    return None

def extraer_domicilio_desde_linea(linea: str, localidad: str):
    """
    Toma el texto que está entre el domicilio y la localidad.
    """
    if not localidad:
        return None

    idx_loc = linea.lower().find(localidad.lower())
    if idx_loc == -1:
        return None

    antes_localidad = linea[:idx_loc].strip()

    # Buscar el inicio del domicilio por patrones comunes
    patrones = [
        r"\bCalle\b",
        r"\bAvenida\b",
        r"\bAv\.\b",
        r"\bAv\b",
        r"\bPasaje\b",
        r"\bPJE\b",
        r"\bPje\b",
        r"\bTronador\b",
        r"\bGalicia\b",
        r"\bUriburu\b",
        r"\bMonroe\b",
        r"\bFreire\b",
        r"\bLavallol\b",
        r"\bALEJO\b",
        r"\bQuerandies\b",
        r"\bQuerandíes\b",
        r"\bNazarre\b",
        r"\bCordoba\b",
        r"\bC[oó]rdoba\b",
        r"\bRiestra\b",
        r"\bOlavarr[ií]a\b",
        r"\bCatamarca\b",
        r"\bElpidio\b",
        r"\bLuis\b",
        r"\bSanta\b",
    ]

    inicio = None
    for patron in patrones:
        m = re.search(patron, antes_localidad, re.IGNORECASE)
        if m:
            pos = m.start()
            if inicio is None or pos < inicio:
                inicio = pos

    if inicio is None:
        return None

    domicilio = antes_localidad[inicio:].strip()
    return limpiar(domicilio)

def extraer_cliente_desde_linea(linea: str, domicilio: str):
    idx = linea.lower().find(domicilio.lower())
    if idx > 0:
        cliente = linea[:idx].strip()
        return limpiar(cliente)
    return "Cliente"

def es_linea_util(linea: str):
    if not linea:
        return False

    bloqueados = [
        "Impresión de Hoja de Ruta",
        "Total Documentos",
        "m3 Total Viaje",
        "CHOFER",
        "Firma:",
        "Aclaración:",
        "ARRIBO",
        "SALIDA",
        "CONTROLADOR",
        "OBSERVACIONES",
        "IMPORTANTE",
        "Estado Vehículo",
        "Recepcionó:",
        "Custodia:",
    ]

    for b in bloqueados:
        if b.lower() in linea.lower():
            return False

    return True

def extraer_paradas_y_hoja(file_storage):
    nro_hoja = None
    paradas = []
    vistos = set()

    with pdfplumber.open(file_storage) as pdf:
        texto_total = []

        for page in pdf.pages:
            texto = page.extract_text() or ""
            if texto:
                texto_total.append(texto)

        texto_total = "\n".join(texto_total)
        nro_hoja = extraer_nro_hoja(texto_total)

        lineas = texto_total.split("\n")

        for linea in lineas:
            linea = limpiar(linea)

            if not es_linea_util(linea):
                continue

            localidad = detectar_localidad_en_linea(linea)
            if not localidad:
                continue

            domicilio = extraer_domicilio_desde_linea(linea, localidad)
            if not domicilio:
                continue

            cliente = extraer_cliente_desde_linea(linea, domicilio)

            direccion_mapa = f"{domicilio}, {localidad}, Buenos Aires, Argentina"
            key = direccion_mapa.lower()

            if key in vistos:
                continue
            vistos.add(key)

            paradas.append({
                "cliente": cliente,
                "direccion": domicilio,
                "localidad": localidad,
                "direccion_mapa": direccion_mapa
            })

    return nro_hoja, paradas
