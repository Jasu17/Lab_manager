from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from app.ui.widgets.usuario_widget import UsuarioWidget

class AdminWindow(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Lam Manager - Administrador")
        self.setFixedSize(900, 600)

        self.usuario_widget = UsuarioWidget()

        tabs = QTabWidget()
        tabs.addTab(self.usuario_widget, "Usuarios")

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Panel de Administrador - {usuario['nombre']}"))
        layout.addWidget(tabs)
        self.setLayout(layout)