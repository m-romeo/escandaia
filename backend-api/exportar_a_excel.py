import pandas as pd
from sqlmodel import create_engine, Session, select
from models import Factura, LineaFactura
from pathlib import Path

def exportar_excel_desde_bd():
    # 1. Conectar usando SQLModel (usa el mismo engine que tu app)
    sqlite_file = Path(__file__).parent / "facturas.db"
    engine = create_engine(f"sqlite:///{sqlite_file}")

    # 2. Cargar datos desde la base con SQLModel
    with Session(engine) as session:
        facturas = session.exec(select(Factura)).all()
        lineas = session.exec(select(LineaFactura)).all()

    # 3. Convertir a DataFrame
    df_facturas = pd.DataFrame([f.model_dump() for f in facturas])
    df_lineas = pd.DataFrame([l.model_dump() for l in lineas])

    # 4. Unir facturas + líneas
    df = df_lineas.merge(
        df_facturas,
        left_on="factura_id",
        right_on="id",
        suffixes=("_linea", "_factura"),
        how="left"
    )

    # 5. Seleccionar y renombrar columnas
    df = df[[
        "factura_id",
        "fecha",
        "proveedor",
        "numero_factura",
        "descripcion",
        "cantidad",
        "precio_unitario",
        "total_linea",
        "total"
    ]]
    df.columns = [
        "Factura ID",
        "Fecha",
        "Proveedor",
        "Núm. Factura",
        "Descripción",
        "Cantidad",
        "Precio Unitario",
        "Total Línea",
        "Total Factura"
    ]

    # 6. Guardar en Excel
    output = Path(__file__).parent / "facturas_maestro.xlsx"
    df.to_excel(output, index=False)

    print(f"Excel actualizado en: {output}")

