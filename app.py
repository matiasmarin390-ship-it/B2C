from flask import Flask, render_template, request
from utils.parser import extraer_direcciones
from utils.optimizer import optimizar_ruta, generar_link_maps
import os

app = Flask(__name__)

DEPOSITOS = {
    "monte_chingolo": "Monte Chingolo, Buenos Aires",
    "roque_perez": "Roque Perez, Buenos Aires"
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            deposito = request.form.get("deposito")
            archivo = request.files.get("file")

            if not deposito or deposito not in DEPOSITOS:
                return "Error: depósito inválido"

            if not archivo:
                return "Error: falta archivo"

            direcciones = extraer_direcciones(archivo)

            if not direcciones:
                return "No se detectaron direcciones"

            origen = DEPOSITOS[deposito]

            ruta, distancia, tiempo = optimizar_ruta(origen, direcciones)

            link_maps = generar_link_maps(origen, direcciones)

            return render_template(
                "index.html",
                ruta=ruta,
                distancia=distancia,
                tiempo=tiempo,
                link=link_maps,
                deposito=origen
            )

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("index.html", ruta=None)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
