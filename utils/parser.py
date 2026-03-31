import pdfplumber
import re

PALABRAS_DIRECCION = [
    "calle", "av", "av.", "avenida", "pasaje", "pje", "pje.",
    "tronador", "galicia", "uriburu", "monroe", "freire",
    "lavallol", "querandies", "querandíes", "nazarre", "cordoba",
    "córdoba", "riestra", "olavarría", "olavarria", "catamarca"
]

LOCALIDADES_CONOCIDAS = [
    "la boca",
    "capital federal",
    "san cristóbal",
    "san cristobal",
    "almagro",
    "villa santa rit",
    "villa santa rita",
    "villa crespo",
    "parque chas",
    "belgrano",
    "flores",
    "velez sarsfield",
    "vélez sarsfield",
    "caballito",
    "devoto",
    "ciudad autónoma",
    "ciudad autonoma",
    "palermo"
]

def limpiar_texto(texto: str) -> str:
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

def parece_direccion(linea: str) -> bool:
    l = linea.lower()
    tiene_palabra = any(p in l for p in PALABRAS_DIRECCION)
    tiene_numero = bool(re.search(r"\b\d{2,5}\b", l)) or " sn " in f" {l} "
    return tiene_palabra and tiene_numero

def extraer_localidad(linea: str) -> str:
    l = linea.lower()
    for loc in LOCALIDADES_CONOCIDAS:
        if loc in l:
            return loc.title()
    return "CABA"

def normalizar_direccion(direccion: str, localidad: str) -> str:
    direccion = limpiar_texto(direccion)

    reemplazos = {
        " av. ": " Avenida ",
        " av ": " Avenida ",
        " pje ": " Pasaje ",
        " pje. ": " Pasaje ",
        " calle ": " Calle ",
    }

    texto = f" {direccion} "
    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    texto = limpiar_texto(texto)
    return f"{texto}, {localidad}, Buenos Aires, Argentina"

def extraer_direcciones(file_storage) -> list[str]:
    direcciones = []
    vistos = set()

    with pdfplumber.open(file_storage) as pdf:
        for page in pdf.pages:
            texto = page.extract_text() or ""
            if not texto:
                continue

            lineas = texto.split("\n")

            for linea in lineas:
                linea_limpia = limpiar_texto(linea)

                if not linea_limpia:
                    continue

                if not parece_direccion(linea_limpia):
                    continue

                if "impresión de hoja de ruta" in linea_limpia.lower():
                    continue

                if "total documentos" in linea_limpia.lower():
                    continue

                if "controlador" in linea_limpia.lower():
                    continue

                localidad = extraer_localidad(linea_limpia)

                # intenta extraer solo el fragmento de dirección
                # desde la primera palabra de tipo calle/av/pasaje hasta antes de la localidad
                patron = re.compile(
                    r"(?i)\b(calle|av\.?|avenida|pasaje|pje\.?)\b.*?(?=(la boca|capital federal|san cristóbal|san cristobal|almagro|villa santa rit|villa santa rita|villa crespo|parque chas|belgrano|flores|velez sarsfield|vélez sarsfield|caballito|devoto|ciudad autónoma|ciudad autonoma|palermo)\b|$)"
                )
                m = patron.search(linea_limpia)

                if m:
                    direccion_raw = limpiar_texto(m.group(0))
                else:
                    # fallback: usar toda la línea
                    direccion_raw = linea_limpia

                direccion_final = normalizar_direccion(direccion_raw, localidad)

                key = direccion_final.lower()
                if key not in vistos:
                    vistos.add(key)
                    direcciones.append(direccion_final)

    return direcciones
