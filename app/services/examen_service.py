from sqlalchemy.orm import Session
from app.models.examen import ExamenRealizado, EstadoExamen, TipoExamen

def get_examem_by_id(db: Session, id_examen: int) -> ExamenRealizado | None:
    return db.query(ExamenRealizado).filter(
        ExamenRealizado.id_examen == id_examen
    ).first()

def get_examenes_by_cita(db: Session, id_cita: int) -> list[ExamenRealizado]:
    return db.query(ExamenRealizado).filter(
        ExamenRealizado.cita == id_cita
    ).all()

def get_all_tipos_examen(db: Session) -> list[TipoExamen]:
    return db.query(TipoExamen).order_by(TipoExamen.nombre).all()

def save_resultado(
    db: Session,
    id_examen: int,
    id_usuario: int,
    resultado: str | None = None,
    observaciones: str | None = None,
    completar: bool = False, 
) -> ExamenRealizado | None:

    examen = get_examem_by_id(db, id_examen)
    if examen is None:
        return None

    if resultado is not None:
        examen.resultado = resultado
    if observaciones is not None:
        examen.observaciones = observaciones
    
    examen.id_usuario = id_usuario
    examen.estado = EstadoExamen.COMPLETADO if completar else EstadoExamen.EN_PROCESO

    db.commit()
    db.refresh(examen)
    return examen