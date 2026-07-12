"""
Modelo de cita.
Representa el agendamiento de un paciente, con su estado en el flujo
de atención y datos opcionales de consentimiento informado.
"""

import enum
from sqlalchemy import Column, Integer, String, Date, Time, Boolean, ForeignKey, Enum, LargeBinary
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class EstadoCita(enum.Enum):
    AGENDADA = "AGENDADA"
    EN_ESPERA = "EN_ESPERA"
    EN_ATENCION = "EN_ATENCION"
    FINALIZADA = "FINALIZADA"


class Cita(Base, TimestampMixin):
    __tablename__ = "cita"

    id_cita = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    localidad = Column(String, nullable=True)
    estado = Column(Enum(EstadoCita), default=EstadoCita.AGENDADA, nullable=False)

    # Consentimiento informado (opcional, RF9)
    consentimiento_firmado = Column(Boolean, default=False, nullable=False)
    ruta_consentimiento = Column(String, nullable=True)
    firma_digital = Column(LargeBinary, nullable=True)

    # Foreign Keys
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)

    # Relaciones
    paciente = relationship("Paciente", back_populates="citas")
    usuario = relationship("Usuario", back_populates="citas_registradas")
    examenes = relationship("ExamenRealizado", back_populates="cita")
    respuestas_encuesta = relationship("RespuestaEncuesta", back_populates="cita")