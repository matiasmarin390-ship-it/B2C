import pdfplumber

def extraer_direcciones(file):
    direcciones = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            lines = text.split("\n")
            for line in lines:
                if "Calle" in line or "Avenida" in line or "Av." in line:
                    partes = line.split()
                    direccion = " ".join(partes[1:5])
                    direcciones.append(direccion + ", Buenos Aires")

    return direcciones
