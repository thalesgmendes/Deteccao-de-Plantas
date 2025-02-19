from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from ultralytics import YOLO
import base64
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

model = YOLO("best.pt")

plant_info = {
    "buganvilia": {
        "name": "Buganvília",
        "description": "A buganvília é uma planta ornamental conhecida por suas cores vibrantes.",
        "care_tips": "Necessita de sol pleno e regas regulares."
    },
    "tulip": {
        "name": "Tulipa",
        "description": "Tulipas são flores coloridas que simbolizam elegância.",
        "care_tips": "Plante em solo bem drenado e regue moderadamente."
    },
    # Adicione mais plantas aqui
}

@app.route("/")
def inicio():
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

    # Captura o nome da planta detectada
    detected_plant = results[0].names[results[0].boxes.cls[0].item()]  # Pega a primeira detecção

    _, buffer = cv2.imencode(".jpg", annotated_frame)
    processed_image_data = base64.b64encode(buffer).decode("utf-8")

    return jsonify({
        "processed_image": f"data:image/jpeg;base64,{processed_image_data}",
        "plant_name": detected_plant  # Retorna o nome da planta
    })

@app.route("/info/<plant_name>")
def show_plant_info(plant_name):
    info = plant_info.get(plant_name.lower(), {
        "name": "Desconhecida",
        "description": "Informações não disponíveis para esta planta.",
        "care_tips": "Consulte um especialista para mais detalhes."
    })
    return render_template("info.html", plant=info)

if __name__ == "__main__":
    app.run(debug=True)