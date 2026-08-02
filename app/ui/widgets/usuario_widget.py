from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QCheckBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
import shutil
import os
from app.database.session import SessionLocal
from app.services.usuario_service import(
    get_all_usuarios, get_usuario_by_id, update_usuario, change_password,
    deactivate_usuario, reactivate_usuario, add_rol, remove_rol, get_all_roles
)
from app.ui.widgets.usuario_form_dialog import UsuarioFormDialog

USUARIOS_COLUMNS = ["Identificacion", "Nombre", "Roles", "Activo"]

class UsuarioWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.id_usuario_actual = None
        self._roles_cache = []

        btn_crear = QPushButton("Crear Usuario")
        btn_crear.clicked.connect(self.handle_crear_usuario)

        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(len(USUARIOS_COLUMNS))
        self.tabla_usuarios.setHorizontalHeaderLabels(USUARIOS_COLUMNS)
        self.tabla_usuarios.horizontalHeader().setStretchLastSection(True)
        self.tabla_usuarios.itemSelectionChanged.connect(self.handle_seleccionar_usuario)

        # -- Formulario de Edición
        self.input_identificacion = QLineEdit()
        self.input_nombre = QLineEdit()
        self.input_nueva_password = QLineEdit()
        self.input_nueva_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_nueva_password.setPlaceholderText("Dejar vacío para no cambiar")
        self.input_registro_profesional = QLineEdit()
        
        self.label_firma_actual = QLabel("Sin firma cargada...")
        self.btn_seleccionar_firma = QPushButton("Cargar firma (imagen)")
        self.btn_seleccionar_firma.clicked.connect(self.handle_seleccionar_firma)
        self._ruta_firma_nueva = None
        
        self.checkboxes_roles_widget = QWidget()
        self.checkboxes_roles_layout = QVBoxLayout()
        self.checkboxes_roles_widget.setLayout(self.checkboxes_roles_layout)
        self.checkboxes_roles = {}

        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.setEnabled(False)
        self.btn_guardar.clicked.connect(self.handle_guardar)

        self.btn_toggle_activo = QPushButton("Desactivar / Reactivar")
        self.btn_toggle_activo.setEnabled(False)
        self.btn_toggle_activo.clicked.connect(self.handle_toggle_activo)

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Identificación:"))
        form_layout.addWidget(self.input_identificacion)
        form_layout.addWidget(QLabel("Nombre:"))
        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(QLabel("Nueva contraseña:"))
        form_layout.addWidget(self.input_nueva_password)
        form_layout.addWidget(QLabel("Registro profesional (opcional):"))
        form_layout.addWidget(self.input_registro_profesional)
        form_layout.addWidget(QLabel("Firma Digital (opcional):"))
        form_layout.addWidget(self.label_firma_actual)
        form_layout.addWidget(self.btn_seleccionar_firma)
        form_layout.addWidget(QLabel("Roles:"))
        form_layout.addWidget(self.checkboxes_roles_widget)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.btn_guardar)
        botones_layout.addWidget(self.btn_toggle_activo)

        layout = QVBoxLayout()
        layout.addWidget(btn_crear)
        layout.addWidget(self.tabla_usuarios)
        layout.addLayout(form_layout)
        layout.addLayout(botones_layout)
        self.setLayout(layout)

        self._cargar_roles_disponibles()
        self.refresh_usuarios()

    def _cargar_roles_disponibles(self):
        db = SessionLocal()
        try:
            roles = get_all_roles(db)
            self._roles_cache = [(r.id_rol, r.nombre) for r in roles]
        finally:
            db.close()

        for id_rol, nombre_rol in self._roles_cache:
            checkbox = QCheckBox(nombre_rol)
            self.checkboxes_roles[id_rol] = checkbox
            self.checkboxes_roles_layout.addWidget(checkbox)

    def refresh_usuarios(self):
        db = SessionLocal()
        try:
            usuarios = get_all_usuarios(db)
            filas = [
                {
                    "id_usuario":u.id_usuario,
                    "identificacion":u.identificacion,
                    "nombre":u.nombre,
                    "roles": ", ".join(r.nombre for r in u.roles),
                    "activo":u.activo
                }
                for u in usuarios
            ]
        finally:
            db.close()
        
        self.tabla_usuarios.setRowCount(len(filas))
        for row_idx, f in enumerate(filas):
            item_id = QTableWidgetItem(f["identificacion"])
            item_id.setData(Qt.ItemDataRole.UserRole, f["id_usuario"])
            self.tabla_usuarios.setItem(row_idx, 0, item_id)
            self.tabla_usuarios.setItem(row_idx, 1, QTableWidgetItem(f["nombre"]))
            self.tabla_usuarios.setItem(row_idx, 2, QTableWidgetItem(f["roles"]))
            self.tabla_usuarios.setItem(row_idx, 3, QTableWidgetItem("Sí" if f["activo"] else "No"))
    
    def handle_seleccionar_usuario(self):
        fila = self.tabla_usuarios.currentRow()
        if fila < 0:
            return
        
        id_usuario = self.tabla_usuarios.item(fila, 0).data(Qt.ItemDataRole.UserRole)

        db = SessionLocal()
        try:
            usuario = get_usuario_by_id(db, id_usuario)
            if usuario is None:
                return

            self.id_usuario_actual = usuario.id_usuario
            self.input_identificacion.setText(usuario.identificacion)
            self.input_nombre.setText(usuario.nombre)
            self.input_nueva_password.clear()
            self.input_registro_profesional.setText(usuario.registro_profesional or "")
            self._ruta_firma_nueva = None
            if usuario.firma_imagen:
                self.label_firma_actual.setText(f"Firma cargada: {os.path.basename(usuario.firma_imagen)}")
            else:
                self.label_firma_actual.setText("Sin firma cargada.")

            roles_actuales = {r.id_rol for r in usuario.roles}
            for id_rol, checkbox in self.checkboxes_roles.items():
                checkbox.setChecked(id_rol in roles_actuales)
            
        finally:
            db.close()

        self.btn_guardar.setEnabled(True)
        self.btn_toggle_activo.setEnabled(True)

    def handle_guardar(self):
        if self.id_usuario_actual is None:
            return

        campos_actualizar = {
            "identificacion": self.input_identificacion.text().strip(),
            "nombre": self.input_nombre.text().strip(),
            "registro_profesional": self.input_registro_profesional.text().strip() or None,
        }

        if self._ruta_firma_nueva:
            carpeta_firmas = os.path.join("app", "resources", "firmas")
            os.makedirs(carpeta_firmas, exist_ok=True)
            extension = os.path.splitext(self._ruta_firma_nueva)[1]
            nombre_archivo = f"usuario_{self.id_usuario_actual}{extension}"
            ruta_destino = os.path.join(carpeta_firmas, nombre_archivo)
            shutil.copy(self._ruta_firma_nueva, ruta_destino)
            campos_actualizar["firma_imagen"] = ruta_destino

        db = SessionLocal()
        try:
            update_usuario(db, self.id_usuario_actual, **campos_actualizar)

            nueva_password = self.input_nueva_password.text()
            if nueva_password:
                change_password(db, self.id_usuario_actual, nueva_password)

            usuario_actual = get_usuario_by_id(db, self.id_usuario_actual)
            roles_actuales = {r.id_rol for r in usuario_actual.roles}
            roles_marcados = {
                id_rol for id_rol, checkbox in self.checkboxes_roles.items()
                if checkbox.isChecked()
            }

            for id_rol in roles_marcados - roles_actuales:
                add_rol(db, self.id_usuario_actual, id_rol)
            for id_rol in roles_actuales - roles_marcados:
                remove_rol(db, self.id_usuario_actual, id_rol)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
            return
        finally:
            db.close()

        QMessageBox.information(self, "Exito", "Usuario actualizado correctamente.")
        self.input_nueva_password.clear()
        self.refresh_usuarios()

    def handle_toggle_activo(self):
        if self.id_usuario_actual is None:
            return

        db = SessionLocal()
        try:
            usuario = get_usuario_by_id(db, self.id_usuario_actual)
            if usuario.activo:
                deactivate_usuario(db, self.id_usuario_actual)
            else:
                reactivate_usuario(db, self.id_usuario_actual)
        finally:
            db.close()

        self.refresh_usuarios()

    def handle_seleccionar_firma(self):
        ruta_origen, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen de firma", "", "Imágenes (*.png *.jpg *.jpeg)"
        )
        if not ruta_origen:
            return

        self._ruta_firma_nueva = ruta_origen
        self.label_firma_actual.setText(f"Nueva firma seleccionada: {os.path.basename(ruta_origen)}")

    def handle_crear_usuario(self):
        dialog = UsuarioFormDialog(self)
        if dialog.exec() == UsuarioFormDialog.DialogCode.Accepted:
            self.refresh_usuarios()