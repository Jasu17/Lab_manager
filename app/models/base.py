"""
Modulo para los modelos de SQLAlchemy.
Define la Base declarativa y el mixin de timestamps reutilizable en las entidades que requieren auditoria de creación y modificación.
"""

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime

class Base(DeclarativeBase):
    """Base declarativa para todos los modelos del sistema."""
    pass

class TimestampMixin:
    """
    Mixin que agrega columnas de auditorias temporal,
    Usado por: Cita, ExamenRealziado
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    ) 