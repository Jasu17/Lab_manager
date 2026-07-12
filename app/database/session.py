"""
Configuracion en la base de datos.
Define el engine de SQLAlchemy, la fabrica de sesiones y la función de inicialiacion que crea las tablas si no existen
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

DATABASE_URL= "sqlite:///lab_manager.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker (bind=engine, autoflush=False, autocommit=False)

def init_db():
    """
    Crea todas las tablas definidas en los modelos si no existen aun,
    Debe llamarse una sola vez al iniciar la aplicación (o reemplazarse
    por Alembic una vez se gestionen migraciones).
    """
    from app.models import usuario, paciente, examen, cita, encuesta #noqa: F401
    Base.metadata.create_all(bind=engine)
