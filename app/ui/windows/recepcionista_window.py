from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from app.ui.widgets.agenda_widget import AgendaWidget
from app.ui.widgets.cita_widget import CitaWidget
from app.ui.widgets.paciente_widget import PacienteWidget

class RecepcionistaWindow(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Lab Manager - Recepcionista")
        self.setFixedSize(900, 600)

        self.agenda_widget = AgendaWidget()
        self.cita_widget = CitaWidget(usuario)
        self.paciente_widget = PacienteWidget()

        tabs = QTabWidget()
        tabs.addTab(self.agenda_widget, "Agenda")
        tabs.addTab(self.cita_widget, "Nueva Cita")
        tabs.addTab(self.paciente_widget, "Pacientes")

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Panel de Recepcionista - {usuario['nombre']}"))
        layout.addWidget(tabs)
        self.setLayout(layout)