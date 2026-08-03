"""
Modelos de autenticación y roles.
Usuario y Rol se relacionan muchos a muchos a través de UsuarioRol.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    identificacion = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    registro_profesional = Column(String, nullable=True)
    firma_imagen = Column(String, nullable=True)

    # Relaciones
    roles = relationship(
        "Rol",
        secondary="usuario_rol",
        back_populates="usuarios"
    )
    citas_registradas = relationship("Cita", back_populates="usuario")
    examenes_registrados = relationship("ExamenRealizado", back_populates="usuario")


class Rol(Base):
    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False)

    # Relaciones
    usuarios = relationship(
        "Usuario",
        secondary="usuario_rol",
        back_populates="roles"
    )


class UsuarioRol(Base):
    __tablename__ = "usuario_rol"

    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), primary_key=True)
    id_rol = Column(Integer, ForeignKey("rol.id_rol"), primary_key=True)