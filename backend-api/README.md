# Backend API

Este directorio contiene la API escrita en **FastAPI** para procesar facturas mediante OCR y almacenarlas en una base de datos SQLite.

## Requisitos

- Python 3.9 o superior
- Instalar dependencias:
  ```bash
  pip install -r requirements.txt
  ```
- Configurar las credenciales de Google Cloud en la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS` para poder usar Vision y Storage.

## Puesta en marcha

1. Crear la base de datos local:
   ```bash
   python init_db.py
   ```
2. Lanzar la API en modo desarrollo:
   ```bash
   uvicorn main:app --reload
   ```

La base `facturas.db` y las imágenes subidas se guardan en este mismo directorio.

## Archivos principales

- `main.py` – Aplicación FastAPI con los endpoints para subir facturas, procesar PDFs con Google Vision y consultar la información.
- `models.py` – Modelos SQLModel (`Factura` y `LineaFactura`).
- `ocr_google_document.py` – Funciones que lanzan el OCR en Google Cloud Storage y descargan los resultados.
- `procesamiento/parser_facturas.py` – Heurísticas para convertir el texto del OCR en datos estructurados.
- `init_db.py` – Script para crear las tablas de SQLite.
- `requirements.txt` – Lista de dependencias.

## Endpoints destacados

- `POST /factura` – Sube una imagen y devuelve el texto detectado.
- `GET /procesar-factura-pdf` – Ejemplo de OCR sobre un PDF en GCS.
- `GET /procesar-pdf-ocr?pdf=nombre.pdf` – Procesa un PDF concreto.
- `GET /procesar-nuevos-pdfs` – Ejecuta el OCR de todos los PDFs pendientes en el bucket.
- `GET /extraer-datos-de-facturas` – Descarga los JSON de OCR y extrae información.
- `GET /guardar-datos-en-db` – Guarda en SQLite los datos estructurados.
- CRUD de facturas: `GET /facturas`, `POST /facturas`, `GET/PUT/DELETE /facturas/{id}`, `GET /lineas-factura/{factura_id}`.

## Flujo básico

1. Se sube una imagen o PDF de factura.
2. Google Vision extrae el texto del documento.
3. `parser_facturas.py` interpreta el texto para obtener proveedor, fecha, líneas de producto y total.
4. `guardar_datos_en_db` inserta esta información en `facturas.db`.
5. El dashboard web y la app móvil consumen los datos desde estos endpoints.

