"""
Servicio de autenticación.
Maneja login (validacion de credenciales) y hashing de contraseñas.
Los usuarios se autentican con identifiaccion + contraseña (RF13)  
"""

import bcrypt
from sqlalchemy.orm import Session
from app.models.usuario import Usuario


def hash_password(password: str) -> str:
    """Genera el hash de una contraseña en texto plano."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

def autenticate(db: Session, identificacion: str, password: str) -> Usuario | None:
    """
    Intenta autenticar un usuario por identificacion y contraseña.
    Retorna el Usuario si las credenciales son validas y está activo,
    o None en caso contrario 
    """
    usuario = (
        db.query(Usuario)
        .filter(Usuario.identificacion == identificacion, Usuario.activo==True)
        .first()
    )  
    
    if usuario is None:
        return None

    if not verify_password(password, usuario.password_hash):
        return None
    
    return usuario
