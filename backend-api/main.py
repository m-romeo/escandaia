from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from procesamiento.parser_facturas import parse_text_ocr
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

@app.get("/procesar-factura-pdf")
def procesar_factura_pdf():
    from ocr_google_document import procesar_pdf_en_gcs, descargar_texto_ocr

    ruta_pdf = "gs://facturas-escandaia/pendientes/Factura2206163457.pdf"
    salida = procesar_pdf_en_gcs(ruta_pdf)

    import time
    time.sleep(10)  # o bucle inteligente en el futuro

    texto = descargar_texto_ocr(salida)
    datos = parse_text_ocr(texto)

    return {
        "mensaje": "Factura procesada",
        "datos_estructurados": datos
    }
