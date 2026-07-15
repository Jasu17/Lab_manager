import app.models
from app.database.session import SessionLocal
from app.models.usuario import Rol, Usuario
from app.services.auth_service import hash_password

ROLES_BASE = ["Administrador", "Recepcionista", "Bacteriologa"]

def seed():
    db = SessionLocal()
    try:
        #Crear roles bases si no existen
        roles_creados = {}
        for nombre_rol in ROLES_BASE:
            rol = db.query(Rol).filter(Rol.nombre == nombre_rol).first()
            if rol is None:
                rol = Rol(nombre = nombre_rol)
                db.add(rol)
                db.flush()
                print(f"Rol creado: {nombre_rol}")
            else:
                print(f"Rol ya existe: {nombre_rol}")
            roles_creados[nombre_rol] = rol

        # Crear usuario admin si no existe
        admin = db.query(Usuario).filter(Usuario.identificacion == "admin").first()
        if admin is None:
            admin = Usuario(
                identificacion="admin",
                nombre="Administrador",
                password_hash=hash_password("admin123"),
                activo=True,
            )
            admin.roles.append(roles_creados["Administrador"])
            db.add(admin)
            print("Usuario admin creado (Identificacion: admin, password: admin123)")
        else:
            print("Usuario admin ya existe, no se modifica")
        
        db.commit()
        print("Seed completado")

    finally:
        db.close()


if __name__ == "__main__":
    seed()