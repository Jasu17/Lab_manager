import sys
from PySide6.QtWidgets import QApplication
from app.ui.windows.login_window import LoginWindow
from app.ui.windows.role_selector_window import RoleSelectorWindow
from app.ui.windows.admin_window import AdminWindow
from app.ui.windows.recepcionista_window import RecepcionistaWindow
from app.ui.windows.bacteriologa_window import BacteriologaWindow

ROLE_WINDOW_MAP = {
    "Administrador": AdminWindow,
    "Recepcionista": RecepcionistaWindow,
    "Bacteriologa": BacteriologaWindow,
}

class AppController:
    def __init__(self):
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.handle_login_success)

        self.role_selector_window = None
        self.role_window = None

        self.login_window.show()

    def handle_login_success(self, usuario):
        self.login_window.close()

        usuario_dict = {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "identificacion": usuario.identificacion,
        }
        roles = list(usuario.roles)

        if len(roles) == 1:
            self.open_role_window(usuario_dict, roles, roles[0])
        else:
            self.mostrar_selector(usuario_dict, roles)

    def mostrar_selector(self, usuario_dict, roles):
        self.role_selector_window = RoleSelectorWindow(usuario_dict, roles)
        self.role_selector_window.role_selected.connect(
            lambda rol: self.open_role_window(usuario_dict, roles, rol)
        )
        self.role_selector_window.show()

    def open_role_window(self, usuario_dict, roles, rol):
        if self.role_selector_window is not None:
            self.role_selector_window.close()
        if self.role_window is not None:
            self.role_window.close()

        window_class = ROLE_WINDOW_MAP.get(rol.nombre)
        if window_class is None:
            raise ValueError(f"No hay ventana definida para el rol: {rol.nombre}")

        self.role_window = window_class(usuario_dict, roles)
        self.role_window.cambiar_rol_solicitado.connect(self.handle_cambiar_rol)
        self.role_window.show()

    def handle_cambiar_rol(self, usuario_dict, roles):
        self.role_window.close()
        self.mostrar_selector(usuario_dict, roles)

def main():
    app = QApplication(sys.argv)
    controller = AppController()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 