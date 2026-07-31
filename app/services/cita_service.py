from datetime import date, datetime, time, timedelta
from sqlalchemy.orm import Session
from app.models.cita import Cita, EstadoCita
from app.models.examen import ExamenRealizado, EstadoExamen, TipoExamen

def _actualizar_estados_por_tiempo (db :Session) -> None:
    limite = datetime.now() + timedelta(hours=24)
    citas_agendadas = db.query(Cita).filter(Cita.estado == EstadoCita.AGENDADA).all()

    cambios = False
    for cita in citas_agendadas:
        fecha_hora_cita = datetime.combine(cita.fecha, cita.hora)
        if fecha_hora_cita <= limite:
            cita.estado = EstadoCita.EN_ESPERA
            cambios = True

    if cambios:
        db.commit()

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

    fecha_hora_cita = datetime.combine(fecha, hora)
    ahora = datetime.now()

    if fecha_hora_cita < ahora:
        raise ValueError(
            "No se pueden agendar citas en el pasado."
            "Puede usar la fecha y hora actual"
        )

    if fecha_hora_cita - ahora > timedelta(hours=24):
        estado_inicial = EstadoCita.AGENDADA
    else:
        estado_inicial = EstadoCita.EN_ESPERA

    cita = Cita(
        id_paciente=id_paciente,
        id_usuario=id_usuario,
        fecha=fecha,
        hora=hora,
        localidad=localidad,
        estado=estado_inicial,
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
    _actualizar_estados_por_tiempo(db)
    query = db.query(Cita)
    if estado is not None:
        query = query.filter(Cita.estado == estado)

    return query.order_by(Cita.fecha, Cita.hora).all()

def get_agenda_bacteriologa(db: Session) -> list[Cita]:
    _actualizar_estados_por_tiempo(db)
    return (
        db.query(Cita).filter(
            Cita.estado.in_([EstadoCita.EN_ESPERA, EstadoCita.EN_ATENCION]))
            .order_by(Cita.fecha, Cita.hora)
            .all()
    )

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

def add_examen_to_cita (db: Session, id_cita: int, id_tipo_examen: int)-> ExamenRealizado | None:
    cita = get_cita_by_id(db, id_cita)
    if cita is None:
        return None

    if cita.estado not in (EstadoCita.AGENDADA, EstadoCita.EN_ESPERA, EstadoCita.EN_ATENCION):
        raise ValueError("No se pueden editar exámenes de una cita finalizada o cancelada.")

    tipo_examen = db.query(TipoExamen).filter(
        TipoExamen.id_tipo_examen == id_tipo_examen
    ).first()
    if tipo_examen is None:
        raise ValueError(f"TipoExamen {id_tipo_examen} no existe.")

    examen = ExamenRealizado(
        id_cita=id_cita,
        id_tipo_examen=id_tipo_examen,
        precio_cobrado=tipo_examen.precio,
        estado=EstadoExamen.PENDIENTE,
    )
    db.add(examen)
    db.flush()
    return examen

def remove_examen_from_cita(db: Session, id_examen:int, id_cita: int, examenes_finales_count: int)->bool:
    examen = db.query(ExamenRealizado).filter(
        ExamenRealizado.id_examen == id_examen
    ).first()
    if examen is None:
        return False

    cita = get_cita_by_id(db, id_cita)
    if cita.estado not in (EstadoCita.AGENDADA, EstadoCita.EN_ATENCION, EstadoCita.EN_ESPERA):
        raise ValueError("No se pueden editar exámenes de una cita finalizada o cancelada")

    if examenes_finales_count <= 1:
        raise ValueError("La cita debe tener al menos un examen; No se puede eliminar el último")

    db.delete(examen)
    db.flush()
    return True