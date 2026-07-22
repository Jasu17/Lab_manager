"""
Modelos de exámenes.
TipoExamen: catálogo de exámenes ofrecidos por el laboratorio.
ExamenRealizado: instancia de un examen aplicado en una cita específica.
"""

import enum
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class EstadoExamen(enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADO = "COMPLETADO"


class TipoExamen(Base):
    __tablename__ = "tipo_examen"

    id_tipo_examen = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    referencia = Column(String, nullable=True)
    precio = Column(Integer, nullable=False)
    tipo_muestra = Column(String, nullable=True)
    tecnica_utilizada = Column(String, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)

    # Relaciones
    examenes_realizados = relationship("ExamenRealizado", back_populates="tipo_examen")


class ExamenRealizado(Base, TimestampMixin):
    __tablename__ = "examen_realizado"

    id_examen = Column(Integer, primary_key=True, autoincrement=True)
    resultado = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)
    precio_cobrado = Column(Integer, nullable=False)
    estado = Column(Enum(EstadoExamen), default=EstadoExamen.PENDIENTE, nullable=False)

    # Foreign Keys
    id_cita = Column(Integer, ForeignKey("cita.id_cita"), nullable=False)
    id_tipo_examen = Column(Integer, ForeignKey("tipo_examen.id_tipo_examen"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=True)

    # Relaciones
    cita = relationship("Cita", back_populates="examenes")
    tipo_examen = relationship("TipoExamen", back_populates="examenes_realizados")
    usuario = relationship("Usuario", back_populates="examenes_registrados")