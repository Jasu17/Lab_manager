from sqlalchemy.orm import Session
from app.models.usuario import Usuario, Rol
from app.services.auth_service import hash_password

def create_usuario(
    db: Session,
    identificacion: str,
    nombre: str,
    password: str,
    roles: list[int] | None=None,
) -> Usuario:

    usuario = Usuario(
        identificacion=identificacion,
        nombre=nombre,
        password=hash_password(password),
        activo=True,
    )

    if roles:
        usuario.roles = db.query(Rol).filter(Rol.id_rol.in_(roles)).all()

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def get_usuario_by_id(db: Session, id_usuario: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

def get_all_usuarios(db: Session, solo_activos: bool=False) -> list[Usuario]:
    query = db.query(Usuario)
    if solo_activos:
        query = query.filter(Usuario.activo == True)
    return query.all()

def update_usuario(db: Session, id_usuario: int, **campos) -> Usuario | None:
    usuario = get_usuario_by_id(id_usuario)
    if usuario is None:
        return None

    campos.pop("passowrd", None) # La contraseña no se actualiza aquí
    for campo, valor in campos.items():
        if hasattr(usuario, campo):
            setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario

def change_password(db: Session, id_usuario: int, new_password: str) -> Usuario | None:
    usuario = get_usuario_by_id(db, id_usuario)
    if usuario is None:
        return None

    usuario.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(usuario)
    return usuario

def deactivate_usuario(db: Session, id_usuario: int) -> Usuario | None:
    usuario = get_usuario_by_id(db, id_usuario)
    if usuario is None:
        return None
    
    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario

def reactivate_usuario(db: Session, id_usuario: int) -> Usuario | None:
    usuario = get_usuario_by_id(db, id_usuario)
    if usuario is None:
        return None

    usuario.activo = True
    db.commit()
    db.refresh(usuario)
    return usuario

def add_rol(db: Session, id_usuario: int, id_rol: int) -> Usuario | None:
    usuario = get_usuario_by_id(db, id_usuario)
    rol = db.query(Rol).filter(Rol.id_rol == id_rol).first()

    if usuario is None or rol is None:
        return None

    if rol not in usuario.roles:
        usuario.roles.append(rol)
        db.commit()
        db.refresh(usuario)

    return usuario

def remove_rol(db: Session, id_usuario: int, id_rol: int) -> Usuario | None:
    usuario = get_usuario_by_id(db, id_usuario)
    rol = db.query(Rol).filter(Rol.id_rol == id_rol).first()

    if usuario is None or rol is None:
        return None

    if rol in usuario.roles:
        usuario.roles.remove(rol)
        db.commit()
        db.refresh(usuario)
    
    return usuario