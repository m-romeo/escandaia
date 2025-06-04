from google.cloud import vision_v1 as vision
from google.cloud.vision_v1 import types
import time

def procesar_pdf_en_gcs(gcs_input_uri: str):
    client = vision.ImageAnnotatorClient()

    # Configuración de OCR
    mime_type = 'application/pdf'
    batch_size = 2  # Máx. páginas por archivo PDF a procesar a la vez

    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    gcs_source = vision.GcsSource(uri=gcs_input_uri)
    input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination_uri = gcs_input_uri.replace(".pdf", "_output/")
    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature],
        input_config=input_config,
        output_config=output_config,
    )

    operation = client.async_batch_annotate_files(requests=[async_request])
    print("Esperando resultado de OCR Document...")

    operation.result(timeout=300)  # Espera máxima de 5 minutos

    print(f"✅ OCR terminado. Resultado guardado en: {gcs_destination_uri}")
    return gcs_destination_uri


from google.cloud import storage
import json

def descargar_texto_ocr(gcs_output_uri: str):
    # gcs_output_uri = 'gs://bucket/nombre_output/'
    bucket_name = gcs_output_uri.replace("gs://", "").split("/")[0]
    prefix = "/".join(gcs_output_uri.replace("gs://", "").split("/")[1:])

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = list(bucket.list_blobs(prefix=prefix))
    json_blobs = [blob for blob in blobs if blob.name.endswith(".json")]

    if not json_blobs:
        return "No se encontró ningún resultado JSON de OCR."

    # Cargar el primer archivo JSON (normalmente hay uno por PDF)
    blob = json_blobs[0]
    contenido = blob.download_as_bytes()
    data = json.loads(contenido)

    # Extraer texto completo
    full_text = data["responses"][0]["fullTextAnnotation"]["text"]

    return full_text
