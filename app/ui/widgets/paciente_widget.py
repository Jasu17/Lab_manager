from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QComboBox,
    QSpinBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from app.ui.widgets.debounced_search import DebouncedSearch
from app.database.session import SessionLocal
from app.services.paciente_service import search_pacientes, update_paciente

TIPOS_ID = ["CC","TI","CE","PA"]
OPCIONES_SEXO = ["Masculino", "Femenino", "NB", "T"]
OPCIONES_ESTADO_CIVIL = ["Soltero/a", "Casado/a", "Unión libre", "Divorciado/a", "Viudo/a"]
RESULTADOS_COLUMNS = ["Nombre", "Tipo ID", "Identificación"]

class PacienteWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.id_paciente_actual = None

        # -- Busqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por nombre o identificaion...")
        self._debounced_search = DebouncedSearch(self.input_busqueda, self.handle_buscar)

        busqueda_layout = QHBoxLayout()
        busqueda_layout.addWidget(self.input_busqueda)

        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(len(RESULTADOS_COLUMNS))
        self.tabla_resultados.setHorizontalHeaderLabels(RESULTADOS_COLUMNS)
        self.tabla_resultados.horizontalHeader().setStretchLastSection(True)
        self.tabla_resultados.itemSelectionChanged.connect(self.handle_seleccionar_paciente)

        # -- Formulario de selección
        self.input_identificacion = QLineEdit()
        self.input_tipo_id = QComboBox()
        self.input_tipo_id.addItems(TIPOS_ID)
        self.input_nombre = QLineEdit()
        self.input_telefono = QLineEdit()
        self.input_fecha_nacimiento = QDateEdit()
        self.input_fecha_nacimiento.setCalendarPopup(True)
        self.input_fecha_nacimiento.setDate(QDate(2000, 1, 1))
        self.input_eps = QLineEdit()
        self.input_sexo = QComboBox()
        self.input_sexo.addItems(OPCIONES_SEXO)
        self.input_estado_civil = QComboBox()
        self.input_estado_civil.addItems(OPCIONES_ESTADO_CIVIL)
        self.input_hijos = QSpinBox()
        self.input_hijos.setRange(0, 30)
        self.input_estudios = QLineEdit()
        self.input_responsable = QLineEdit()
        self.input_ciudad = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow("Identificación:", self.input_identificacion)
        form_layout.addRow("Tipo ID:", self.input_tipo_id)
        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Teléfono:", self.input_telefono)
        form_layout.addRow("Fecha nacimiento:", self.input_fecha_nacimiento)
        form_layout.addRow("EPS:", self.input_eps)
        form_layout.addRow("Sexo:", self.input_sexo)
        form_layout.addRow("Estado civil:", self.input_estado_civil)
        form_layout.addRow("Hijos:", self.input_hijos)
        form_layout.addRow("Estudios:", self.input_estudios)
        form_layout.addRow("Responsable:", self.input_responsable)
        form_layout.addRow("Ciudad:", self.input_ciudad)

        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.setEnabled(False)
        self.btn_guardar.clicked.connect(self.handle_guardar)

        # -- Layout General

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Buscar Paciente"))
        layout.addLayout(busqueda_layout)
        layout.addWidget(self.tabla_resultados)
        layout.addWidget(QLabel("Datos del paciente"))
        layout.addLayout(form_layout)
        layout.addWidget(self.btn_guardar)
        self.setLayout(layout)


    def handle_buscar (self, query: str):
        
        db = SessionLocal()
        try:
            pacientes = search_pacientes(db, query)
            resultados = [
                {"id_paciente": p.id_paciente, "nombre": p.nombre, 
                "tipo_id": p.tipo_id, "identificacion": p.identificacion}
                for p in pacientes
            ]
        finally:
            db.close()

        self.tabla_resultados.setRowCount(len(resultados))
        for row_idx, p in enumerate(resultados):
            item_nombre = QTableWidgetItem(p["nombre"])
            item_nombre.setData(Qt.ItemDataRole.UserRole, p["id_paciente"])
            self.tabla_resultados.setItem(row_idx, 0 , item_nombre)
            self.tabla_resultados.setItem(row_idx, 1, QTableWidgetItem(p["tipo_id"]))
            self.tabla_resultados.setItem(row_idx, 2, QTableWidgetItem(p["identificacion"]))

    def handle_seleccionar_paciente(self):
        fila = self.tabla_resultados.currentRow()
        if fila < 0:
            return

        id_paciente = self.tabla_resultados.item(fila, 0).data(Qt.ItemDataRole.UserRole)

        db = SessionLocal()
        try:
            from app.services.paciente_service import get_paciente_by_id
            paciente = get_paciente_by_id(db, id_paciente)
            if paciente is None:
                return

            self.id_paciente_actual = paciente.id_paciente
            self.input_identificacion.setText(paciente.identificacion or "")
            self.input_tipo_id.setCurrentText(paciente.tipo_id or "CC")
            self.input_nombre.setText(paciente.nombre or "")
            self.input_telefono.setText(paciente.telefono or "")

            if paciente.fecha_nacimiento:
                self.input_fecha_nacimiento.setDate(QDate(paciente.fecha_nacimiento))
            else:
                self.input_fecha_nacimiento.setDate(QDate(2000, 1, 1))
            self.input_eps.setText(paciente.eps or "")
            self.input_sexo.setCurrentText(paciente.sexo or "Masculino")
            self.input_estado_civil.setCurrentText(paciente.estado_civil or "Soltero/a")
            self.input_hijos.setValue(paciente.hijos or 0)
            self.input_estudios.setText(paciente.estudios or "")
            self.input_responsable.setText(paciente.responsable or "")
            self.input_ciudad.setText(paciente.ciudad or "")
        finally:
            db.close()

        self.btn_guardar.setEnabled(True)

    def handle_guardar(self):
        if self.id_paciente_actual is None:
            return
        
        db = SessionLocal()
        try:
            update_paciente(
                db,
                self.id_paciente_actual,
                identificacion = self.input_identificacion.text().strip(),
                tipo_id = self.input_tipo_id.currentText(),
                nombre=self.input_nombre.text().strip(),
                telefono=self.input_telefono.text().strip() or None,
                fecha_nacimiento=self.input_fecha_nacimiento.date().toPython(),
                eps=self.input_eps.text().strip() or None,
                sexo=self.input_sexo.currentText(),
                estado_civil=self.input_estado_civil.currentText(),
                hijos=self.input_hijos.value(),
                estudios=self.input_estudios.text().strip() or None,
                responsable=self.input_responsable.text().strip() or None,
                ciudad=self.input_ciudad.text().strip() or None,
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
            return
        finally:
            db.close()

        QMessageBox.information(self, "Éxito", "Paciente Actualizado correctamente.")
        