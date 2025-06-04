from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil, os

from google.cloud import vision

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/factura")
async def recibir_factura(file: UploadFile = File(...)):
    # Guardar la imagen recibida
    os.makedirs("facturas_recibidas", exist_ok=True)
    file_path = f"facturas_recibidas/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Usar Google Vision para hacer OCR
    client = vision.ImageAnnotatorClient()

    with open(file_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    text = response.full_text_annotation.text if response.full_text_annotation.text else ""

    # Respuesta limpia en formato JSON
    return JSONResponse(content={
        "mensaje": "Factura recibida",
        "archivo": file.filename,
        "texto_detectado": text
    })
