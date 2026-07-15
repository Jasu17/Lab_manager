from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class BacteriologaWindow(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Lab Manager - Bacteriologa")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Panel de bacteriologa - {usuario.nombre}"))
        self.setLayout(layout)