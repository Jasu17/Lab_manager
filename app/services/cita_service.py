from datetime import date, time
from sqlalchemy.orm import Session
from app.models.cita import Cita, EstadoCita
from app.models.examen import ExamenRealizado, EstadoExamen, TipoExamen

def create_cita(
    db: Session,
    id_paciente: int,
    id_usuario: int,
    fecha: date,
    hora: time,
    id_tipos_examen: list[list],
    localidad: str | None = None 
) -> Cita:
    
    if not id_tipos_examen:
        raise ValueError("La cita debe tener al menos un examen asociado")

    cita = Cita(
        id_paciente=id_paciente,
        id_usuario=id_usuario,
        fecha=fecha,
        hora=hora,
        localidad=localidad,
        estado=EstadoCita.AGENDADA,
    )
    db.add(cita)
    db.flush() # Asigna id_cita sin cerrar la transacción

    for id_tipo_examen in id_tipos_examen:
        tipo_examen = db.query(TipoExamen).filter(
            TipoExamen.id_tipo_examen == id_tipo_examen
        ).first()
        if tipo_examen is None:
            raise ValueError(f"El tipo de examen {id_tipo_examen} No existe")
        
        examen = ExamenRealizado(
            id_cita=cita.id_cita,
            id_tipo_examen=id_tipo_examen,
            precio_cobrado=tipo_examen.precio,
            estado=EstadoExamen.PENDIENTE,
        )
        db.add(examen)

    db.commit()
    db.refresh(cita)
    return cita

def get_cita_by_id(db: Session, id_cita: int) -> Cita | None:
    return db.query(Cita).filter(Cita.id_cita == id_cita).first()

def get_agenda(db: Session, estado: EstadoCita | None=None) -> list[Cita]:
    query = db.query(Cita)
    if estado is not None:
        query = query.filter(Cita.estado == estado)

    return query.order_by(Cita.fecha, Cita.hora).all()

def update_estado_cita(db: Session, id_cita:int, nuevo_estado: EstadoCita) -> Cita | None:
    cita = get_cita_by_id(db, id_cita)
    if cita is None:
        return None

    cita.estado = nuevo_estado
    db.commit()
    db.refresh(cita)
    return cita

def cancel_cita(db: Session, id_cita: int) -> Cita | None:
    return update_estado_cita(db, id_cita, EstadoCita.CANCELADA)