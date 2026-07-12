"""
Modelos de encuestas de satisfacción.
Estructura dinámica: el administrador define encuestas con preguntas
propias, y las respuestas quedan asociadas a una cita puntual.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Encuesta(Base):
    __tablename__ = "encuesta"

    id_encuesta = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    activa = Column(Boolean, default=True, nullable=False)

    # Relaciones
    preguntas = relationship("Pregunta", back_populates="encuesta")


class Pregunta(Base):
    __tablename__ = "pregunta"

    id_pregunta = Column(Integer, primary_key=True, autoincrement=True)
    texto = Column(String, nullable=False)
    tipo_respuesta = Column(String, nullable=False)

    # Foreign Keys
    id_encuesta = Column(Integer, ForeignKey("encuesta.id_encuesta"), nullable=False)

    # Relaciones
    encuesta = relationship("Encuesta", back_populates="preguntas")
    respuestas = relationship("RespuestaEncuesta", back_populates="pregunta")


class RespuestaEncuesta(Base):
    __tablename__ = "respuesta_encuesta"

    id_respuesta = Column(Integer, primary_key=True, autoincrement=True)
    valor = Column(String, nullable=False)
    fecha = Column(DateTime, nullable=False)

    # Foreign Keys
    id_pregunta = Column(Integer, ForeignKey("pregunta.id_pregunta"), nullable=False)
    id_cita = Column(Integer, ForeignKey("cita.id_cita"), nullable=False)

    # Relaciones
    pregunta = relationship("Pregunta", back_populates="respuestas")
    cita = relationship("Cita", back_populates="respuestas_encuesta")