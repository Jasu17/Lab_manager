from PySide6.QtWidgets import QLabel, QTabWidget
from app.ui.widgets.agenda_widget import AgendaWidget
from app.ui.widgets.cita_widget import CitaWidget
from app.ui.widgets.paciente_widget import PacienteWidget
from app.ui.windows.base_role_windows import BaseRoleWindow

class RecepcionistaWindow(BaseRoleWindow):
    def __init__(self, usuario, roles):
        super().__init__(usuario, roles)
        self.setWindowTitle("Lab Manager - Recepcionista")
        self.setFixedSize(900, 600)

        self.agenda_widget = AgendaWidget()
        self.cita_widget = CitaWidget(usuario)
        self.paciente_widget = PacienteWidget()

        tabs = QTabWidget()
        tabs.addTab(self.agenda_widget, "Agenda")
        tabs.addTab(self.cita_widget, "Nueva Cita")
        tabs.addTab(self.paciente_widget, "Pacientes")

        self.add_content(QLabel(f"Panel de Recepcionista - {usuario['nombre']}"))
        self.add_content(tabs)