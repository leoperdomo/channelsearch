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
    filter_sat = request.args.get("filter", "").lower() == "satellite"
    filter_ipquam = request.args.get("filter", "").lower() == "ipquam"
    
    channels_ref = db.reference("channels")
    channels = channels_ref.get()

    if not query:
        return jsonify({"error": "Debes proporcionar un término de búsqueda."}), 400

    results = []
    
    for key, data in channels.items():
        # Comprobar si el filtro de tarjeta IPQuam está activado
        if filter_ipquam:
            targeta_ipquam = str(data.get("targeta_ipquam", "")).lower()
            if query not in targeta_ipquam:
                continue  # Si la búsqueda no coincide con la tarjeta, omitir el canal

        # Comprobar si el filtro de satélite está activado
        if filter_sat:
            satellite = str(data.get("satelite", "")).lower()  # Asegúrate de usar el campo correcto
            if query not in satellite:
                continue  # Si la búsqueda no coincide con el satélite, omitir el canal
        
        # Filtrar también por nombre o ID de canal
        if query in str(data.get("canal_id", "")).lower() or query in data.get("nombre_canal", "").lower():
            results.append({
                "key": key,
                **data  # Incluye todos los datos del canal
            })

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
