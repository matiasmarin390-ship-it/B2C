from flask import Flask, render_template, request
from utils.parser import extraer_direcciones
from utils.geocoding import geocodificar
from utils.optimizer import optimizar_ruta, generar_link_maps

app = Flask(__name__)

DEPOSITOS = {
    "monte_chingolo": "Monte Chingolo, Buenos Aires",
    "roque_perez": "Roque Perez, Buenos Aires"
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        deposito = request.form["deposito"]
        archivo = request.files["file"]

        direcciones = extraer_direcciones(archivo)

        puntos = []
        for d in direcciones:
            coords = geocodificar(d)
            if coords:
                puntos.append({"direccion": d, "coords": coords})

        origen = geocodificar(DEPOSITOS[deposito])

        ruta_optimizada, distancia_total, tiempo_total = optimizar_ruta(origen, puntos)

        link_maps = generar_link_maps(origen, ruta_optimizada)

        return render_template("index.html",
                               ruta=ruta_optimizada,
                               distancia=distancia_total,
                               tiempo=tiempo_total,
                               link=link_maps)

    return render_template("index.html")
