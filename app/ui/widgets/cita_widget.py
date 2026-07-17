"""
Widget de agendamiento de citas (RF10.2).
Permite buscar/registrar un paciente y agendar una cita con uno o
más exámenes en una sola pantalla.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QDateEdit, QTimeEdit,
    QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import QDate, QTime, Qt
from app.database.session import SessionLocal
from app.services.paciente_service import search_pacientes
from app.services.examen_service import get_all_tipos_examen
from app.services.cita_service import create_cita
from app.ui.widgets.paciente_form_dialog import PacienteFormDialog

PACIENTE_COLUMNS = ["Nombre", "Tipo ID", "Identificación"]


class CitaWidget(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.paciente_seleccionado = None
        self._all_examenes = []  # [(id_tipo_examen, nombre), ...] cacheado

        # --- Búsqueda de paciente ---
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por nombre o identificación...")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.handle_buscar_paciente)

        btn_nuevo_paciente = QPushButton("Registrar nuevo paciente")
        btn_nuevo_paciente.clicked.connect(self.handle_nuevo_paciente)

        busqueda_layout = QHBoxLayout()
        busqueda_layout.addWidget(self.input_busqueda)
        busqueda_layout.addWidget(btn_buscar)
        busqueda_layout.addWidget(btn_nuevo_paciente)

        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(len(PACIENTE_COLUMNS))
        self.tabla_resultados.setHorizontalHeaderLabels(PACIENTE_COLUMNS)
        self.tabla_resultados.horizontalHeader().setStretchLastSection(True)
        self.tabla_resultados.itemSelectionChanged.connect(self.handle_seleccionar_paciente)

        self.label_paciente_seleccionado = QLabel("Ningún paciente seleccionado.")

        # --- Formulario de cita ---
        self.input_fecha = QDateEdit()
        self.input_fecha.setDate(QDate.currentDate())
        self.input_fecha.setCalendarPopup(True)

        self.input_hora = QTimeEdit()
        self.input_hora.setTime(QTime.currentTime())

        self.input_localidad = QLineEdit()

        self.input_busqueda_examen = QLineEdit()
        self.input_busqueda_examen.setPlaceholderText("Filtrar exámenes...")
        self.input_busqueda_examen.textChanged.connect(self.filtrar_examenes)

        self.lista_examenes = QListWidget()

        btn_agendar = QPushButton("Agendar cita")
        btn_agendar.clicked.connect(self.handle_agendar_cita)

        # --- Layout general ---
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Buscar paciente"))
        layout.addLayout(busqueda_layout)
        layout.addWidget(self.tabla_resultados)
        layout.addWidget(self.label_paciente_seleccionado)

        layout.addWidget(QLabel("Datos de la cita"))
        fecha_hora_layout = QHBoxLayout()
        fecha_hora_layout.addWidget(QLabel("Fecha:"))
        fecha_hora_layout.addWidget(self.input_fecha)
        fecha_hora_layout.addWidget(QLabel("Hora:"))
        fecha_hora_layout.addWidget(self.input_hora)
        layout.addLayout(fecha_hora_layout)

        layout.addWidget(QLabel("Localidad:"))
        layout.addWidget(self.input_localidad)

        layout.addWidget(QLabel("Exámenes:"))
        layout.addWidget(self.input_busqueda_examen)
        layout.addWidget(self.lista_examenes)

        layout.addWidget(btn_agendar)
        self.setLayout(layout)

        self._cargar_tipos_examen()

    def _cargar_tipos_examen(self):
        db = SessionLocal()
        try:
            tipos = get_all_tipos_examen(db)
            self._all_examenes = [(t.id_tipo_examen, t.nombre) for t in tipos]
        finally:
            db.close()
        self.filtrar_examenes("")

    def filtrar_examenes(self, texto: str):
        self.lista_examenes.clear()
        texto = texto.lower().strip()
        for id_tipo_examen, nombre in self._all_examenes:
            if texto in nombre.lower():
                item = QListWidgetItem(nombre)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                item.setData(Qt.ItemDataRole.UserRole, id_tipo_examen)
                self.lista_examenes.addItem(item)

    def handle_buscar_paciente(self):
        query = self.input_busqueda.text().strip()
        if not query:
            return

        db = SessionLocal()
        try:
            pacientes = search_pacientes(db, query)
            resultados = [
                {
                    "id_paciente": p.id_paciente,
                    "nombre": p.nombre,
                    "tipo_id": p.tipo_id,
                    "identificacion": p.identificacion,
                }
                for p in pacientes
            ]
        finally:
            db.close()

        self.tabla_resultados.setRowCount(len(resultados))
        for row_idx, p in enumerate(resultados):
            item_nombre = QTableWidgetItem(p["nombre"])
            item_nombre.setData(Qt.ItemDataRole.UserRole, p)
            self.tabla_resultados.setItem(row_idx, 0, item_nombre)
            self.tabla_resultados.setItem(row_idx, 1, QTableWidgetItem(p["tipo_id"]))
            self.tabla_resultados.setItem(row_idx, 2, QTableWidgetItem(p["identificacion"]))

    def handle_seleccionar_paciente(self):
        fila = self.tabla_resultados.currentRow()
        if fila < 0:
            return

        item = self.tabla_resultados.item(fila, 0)
        self.paciente_seleccionado = item.data(Qt.ItemDataRole.UserRole)
        self.label_paciente_seleccionado.setText(
            f"Paciente seleccionado: {self.paciente_seleccionado['nombre']} "
            f"({self.paciente_seleccionado['identificacion']})"
        )

    def handle_nuevo_paciente(self):
        dialog = PacienteFormDialog(self)
        if dialog.exec() == PacienteFormDialog.DialogCode.Accepted:
            self.paciente_seleccionado = dialog.paciente_creado
            self.label_paciente_seleccionado.setText(
                f"Paciente seleccionado: {self.paciente_seleccionado['nombre']} "
                f"({self.paciente_seleccionado['identificacion']})"
            )

    def handle_agendar_cita(self):
        if self.paciente_seleccionado is None:
            QMessageBox.warning(self, "Falta paciente", "Seleccione o registre un paciente primero.")
            return

        ids_examenes = [
            self.lista_examenes.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.lista_examenes.count())
            if self.lista_examenes.item(i).checkState() == Qt.CheckState.Checked
        ]

        if not ids_examenes:
            QMessageBox.warning(self, "Faltan exámenes", "Seleccione al menos un examen.")
            return

        db = SessionLocal()
        try:
            create_cita(
                db,
                id_paciente=self.paciente_seleccionado["id_paciente"],
                id_usuario=self.usuario["id_usuario"],  
                fecha=self.input_fecha.date().toPython(),
                hora=self.input_hora.time().toPython(),
                id_tipos_examen=ids_examenes,
                localidad=self.input_localidad.text().strip() or None,
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agendar la cita: {e}")
            return
        finally:
            db.close()

        QMessageBox.information(self, "Éxito", "Cita agendada correctamente.")
        self._limpiar_formulario()

    def _limpiar_formulario(self):
        self.paciente_seleccionado = None
        self.label_paciente_seleccionado.setText("Ningún paciente seleccionado.")
        self.input_busqueda.clear()
        self.tabla_resultados.setRowCount(0)
        self.input_localidad.clear()
        self.filtrar_examenes("")