"""Modelos de base de datos para almacenar facturas y sus líneas."""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Factura(SQLModel, table=True):
    """Cabecera de una factura extraída mediante OCR."""
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre_archivo: str
    proveedor: Optional[str]
    fecha: Optional[str]
    numero_factura: Optional[str]
    total: Optional[float]
    creada_en: datetime = Field(default_factory=datetime.utcnow)

class LineaFactura(SQLModel, table=True):
    """Detalle de productos o servicios asociados a una factura."""
    id: Optional[int] = Field(default=None, primary_key=True)
    factura_id: int = Field(foreign_key="factura.id")
    descripcion: str
    cantidad: Optional[float]
    precio_unitario: Optional[float]
    total_linea: Optional[float]

