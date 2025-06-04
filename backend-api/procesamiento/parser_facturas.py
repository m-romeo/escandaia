import re
from datetime import datetime

def parse_text_ocr(text: str) -> dict:
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    data = {
        "proveedor": None,
        "fecha": None,
        "numero_factura": None,
        "productos": [],
        "total": None
    }

    # Regex útiles
    fecha_regex = r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4}"
    precio_regex = r"\d+[.,]\d{2}"
    proveedor_regex = re.compile(r".*(s\.l|slu|sa|proveedor|distribuciones)", re.IGNORECASE)
    total_regex = re.compile(r"(total|importe.*total)", re.IGNORECASE)

    for line in lines:
        # Proveedor (heurística)
        if not data["proveedor"] and proveedor_regex.search(line):
            data["proveedor"] = line.strip()

        # Fecha
        if not data["fecha"]:
            match = re.search(fecha_regex, line)
            if match:
                fecha_txt = match.group().replace("-", "/").replace(".", "/")
                try:
                    data["fecha"] = datetime.strptime(fecha_txt, "%d/%m/%Y").date().isoformat()
                except:
                    pass

        # Número de factura
        if not data["numero_factura"]:
            if "factura" in line.lower():
                num_match = re.search(r"\d{6,}", line)  # 6 dígitos o más
                if num_match:
                    data["numero_factura"] = num_match.group()

        # Total de factura
        if not data["total"] and total_regex.search(line):
            match = re.search(precio_regex, line)
            if match:
                data["total"] = float(match.group().replace(",", "."))

        # Posible producto (muy general, para refinar)
        producto_match = re.match(
            r"(.+?)\s+(\d+(?:[.,]\d+)?)(\s*(kg|g|l|ud|unidad(?:es)?))?\s+(\d+[.,]\d{2})",
            line.lower()
        )
        if producto_match:
            nombre = producto_match.group(1).strip()
            cantidad = float(producto_match.group(2).replace(",", "."))
            unidad = producto_match.group(4) if producto_match.group(4) else ""
            precio = float(producto_match.group(5).replace(",", "."))

            data["productos"].append({
                "nombre": nombre,
                "cantidad": cantidad,
                "unidad": unidad,
                "precio": precio
            })

    return data
