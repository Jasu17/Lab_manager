from PySide6.QtWidgets import QLabel, QTabWidget
from app.ui.widgets.tipo_examen_widget import TipoExamenWidget
from app.ui.widgets.usuario_widget import UsuarioWidget
from app.ui.windows.base_role_windows import BaseRoleWindow

class AdminWindow(BaseRoleWindow):
    def __init__(self, usuario, roles):
        super().__init__(usuario, roles)
        self.setWindowTitle("Lab Manager - Administrador")
        self.setFixedSize(900, 600)

        self.usuario_widget = UsuarioWidget()
        self.tipo_examen_widget = TipoExamenWidget()

        tabs = QTabWidget()
        tabs.addTab(self.usuario_widget, "Usuarios")
        tabs.addTab(self.tipo_examen_widget, "Exámenes")

        self.add_content(QLabel(f"Panel de Administrador - {usuario['nombre']}"))
        self.add_content(tabs)