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

def get_all_tipos_examen(db: Session, solo_activos: bool = True) -> list[TipoExamen]:
    query = db.query(TipoExamen)
    if solo_activos:
        query = query.filter(TipoExamen.activo == True)
    return query.order_by(TipoExamen.nombre).all()

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

def get_historial_paciente(db: Session, id_paciente: int) -> list[ExamenRealizado]:
    from app.models.cita import Cita
    return(
        db.query(ExamenRealizado)
        .join(Cita, ExamenRealizado.id_cita == Cita.id_cita)
        .filter(Cita.id_paciente == id_paciente)
        .order_by(ExamenRealizado.created_at.desc())
        .all()
    )

def create_tipo_examen(
    db: Session,
    nombre: str,
    precio: int,
    referencia: str | None = None,
    tipo_muestra: str | None = None,
    tecnica_utilizada: str | None = None,
    ) -> TipoExamen:
    tipo_examen = TipoExamen(
        nombre = nombre,
        precio = precio,
        referencia = referencia,
        tipo_muestra = tipo_muestra,
        tecnica_utilizada = tecnica_utilizada,
        activo = True,
    )
    db.add(tipo_examen)
    db.commit()
    db.refresh(tipo_examen)
    return tipo_examen

def update_tipo_examen(db: Session, id_tipo_examen: int, **campos) -> TipoExamen | None:
    tipo_examen = db.query(TipoExamen).filter(
        TipoExamen.id_tipo_examen == id_tipo_examen
    ).first()
    if tipo_examen is None:
        return None

    for campo, valor in campos.items():
        if hasattr(tipo_examen, campo):
            setattr(tipo_examen, campo, valor)

    db.commit()
    db.refresh(tipo_examen)
    return tipo_examen

def deactivate_tipo_examen(db: Session, id_tipo_examen: int)-> TipoExamen | None:
    tipo_examen = db.query(TipoExamen).filter(
        TipoExamen.id_tipo_examen == id_tipo_examen
    ).first()
    if tipo_examen is None:
        return None

    tipo_examen.activo = False
    db.commit()
    db.refresh(tipo_examen)
    return tipo_examen

def reactivate_tipo_examen(db: Session, id_tipo_examen: int) -> TipoExamen | None:
    tipo_examen = db.query(TipoExamen).filter(
        TipoExamen.id_tipo_examen == id_tipo_examen
    ).first()
    if tipo_examen is None:
        return None

    tipo_examen.activo = True
    db.commit()
    db.refresh(tipo_examen)
    return tipo_examen