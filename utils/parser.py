import pdfplumber
import re

LOCALIDADES = [
    "LA BOCA",
    "CAPITAL FEDERAL",
    "SAN CRISTÓBAL",
    "SAN CRISTOBAL",
    "ALMAGRO",
    "VILLA SANTA RIT",
    "VILLA SANTA RITA",
    "VILLA CRESPO",
    "PARQUE CHAS",
    "BELGRANO",
    "FLORES",
    "VELEZ SARSFIELD",
    "VÉLEZ SARSFIELD",
    "CABALLITO",
    "DEVOTO",
    "CIUDAD AUTÓNOMA",
    "CIUDAD AUTONOMA",
    "PALERMO",
]

INICIOS_DOMICILIO = [
    "CALLE", "AVENIDA", "AV.", "AV", "PASAJE", "PJE", "PJE.", "TRONADOR",
    "GALICIA", "URIBURU", "MONROE", "FREIRE", "LAVALLOL", "ALEJO",
    "QUERANDIES", "QUERANDÍES", "NAZARRE", "CORDOBA", "CÓRDOBA",
    "RIESTRA", "OLAVARRIA", "OLAVARRÍA", "CATAMARCA", "ELPIDIO",
    "LUIS", "SANTA", "AV.RIESTRA"
]

BLOQUEADOS = [
    "IMPRESIÓN DE HOJA DE RUTA",
    "TOTAL DOCUMENTOS",
    "M3 TOTAL VIAJE",
    "CHOFER",
    "FIRMA:",
    "ACLARACIÓN:",
    "ARRIBO",
    "SALIDA",
    "CONTROLADOR",
    "OBSERVACIONES",
    "IMPORTANTE",
    "ESTADO VEHÍCULO",
    "RECEPCIONÓ",
    "CUSTODIA",
    "FECHA:",
    "HOJA:",
]

def limpiar(texto: str) -> str:
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

def extraer_nro_hoja(texto: str):
    m = re.search(r"Impresi[oó]n de Hoja de Ruta Nro\.\s*:\s*(\d+)", texto, re.IGNORECASE)
    return m.group(1) if m else None

def es_linea_util(linea: str) -> bool:
    if not linea:
        return False
    up = linea.upper()
    for b in BLOQUEADOS:
        if b in up:
            return False
    return True

def detectar_localidad(linea: str):
    up = linea.upper()
    for loc in sorted(LOCALIDADES, key=len, reverse=True):
        if loc in up:
            return loc.title()
    return None

def detectar_inicio_domicilio(linea: str):
    up = linea.upper()
    pos_min = None
    valor = None
    for inicio in INICIOS_DOMICILIO:
        pos = up.find(inicio)
        if pos != -1 and (pos_min is None or pos < pos_min):
            pos_min = pos
            valor = inicio
    return pos_min, valor

def extraer_paradas_y_hoja(file_storage):
    nro_hoja = None
    paradas = []
    vistos = set()

    with pdfplumber.open(file_storage) as pdf:
        paginas_texto = []
        for page in pdf.pages:
            txt = page.extract_text() or ""
            if txt:
                paginas_texto.append(txt)

        texto_total = "\n".join(paginas_texto)
        nro_hoja = extraer_nro_hoja(texto_total)

        for linea in texto_total.split("\n"):
            linea = limpiar(linea)
            if not es_linea_util(linea):
                continue

            localidad = detectar_localidad(linea)
            if not localidad:
                continue

            idx_loc = linea.upper().find(localidad.upper())
            if idx_loc == -1:
                continue

            izquierda = limpiar(linea[:idx_loc])

            idx_dom, _ = detectar_inicio_domicilio(izquierda)
            if idx_dom is None:
                continue

            cliente = limpiar(izquierda[:idx_dom]) or "Cliente"
            domicilio = limpiar(izquierda[idx_dom:]) or None

            if not domicilio:
                continue

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
