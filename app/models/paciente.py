"""
Modelo de paciente.
Contiene la información básica registrada por el recepcionista.
"""

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.models.base import Base


class Paciente(Base):
    __tablename__ = "paciente"

    id_paciente = Column(Integer, primary_key=True, autoincrement=True)
    identificacion = Column(String, unique=True, nullable=False)
    tipo_id = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    eps = Column(String, nullable=True)
    sexo = Column(String, nullable=True)
    estado_civil = Column(String, nullable=True)
    hijos = Column(Integer, nullable=True)
    estudios = Column(String, nullable=True)
    responsable = Column(String, nullable=True)
    ciudad = Column(String, nullable=True)

    # Relaciones
    citas = relationship("Cita", back_populates="paciente")