from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from ultralytics import YOLO
import base64
import cv2
import numpy as np
import pyrebase

app = Flask(__name__)
CORS(app)

firebaseConfig = {
  'apiKey': "AIzaSyBTptL4v2ONEmn5CCNGSY3FeefTofz3wp4",
  'authDomain': "deteccao-de-plantas.firebaseapp.com",
  'projectId': "deteccao-de-plantas",
  'storageBucket': "deteccao-de-plantas.firebasestorage.app",
  'databaseURL': "https://deteccao-de-plantas-default-rtdb.firebaseio.com",
  'messagingSenderId': "144203838962",
  'appId': "1:144203838962:web:a62e7f8f2c6adc77f3276b"
}
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()


model = YOLO("best.pt")

@app.route("/")
def inicio():
    return render_template("front.html")

@app.route("/camera")
def camera():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process_image():
    data = request.json
    image_data = data["image"]

    image_data = image_data.split(",")[1]
    image_bytes = base64.b64decode(image_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    results = model(image)
    annotated_frame = results[0].plot()

    if len(results) > 0 and len(results[0].boxes.cls) > 0:
        detected_plant = results[0].names[results[0].boxes.cls[0].item()]
    else:
        detected_plant = "Nenhuma planta detectada"

    _, buffer = cv2.imencode(".jpg", annotated_frame)
    processed_image_data = base64.b64encode(buffer).decode("utf-8")

    return jsonify({
        "processed_image": f"data:image/jpeg;base64,{processed_image_data}",
        "plant_name": detected_plant
    })

@app.route("/info/<plant_name>")
def show_plant_info(plant_name):
    try:
        doc_ref = db.child("plantas").child(plant_name)
        doc = doc_ref.get()

        if doc.val() is None:
            return "Planta não encontrada.", 404
        info = doc.val()
        print(doc.val())
        return render_template('info.html', plant=info)

    except Exception as e:
        return f"Erro ao acessar o banco de dados: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)