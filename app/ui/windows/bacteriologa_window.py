from PySide6.QtWidgets import QTabWidget, QLabel
from app.ui.widgets.bacteriologa_widget import BacteriologaWidget
from app.ui.widgets.historial_widget import HistorialWidget
from app.ui.windows.base_role_windows import BaseRoleWindow


class BacteriologaWindow(BaseRoleWindow):
    def __init__(self, usuario, roles):
        super().__init__(usuario, roles)
        self.setWindowTitle("Lab Manager - Bacterióloga")
        self.setFixedSize(900, 600)

        self.bacteriologa_widget = BacteriologaWidget(usuario)
        self.historial_widget = HistorialWidget()

        tabs = QTabWidget()
        tabs.addTab(self.bacteriologa_widget, "Agenda y Resultados")
        tabs.addTab(self.historial_widget, "Historia Clínica")

        self.add_content(QLabel(f"Panel de Bacterióloga - {usuario['nombre']}"))
        self.add_content(tabs)