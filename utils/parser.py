import pdfplumber
import re

LOCALIDADES = [
    "La Boca",
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

DIRECCION_KEYS = [
    "Calle", "Avenida", "Av.", "Av", "Pasaje", "PJE", "Pje", "Tronador",
    "Galicia", "Uriburu", "Monroe", "Freire", "Lavallol", "Querandies",
    "Querandíes", "Nazarre", "Cordoba", "Córdoba", "Riestra", "Olavarría",
    "Olavarria", "Catamarca"
]

def limpiar(s: str) -> str:
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def detectar_localidad(linea: str):
    for loc in LOCALIDADES:
        if loc.lower() in linea.lower():
            return loc
    return None

def contiene_direccion(linea: str):
    tiene_key = any(k.lower() in linea.lower() for k in DIRECCION_KEYS)
    tiene_num = bool(re.search(r"\b\d{2,5}\b", linea)) or " SN " in f" {linea.upper()} "
    return tiene_key and tiene_num

def extraer_direccion(linea: str, localidad: str):
    if localidad:
        idx = linea.lower().find(localidad.lower())
        if idx > 0:
            base = linea[:idx].strip()
        else:
            base = linea
    else:
        base = linea

    # busca desde la primera palabra de dirección
    patron = re.compile(
        r"(Calle|Avenida|Av\.|Av |Pasaje|PJE|Pje|Tronador|Galicia|Uriburu|Monroe|Freire|Lavallol|Querandies|Querandíes|Nazarre|Cordoba|Córdoba|Riestra|Olavarría|Olavarria|Catamarca).*$",
        re.IGNORECASE
    )
    m = patron.search(base)
    if m:
        return limpiar(m.group(0))
    return limpiar(base)

def extraer_cliente(linea: str, direccion: str):
    idx = linea.lower().find(direccion.lower())
    if idx > 0:
        return limpiar(linea[:idx])
    return "Cliente"

def extraer_paradas(file_storage):
    paradas = []
    vistos = set()

    with pdfplumber.open(file_storage) as pdf:
        for page in pdf.pages:
            texto = page.extract_text() or ""
            if not texto:
                continue

            lineas = texto.split("\n")
            for linea in lineas:
                linea = limpiar(linea)

                if not linea:
                    continue
                if "Impresión de Hoja de Ruta" in linea:
                    continue
                if "Total Documentos" in linea:
                    continue
                if "CHOFER" in linea:
                    continue
                if "CONTROLADOR" in linea:
                    continue
                if "IMPORTANTE" in linea:
                    continue

                if not contiene_direccion(linea):
                    continue

                localidad = detectar_localidad(linea) or "CABA"
                direccion = extraer_direccion(linea, localidad)
                cliente = extraer_cliente(linea, direccion)

                direccion_mapa = f"{direccion}, {localidad}, Buenos Aires, Argentina"
                key = direccion_mapa.lower()

                if key in vistos:
                    continue
                vistos.add(key)

                paradas.append({
                    "cliente": cliente,
                    "direccion": direccion,
                    "localidad": localidad,
                    "direccion_mapa": direccion_mapa
                })

    return paradas
