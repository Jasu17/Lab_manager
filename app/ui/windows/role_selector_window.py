from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal

class RoleSelectorWindow(QWidget):
    role_selected = Signal(object) # Emite el objeto del Rol elegido

    def __init__(self, usuario_dict: dict, roles: list):
        super().__init__()
        self.setWindowTitle("Lab Manager - Seleccionar rol")
        self.setFixedSize(280, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Bienvenido/a, {usuario_dict['nombre']}"))
        layout.addWidget(QLabel("Seleccione un rol con el que desea trabajar: "))

        for rol in roles:
            btn = QPushButton(rol.nombre)
            btn.clicked.connect(lambda checked=False, r=rol: self.role_selected.emit(r))
            layout.addWidget(btn)

        self.setLayout(layout)
