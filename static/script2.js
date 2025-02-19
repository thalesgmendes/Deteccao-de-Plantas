const video = document.querySelector("video");
const captureBtn = document.getElementById("capture-btn");
const processedImage = document.getElementById("processed-image");
const infoBtn = document.getElementById("info-btn");

let detectedPlantName = "";

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        video.play();
    })
    .catch(error => {
        console.log("Erro ao acessar a câmera:", error);
    });

captureBtn.addEventListener("click", async () => {
    const canvas = document.createElement("canvas");
    canvas.height = video.videoHeight;
    canvas.width = video.videoWidth;

    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0);

    const imageData = canvas.toDataURL("image/jpeg");

    try {
        const response = await fetch("http://localhost:5000/process", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ image: imageData }),
        });

        if (!response.ok) {
            throw new Error("Erro ao processar a imagem no backend");
        }

        const data = await response.json();
        const processedImageData = data.processed_image;
        detectedPlantName = data.plant_name;

        processedImage.src = processedImageData;
        processedImage.style.display = "block";
    } catch (error) {
        console.error("Erro:", error);
    }
});

infoBtn.addEventListener("click", () => {
    if (detectedPlantName) {
        window.location.href = `/info/${detectedPlantName}`;
    } else {
        alert("Nenhuma planta detectada. Tire uma foto primeiro.");
    }
});