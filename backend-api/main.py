from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import Body
from procesamiento.parser_facturas import parse_text_ocr
import shutil, os

from google.cloud import vision
from google.cloud import storage

from sqlmodel import Session, select
from sqlmodel import SQLModel, create_engine
from models import Factura, LineaFactura

from sqlmodel import SQLModel, create_engine
from models import Factura, LineaFactura

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///facturas.db")

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

@app.get("/procesar-pdf-ocr")
def procesar_factura_pdf(pdf: str):
    from ocr_google_document import procesar_pdf_en_gcs, descargar_texto_ocr

    ruta_pdf = f"gs://facturas-escandaia/pendientes/{pdf}"
    salida = procesar_pdf_en_gcs(ruta_pdf)

    import time
    time.sleep(10)

    texto = descargar_texto_ocr(salida)
    return {
        "mensaje": "Factura procesada con éxito",
        "texto_extraido": texto
    }

@app.get("/procesar-nuevos-pdfs")
def procesar_nuevos_pdfs():
    from ocr_google_document import procesar_pdf_en_gcs, descargar_texto_ocr
    import time

    bucket_name = "facturas-escandaia"
    prefix = "pendientes/"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = list(bucket.list_blobs(prefix=prefix))
    resultados = []

    for blob in blobs:
        if blob.name.endswith(".pdf"):
            nombre_pdf = blob.name.split("/")[-1].replace(".pdf", "")
            ruta_salida = f"{prefix}{nombre_pdf}_output/output.json"

            # Si ya existe output.json, saltamos
            if storage.Blob(bucket=bucket, name=ruta_salida).exists(storage_client):
                resultados.append({
                    "archivo": blob.name,
                    "estado": "ya procesado"
                })
                continue

            # Si no existe, procesamos
            try:
                ruta_pdf = f"gs://{bucket_name}/{blob.name}"
                salida = procesar_pdf_en_gcs(ruta_pdf)
                time.sleep(10)
                texto = descargar_texto_ocr(salida)
                resultados.append({
                    "archivo": blob.name,
                    "estado": "procesado",
                    "texto_extraido": texto[:1000]
                })
            except Exception as e:
                resultados.append({
                    "archivo": blob.name,
                    "estado": "error",
                    "detalle": str(e)
                })

    return {"resultados": resultados}

@app.get("/extraer-datos-de-facturas")
def extraer_datos_de_facturas():
    from procesamiento.parser_facturas import parse_text_ocr
    from ocr_google_document import descargar_texto_ocr
    from google.cloud import storage

    bucket_name = "facturas-escandaia"
    prefix = "pendientes/"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = list(bucket.list_blobs(prefix=prefix))
    resultados = []

    for blob in blobs:
        if blob.name.endswith(".json") and "_output/" in blob.name:
            try:
                ruta_salida = f"gs://{bucket_name}/{blob.name}"
                texto = descargar_texto_ocr(ruta_salida)
                datos = parse_text_ocr(texto)

                resultados.append({
                    "archivo": blob.name,
                    "texto": texto[:3000],  # o más, si quieres ver más info
                    "datos_estructurados": datos
                })
            except Exception as e:
                resultados.append({
                    "archivo": blob.name,
                    "estado": "error",
                    "detalle": str(e)
                })

    return {"facturas": resultados}

@app.get("/guardar-datos-en-db")
def guardar_datos_en_db():
    from procesamiento.parser_facturas import parse_text_ocr
    from ocr_google_document import descargar_texto_ocr
    from google.cloud import storage

    bucket_name = "facturas-escandaia"
    prefix = "pendientes/"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = list(bucket.list_blobs(prefix=prefix))
    resultados = []

    with Session(engine) as session:
        for blob in blobs:
            if blob.name.endswith(".json") and "_output/" in blob.name:
                nombre_archivo = blob.name.replace("_output/output.json", "").replace("pendientes/", "")

                # ¿Ya está guardado?
                existe = session.exec(select(Factura).where(Factura.nombre_archivo == nombre_archivo)).first()
                if existe:
                    resultados.append({
                        "archivo": nombre_archivo,
                        "estado": "ya guardado"
                    })
                    continue

                try:
                    ruta_salida = f"gs://{bucket_name}/{blob.name}"
                    texto = descargar_texto_ocr(ruta_salida)
                    datos = parse_text_ocr(texto)

                    factura = Factura(
                        nombre_archivo=nombre_archivo,
                        proveedor=datos.get("proveedor"),
                        fecha=datos.get("fecha"),
                        numero_factura=datos.get("numero_factura"),
                        total=datos.get("total")
                    )
                    session.add(factura)
                    session.commit()
                    session.refresh(factura)

                    for p in datos.get("productos", []):
                        linea = LineaFactura(
                            factura_id=factura.id,
                            descripcion=p.get("descripcion"),
                            cantidad=p.get("cantidad"),
                            precio_unitario=p.get("precio_unitario"),
                            total_linea=p.get("total")
                        )
                        session.add(linea)

                    session.commit()
                    resultados.append({
                        "archivo": nombre_archivo,
                        "estado": "guardado"
                    })

                except Exception as e:
                    resultados.append({
                        "archivo": nombre_archivo,
                        "estado": "error",
                        "detalle": str(e)
                    })

    return {"resultados": resultados}

@app.get("/facturas")
def listar_facturas():
    from sqlmodel import Session, select
    with Session(engine) as session:
        consulta = select(Factura).order_by(Factura.creada_en.desc())
        resultados = session.exec(consulta).all()
        return JSONResponse(content=jsonable_encoder(resultados))

@app.get("/lineas-factura/{factura_id}")
def obtener_lineas_factura(factura_id: int):
    from sqlmodel import Session, select
    with Session(engine) as session:
        consulta = select(LineaFactura).where(LineaFactura.factura_id == factura_id)
        resultados = session.exec(consulta).all()
        from fastapi.encoders import jsonable_encoder
        return JSONResponse(content=jsonable_encoder(resultados))

@app.post("/facturas")
def crear_factura(factura: Factura = Body(...)):
    with Session(engine) as session:
        session.add(factura)
        session.commit()
        session.refresh(factura)
        return factura

@app.get("/facturas/{factura_id}")
def obtener_factura(factura_id: int):
    with Session(engine) as session:
        factura = session.get(Factura, factura_id)
        if not factura:
            return {"error": "Factura no encontrada"}
        from fastapi.encoders import jsonable_encoder
        return jsonable_encoder(factura)

@app.put("/facturas/{factura_id}")
def actualizar_factura(factura_id: int, datos: dict = Body(...)):
    with Session(engine) as session:
        factura = session.get(Factura, factura_id)
        if not factura:
            return {"error": "Factura no encontrada"}
        
        # Solo actualiza campos válidos del modelo
        campos_validos = factura.dict().keys()
        for campo, valor in datos.items():
            if campo in campos_validos:
                setattr(factura, campo, valor)
        
        session.add(factura)
        session.commit()
        return factura

@app.delete("/facturas/{factura_id}")
def borrar_factura(factura_id: int):
    with Session(engine) as session:
        factura = session.get(Factura, factura_id)
        if not factura:
            return {"error": "Factura no encontrada"}
        session.delete(factura)
        session.commit()
        return {"mensaje": f"Factura {factura_id} eliminada correctamente"}

