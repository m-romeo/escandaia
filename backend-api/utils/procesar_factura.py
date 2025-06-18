from pathlib import Path
from ocr_google_document import procesar_pdf_en_gcs
from procesamiento.parser_facturas import parse_text_ocr
from db_utils import insertar_factura_y_lineas
from exportar_a_excel import exportar_excel_desde_bd

def procesar_factura_y_actualizar_excel(path_pdf: str):
    ruta = Path(path_pdf)
    if not ruta.exists():
        raise FileNotFoundError(f"El archivo {path_pdf} no existe.")

    # Paso 1: Ejecutar OCR en el PDF
    print(f"Ejecutando OCR en: {path_pdf}")
    texto = procesar_pdf_en_gcs(str(ruta))

    # Paso 2: Parsear texto
    print("Parseando texto extraído...")
    datos = parse_text_ocr(texto)

    # Paso 3: Guardar en base de datos
    print("Guardando en base de datos...")
    insertar_factura_y_lineas(datos)

    # Paso 4: Actualizar Excel
    print("Actualizando Excel maestro...")
    exportar_excel_desde_bd()

    print("Proceso completo: OCR + Guardado + Excel actualizado.")
