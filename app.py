from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from ultralytics import YOLO
import base64
import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

cred = credentials.Certificate('./deteccao-de-plantas-firebase-adminsdk-fbsvc-164c9c4490.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

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
    print(plant_name)
    doc_ref = db.collection("plantas").document(plant_name)
    doc = doc_ref.get()
    if doc.exists:
        info = doc.to_dict()
    else:
        info = None

    return render_template("info.html", plant=info)

if __name__ == "__main__":
    app.run(debug=True)