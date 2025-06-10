import re
from datetime import datetime

def parse_text_ocr(texto: str) -> dict:
    proveedor = None
    fecha = None
    numero_factura = None
    total = None
    productos = []

    texto = texto.replace('\r', '').strip()
    lineas = texto.split('\n')

    # --- Proveedor ---
    for linea in lineas[:15]:
        if any(palabra in linea.lower() for palabra in ["s.l", "slu", "sociedad", "distribuciones", "paruben", "asador"]):
            proveedor = linea.strip()
            break

    # --- Fecha ---
    patrones_fecha = [
        r"\b(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})\b",
        r"Fecha\s*(?:factura|emisión)?[:\-]?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})"
    ]
    for linea in lineas:
        for patron in patrones_fecha:
            match = re.search(patron, linea, re.IGNORECASE)
            if match:
                fecha = match.group(1)
                break
        if fecha:
            break

    # --- Número de factura ---
    patrones_factura = [
        r"factura\s*n[ºo]?[\.]?\s*([A-Z0-9\-\/]+)",
        r"n[ºo]?\s*factura[:\-]?\s*([A-Z0-9\-\/]+)",
        r"f[\/\-]\s?([0-9]+)",
        r"([A-Z]{2,5}\d{6,})"
    ]
    for linea in lineas:
        for patron in patrones_factura:
            match = re.search(patron, linea, re.IGNORECASE)
            if match:
                numero_factura = match.group(1)
                break
        if numero_factura:
            break

    # --- Total ---
    for linea in reversed(lineas):
        if "total" in linea.lower():
            match = re.search(r"([\d]+\,[\d]{2})", linea)
            if match:
                total = match.group(1).replace(",", ".")
                break

    # --- Productos (estructura libre, heurística por bloques) ---
    i = 0
    while i < len(lineas) - 1:
        linea = lineas[i].strip()
        sig = lineas[i+1].strip() if i+1 < len(lineas) else ""

        # Si la línea parece descripción y la siguiente contiene precio
        if re.search(r"[A-Za-z]{3,}", linea) and re.search(r"\d+,\d{2}", sig):
            descripcion = linea
            posibles_numeros = re.findall(r"\d+,\d{2}", sig)
            cantidad_match = re.search(r"\d+", sig)

            producto = {
                "descripcion": descripcion,
                "cantidad": int(cantidad_match.group()) if cantidad_match else None,
                "precio_unitario": float(posibles_numeros[0].replace(",", ".")) if len(posibles_numeros) > 0 else None,
                "total": float(posibles_numeros[-1].replace(",", ".")) if len(posibles_numeros) > 1 else None
            }
            productos.append(producto)
            i += 2
        else:
            i += 1

    return {
        "proveedor": proveedor,
        "fecha": fecha,
        "numero_factura": numero_factura,
        "productos": productos,
        "total": float(total) if total else None
    }
