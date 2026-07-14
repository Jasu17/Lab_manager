"""
Servicio de pacientes.
Cubre las operaciones definidas en RF10.2 (registrar) y RF10.3
(buscar, editar). No se permite eliminar pacientes ni registrarlos
desde el módulo de edición (RF10.3) 
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.paciente import Paciente

def create_paciente(
    db: Session,
    identificacion: str,
    tipo_id: str,
    nombre: str,
    telefono: str | None = None,
    fecha_nacimiento=None,
    eps: str | None = None,
    sexo: str | None = None,
    estado_civil: str | None = None,
    hijos: int | None = None,
    estudios: str | None = None,
    responsable: str | None = None,
) -> Paciente :
    """
    Crea un nuevo paciente. Solo identificacion, tipo_id y nombre son obligatorios
    (registro rapido desde RF10.2); el resto se puede completar luego vía update_paciente
    """
    paciente = Paciente(
        identificacion = identificacion,
        tipo_id = tipo_id,
        nombre = nombre,
        telefono = telefono,
        fecha_nacimiento = fecha_nacimiento,
        eps = eps,
        sexo = sexo,
        estado_civil = estado_civil,
        hijos = hijos,
        estudios = estudios,
        responsable = responsable,
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    return paciente

def get_paciente_by_id(db: Session, id_paciente: int) -> Paciente | None:
    """Obtiene un paciente por su ID."""
    return db.query(Paciente).filter(Paciente.id_paciente == id_paciente).first

def search_pacientes(db: Session, query: str) -> list[Paciente]:
    """
    Busca pacientes por nombre o identificacion.
    Busqueda parcial e insensible a mayúsculas/minpusculas.
    """
    filtro = f"%{query}%"
    return (
        db.query(Paciente)
        .filter(
            or_(
                Paciente.nombre.ilike(filtro),
                Paciente.identificacion.ilike(filtro),
            )
        )
        .all()
    )

def update_paciente(db: Session, id_paciente: int, **campos) -> Paciente | None:
    """
    Actualiza los campos de un paciente existente
    campos: pares clave-valor correspondientes a atributos de Paciente.
    """
    paciente = get_paciente_by_id(db, id_paciente)
    if paciente is None:
        return None

    for campo, valor in campos.items():
        if hasattr(paciente, campo):
            setattr(paciente, campo, valor)

    db.commit()
    db.refresh(paciente)
    return paciente