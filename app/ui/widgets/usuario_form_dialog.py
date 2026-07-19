from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout,
    QLabel, QCheckBox, QWidget, QHBoxLayout
)
from app.database.session import SessionLocal
from app.services.usuario_service import create_usuario, get_all_roles

class UsuarioFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear nuevo usuario")
        self.setFixedSize(320, 320)
        self.usuario_creado = None

        self.input_identificacion = QLineEdit()
        self.input_nombre = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.label_error = QLabel("")
        self.label_error.setStyleSheet("color: red;")

        form_layout = QFormLayout()
        form_layout.addRow("Identificación:", self.input_identificacion)
        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Contraseña:", self.input_password)

        self.checkboxes_roles = {}
        roles_widget = QWidget()
        roles_layout = QVBoxLayout()
        roles_layout.addWidget(QLabel("Roles:"))

        db = SessionLocal()
        try:
            roles = get_all_roles(db)
            self._roles_cache = [(r.id_rol, r.nombre) for r in roles]
        finally:
            db.close()

        for id_rol, nombre_rol in self._roles_cache:
            checkbox = QCheckBox(nombre_rol)
            self.checkboxes_roles[id_rol] = checkbox
            roles_layout.addWidget(checkbox)
        roles_widget.setLayout(roles_layout)

        btn_guardar = QPushButton("Crear Usuario")
        btn_guardar.clicked.connect(self.handle_guardar)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(roles_widget)
        layout.addWidget(self.label_error)
        layout.addWidget(btn_guardar)
        self.setLayout(layout)

    def handle_guardar(self):
        identificacion = self.input_identificacion.text().strip()
        nombre = self.input_nombre.text().strip()
        password = self.input_password.text()

        if not identificacion or not nombre or not password:
            self.label_error.setText("Todos los campos son obligatorios.")
            return

        roles_seleccionados = [
            id_rol for id_rol, checkbox in self.checkboxes_roles.items()
            if checkbox.isChecked()
        ]

        db = SessionLocal()
        try:
            usuario = create_usuario(
                db, identificacion=identificacion, nombre=nombre,
                password=password, roles = roles_seleccionados
            )
            self.usuario_creado = {
                "id_usuario": usuario.id_usuario,
                "nombre": usuario.nombre,
                "identificacion": usuario.identificacion,
            }
        except Exception as e:
            self.label_error.setText(f"Error al cargar {e}")
            return
        finally:
            db.close()

        self.accept()