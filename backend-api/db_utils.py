from sqlmodel import Session
from models import Factura
from database import engine

def insertar_factura_y_lineas(factura: Factura) -> Factura:
    with Session(engine) as session:
        session.add(factura)
        session.commit()
        session.refresh(factura)
        return factura

