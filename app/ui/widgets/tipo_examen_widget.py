from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)

from app.database.session import SessionLocal
from app.services.examen_service import (
    create_tipo_examen,
    deactivate_tipo_examen,
    get_all_tipos_examen,
    reactivate_tipo_examen,
    update_tipo_examen
)

TIPOS_EXAMEN_COLUMNS = ["Nombre", "Referencia", "Precio", "Tipo Muestra", "Técnica", "Activo"]

class TipoExamenWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.id_tipo_examen_actual = None

        # -- Tabla de catálogo
        self.tabla_examenes = QTableWidget()
        self.tabla_examenes.setColumnCount(len(TIPOS_EXAMEN_COLUMNS))
        self.tabla_examenes.setHorizontalHeaderLabels(TIPOS_EXAMEN_COLUMNS)
        self.tabla_examenes.horizontalHeader().setStretchLastSection(True)
        self.tabla_examenes.itemSelectionChanged.connect(self.handle_seleccionar_examen)

        # -- Formulario
        self.input_nombre = QLineEdit()
        self.input_referencia = QLineEdit()
        self.input_precio = QSpinBox()
        self.input_precio.setRange(0, 10_000_000)
        self.input_precio.setSingleStep(1000)
        self.input_tipo_muestra = QLineEdit()
        self.input_tecnica = QLineEdit()

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Nombre:"))
        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(QLabel("Referencia:"))
        form_layout.addWidget(self.input_referencia)
        form_layout.addWidget(QLabel("Precio:"))
        form_layout.addWidget(self.input_precio)
        form_layout.addWidget(QLabel("Tipo de muestra:"))
        form_layout.addWidget(self.input_tipo_muestra)
        form_layout.addWidget(QLabel("Técnica Utilizada:"))
        form_layout.addWidget(self.input_tecnica)

        self.btn_crear = QPushButton("Crear Nuevo")
        self.btn_crear.clicked.connect(self.handle_crear)

        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.setEnabled(False)
        self.btn_guardar.clicked.connect(self.handle_guardar)

        self.btn_toggle_activo = QPushButton("Desactivar / Reactivar")
        self.btn_toggle_activo.setEnabled(False)
        self.btn_toggle_activo.clicked.connect(self.handle_toggle_activo)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.btn_crear)
        botones_layout.addWidget(self.btn_guardar)
        botones_layout.addWidget(self.btn_toggle_activo)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Catálogo de examenes"))
        layout.addWidget(self.tabla_examenes)
        layout.addLayout(form_layout)
        layout.addLayout(botones_layout)
        self.setLayout(layout)

        self.refresh_examenes()

    def refresh_examenes(self):
        db = SessionLocal()
        try:
            tipos = get_all_tipos_examen(db, solo_activos=False)
            self._examenes_cache = [
                {
                    "id_tipo_examen": t.id_tipo_examen,
                    "nombre": t.nombre,
                    "referencia": t.referencia,
                    "precio": t.precio,
                    "tipo_muestra": t.tipo_muestra,
                    "tecnica_utilizada": t.tecnica_utilizada,
                    "activo": t.activo
                }
                for t in tipos
            ]
        finally:
            db.close()

        self.tabla_examenes.setRowCount(len(self._examenes_cache))
        for row_idx, t in enumerate(self._examenes_cache):
            item_nombre = QTableWidgetItem(t["nombre"])
            item_nombre.setData(Qt.ItemDataRole.UserRole, row_idx)
            self.tabla_examenes.setItem(row_idx, 0, item_nombre)
            self.tabla_examenes.setItem(row_idx, 1, QTableWidgetItem(t["referencia"]))
            self.tabla_examenes.setItem(row_idx, 2, QTableWidgetItem(str(t["precio"])))
            self.tabla_examenes.setItem(row_idx, 3, QTableWidgetItem(t["tipo_muestra"]))
            self.tabla_examenes.setItem(row_idx, 4, QTableWidgetItem(t["tecnica_utilizada"]))
            self.tabla_examenes.setItem(row_idx, 5, QTableWidgetItem("Si" if t["activo"] else "No"))
            
        self._limpiar_formulario()

    def handle_seleccionar_examen(self):
        fila = self.tabla_examenes.currentRow()
        if fila < 0:
            return

        row_idx = self.tabla_examenes.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        t = self._examenes_cache[row_idx]

        self.id_tipo_examen_actual = t["id_tipo_examen"]
        self.input_nombre.setText(t["nombre"])
        self.input_referencia.setText(t["referencia"] or "")
        self.input_precio.setValue(t["precio"])
        self.input_tipo_muestra.setText(t["tipo_muestra"] or "")
        self.input_tecnica.setText(t["tecnica_utilizada"] or "")

        self.btn_guardar.setEnabled(True)
        self.btn_toggle_activo.setEnabled(True)

    def handle_crear(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Falta nombre", "El nombre del examen es obligatorio")
            return

        db = SessionLocal()
        try:
            create_tipo_examen(
                db,
                nombre=nombre,
                precio=self.input_precio.value(),
                referencia=self.input_referencia.text().strip() or None,
                tipo_muestra=self.input_tipo_muestra.text().strip() or None,
                tecnica_utilizada=self.input_tecnica.text().strip() or None,
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear: {e}")
            return    
        finally:
            db.close()

        QMessageBox.information(self, "Éxito", "Examen creado correctamente")
        self.refresh_examenes()

    def handle_guardar(self):
        if self.id_tipo_examen_actual is None:
            return
        
        db = SessionLocal()
        try:
            update_tipo_examen(
                db, self.id_tipo_examen_actual,
                nombre=self.input_nombre.text().strip(),
                precio=self.input_precio.value(),
                referencia=self.input_referencia.text().strip() or None,
                tipo_muestra=self.input_tipo_muestra.text().strip() or None,
                tecnica_utilizada=self.input_tecnica.text().strip() or None,
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
            return
        finally:
            db.close()

        QMessageBox.information(self, "Exito", "Examen Guardado correctamente")
        self.refresh_examenes

    def handle_toggle_activo(self):
        if self.id_tipo_examen_actual is None:
            return

        db = SessionLocal()
        try:
            tipo_examen = next(
                t for t in self._examenes_cache
                if t["id_tipo_examen"] == self.id_tipo_examen_actual
            )
            if tipo_examen["activo"]:
                deactivate_tipo_examen(db, self.id_tipo_examen_actual)
            else:
                reactivate_tipo_examen(db, self.id_tipo_examen_actual)

        finally:
            db.close()

        self.refresh_examenes()

    def _limpiar_formulario(self):
        self.id_tipo_examen_actual = None
        self.input_nombre.clear()
        self.input_referencia.clear()
        self.input_precio.setValue(0)
        self.input_tipo_muestra.clear()
        self.input_tecnica.clear()
        self.btn_guardar.setEnabled(False)
        self.btn_toggle_activo.setEnabled(False)