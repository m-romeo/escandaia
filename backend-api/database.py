from sqlmodel import create_engine

# Ruta local de la base de datos SQLite
DATABASE_URL = "sqlite:///facturas.db"
engine = create_engine(DATABASE_URL, echo=False)
