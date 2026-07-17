from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from app.ui.widgets.agenda_widget import AgendaWidget
from app.ui.widgets.cita_widget import CitaWidget


class RecepcionistaWindow(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Lab Manager - Recepcionista")
        self.setFixedSize(900, 600)

        self.agenda_widget = AgendaWidget()
        self.cita_widget = CitaWidget(usuario)

        tabs = QTabWidget()
        tabs.addTab(self.agenda_widget, "Agenda")
        tabs.addTab(self.cita_widget, "Nueva Cita")

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Panel de Recepcionista - {usuario['nombre']}"))
        layout.addWidget(tabs)
        self.setLayout(layout)