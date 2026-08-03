from PySide6.QtCore import Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

class BaseRoleWindow(QWidget):
    cambiar_rol_solicitado = Signal(object, object) # (usuario_dict, roles)

    def __init__(self, usuario: dict, roles: list):
        super().__init__()
        self.usuario = usuario
        self.roles = roles

        self._barra_superior = QHBoxLayout()
        if len(roles) > 1:
            btn_cambiar_rol = QPushButton("Cambiar de rol")
            btn_cambiar_rol.clicked.connect(self._handle_cambiar_rol)
            self._barra_superior.addStretch()
            self._barra_superior.addWidget(btn_cambiar_rol)

            shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
            shortcut.activated.connect(self._handle_cambiar_rol)

        self._layout_principal = QVBoxLayout()
        self._layout_principal.addLayout(self._barra_superior)
        super().setLayout(self._layout_principal)

    def _handle_cambiar_rol(self):
        self.cambiar_rol_solicitado.emit(self.usuario, self.roles)

    def add_content(self, widget: QWidget):
        """
        Agrega el contenido específico de cada ventana de rol debajo
        de la barra superior. Las subclases deben usar este método
        en lugar de self.setLayout() directamente
        """
        self._layout_principal.addWidget(widget)