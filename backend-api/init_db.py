from sqlmodel import SQLModel, create_engine
from models import Factura, LineaFactura

sqlite_file = "facturas.db"
engine = create_engine(f"sqlite:///{sqlite_file}")

def crear_base_de_datos():
    SQLModel.metadata.create_all(engine)
    print(f"Base de datos creada: {sqlite_file}")

if __name__ == "__main__":
    crear_base_de_datos()