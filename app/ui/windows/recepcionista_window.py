from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class RecepcionistaWindow(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Lab Manager - Recepcionista")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Panel de recepcionista - {usuario.nombre}"))
        self.setLayout(layout)