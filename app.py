from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Configurar Firebase
cred = credentials.Certificate(r"C:\Users\Johana\Desktop\grilla\g.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://grilla-2a75e-default-rtdb.firebaseio.com"
})

# Ruta para el home
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["GET"])
def search_channel():
    query = request.args.get("query", "").strip().lower()
    filter_sat = request.args.get("filter", "").lower() == "satelite"
    filter_ipquam = request.args.get("filter", "").lower() == "ipquam"
    filter_fuente = request.args.get("filter", "").lower() == "fuente"
    filter_ts_out = request.args.get("filter", "").lower() == "ts_out"
    filter_frecuencia = request.args.get("filter", "").lower() == "frecuencia"  # Nuevo filtro

    channels_ref = db.reference("channels")
    channels = channels_ref.get()

    results = []

    for key, data in channels.items():
        # Búsqueda por campos específicos
        satellite = str(data.get("satelite", "")).strip().lower()
        targeta_ipquam = str(data.get("targeta_ipquam", "")).strip()
        fuente = str(data.get("fuente", "")).strip().lower()
        ts_out = str(data.get("ts_out_3680", "")).strip()
        frecuencia_caja = str(data.get("frecuencia_caja", "")).strip()

        # Filtro combinado: tarjeta y TS Out (ejemplo: "2/11")
        if filter_ipquam and filter_ts_out:
            if "/" in query:
                parts = query.split("/")
                if len(parts) == 2:
                    tarjeta_query, ts_query = parts
                    if tarjeta_query != targeta_ipquam or ts_query != ts_out:
                        continue

        # Filtro combinado: tarjeta y frecuencia (ejemplo: "2/474")
        elif filter_ipquam and filter_frecuencia:
            if "/" in query:
                parts = query.split("/")
                if len(parts) == 2:
                    tarjeta_query, frecuencia_query = parts
                    if tarjeta_query != targeta_ipquam or frecuencia_query != frecuencia_caja:
                        continue

        # Filtro individual por frecuencia
        elif filter_frecuencia:
            if query != frecuencia_caja:
                continue

        # Filtro individual por tarjeta IPQuam
        elif filter_ipquam:
            if query != targeta_ipquam:
                continue

        # Filtro individual por TS Out
        elif filter_ts_out:
            if query != ts_out:
                continue

        # Filtro individual por satélite
        elif filter_sat:
            sat_match = (
                query in satellite or
                query in satellite.replace("(", "").replace(")", "").replace(" ", "") or
                query in satellite.split("(")[0].strip()
            )
            if not sat_match:
                continue

        # Filtro por fuente (búsqueda parcial)
        elif filter_fuente:
            if query not in fuente:
                continue

        # Búsqueda normal por nombre o ID de canal
        canal_id = str(data.get("canal_id", "")).strip().lower()
        nombre_canal = data.get("nombre_canal", "").strip().lower()

        if (query in canal_id or 
            query in nombre_canal or 
            filter_sat or 
            filter_ipquam or 
            filter_fuente or
            filter_ts_out or 
            filter_frecuencia):
            results.append({
                "key": key,
                **data
            })

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
