import os
from flask import Flask, render_template, request
from utils.parser import extraer_direcciones
from utils.geocoding import geocodificar
from utils.optimizer import optimizar_ruta, generar_link_maps

app = Flask(__name__)

DEPOSITOS = {
    "monte_chingolo": "Monte Chingolo, Buenos Aires, Argentina",
    "roque_perez": "Roque Perez, Buenos Aires, Argentina"
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            deposito = request.form.get("deposito")
            archivo = request.files.get("file")

            if not deposito:
                return "Error: no se seleccionó depósito", 400

            if deposito not in DEPOSITOS:
                return "Error: depósito inválido", 400

            if not archivo or archivo.filename == "":
                return "Error: no se adjuntó ningún archivo", 400

            direcciones = extraer_direcciones(archivo)

            if not direcciones:
                return "Error: no se pudieron extraer direcciones del archivo", 400

            puntos = []
            for d in direcciones:
                coords = geocodificar(d)
                if coords:
                    puntos.append({
                        "direccion": d,
                        "coords": coords
                    })

            if not puntos:
                return "Error: no se pudieron geocodificar las direcciones", 400

            origen = geocodificar(DEPOSITOS[deposito])

            if not origen:
                return "Error: no se pudo geocodificar el depósito de salida", 400

            ruta_optimizada, distancia_total, tiempo_total = optimizar_ruta(origen, puntos)

            link_maps = generar_link_maps(origen, ruta_optimizada) if ruta_optimizada else None

            return render_template(
                "index.html",
                ruta=ruta_optimizada,
                distancia=distancia_total,
                tiempo=tiempo_total,
                link=link_maps,
                deposito=DEPOSITOS[deposito]
            )

        except Exception as e:
            return f"Error interno: {str(e)}", 500

    return render_template("index.html", ruta=None, distancia=None, tiempo=None, link=None)

@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
