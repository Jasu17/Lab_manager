from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal

class RoleSelectorWindow(QWidget):
    role_selected = Signal(object)

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Lab Manager - Seleccionar rol")
        self.setFixedSize(280, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Bienbenido/a, {usuario.nombre}"))
        layout.addWidget(QLabel("Seleccione un rol con el que desea trabajar: "))

        for rol in usuario.roles:
            btn = QPushButton(rol.nombre)
            btn.clicked.connect(lambda checked=False, r=rol: self.role_selected.emit(r))
            layout.addWidget(btn)

        self.setLayout(layout)
