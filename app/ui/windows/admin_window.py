from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class AdminWindow(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Lab Manager - Administrador")
        self.setFixedSize(600,400)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Panel de administrador - {usuario['nombre']}"))
        self.setLayout(layout)