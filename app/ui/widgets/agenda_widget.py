from PySide6.QtWidgets import(
    QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QComboBox, QPushButton
)
from sqlalchemy.orm import joinedload
from app.database.session import SessionLocal
from app.models.cita import Cita, EstadoCita
from app.services.cita_service import update_estado_cita
from app.models.examen import ExamenRealizado
from app.ui.widgets.editar_examenes_dialog import EditarExamenesDialog

COLUMNS = ["Nombre", "Tipo ID", "Identificación", "Fecha", "Hora", "Exámenes", "Estado", "Acciones"]

class AgendaWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = QTabWidget()
        self.tables = {} # estado cita -> QTableWidget

        for estado in EstadoCita:
            tabla = QTableWidget()
            tabla.setColumnCount(len(COLUMNS))
            tabla.setHorizontalHeaderLabels(COLUMNS)
            tabla.horizontalHeader().setStretchLastSection(True)
            self.tables[estado] = tabla
            self.tabs.addTab(tabla, estado.value)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.refresh_agenda()

    def refresh_agenda(self):
        db = SessionLocal()
        try:
            citas = (
                db.query(Cita)
                .options(
                    joinedload(Cita.paciente),
                    joinedload(Cita.examenes).joinedload(ExamenRealizado.tipo_examen),
                )
                .order_by(Cita.fecha, Cita.hora)
                .all()
            )


            filas_por_estado = {estado: [] for estado in EstadoCita}
            for cita in citas:
                examen_str = ", ".join(
                    ex.tipo_examen.nombre for ex in cita.examenes
                )
                filas_por_estado[cita.estado].append({
                    "id_cita": cita.id_cita,
                    "nombre": cita.paciente.nombre,
                    "tipo_id": cita.paciente.tipo_id,
                    "identificacion": cita.paciente.identificacion,
                    "fecha": cita.fecha.strftime("%Y-%m-%d"),
                    "hora": cita.hora.strftime("%H:%M"),
                    "examenes": examen_str,
                    "examenes_detalle": [
                        {"id_examen": ex.id_examen, "id_tipo_examen": ex.id_tipo_examen}
                        for ex in cita.examenes
                    ],
                    "estado": cita.estado,
                })

        finally:
            db.close()

        for estado, filas in filas_por_estado.items():
            self._poblar_tabla(self.tables[estado], filas)

    def _poblar_tabla(self, tabla: QTableWidget, filas: list[dict]):
        tabla.setRowCount(len(filas))

        for row_idx, fila in enumerate(filas):
            tabla.setItem(row_idx, 0, QTableWidgetItem(fila["nombre"]))
            tabla.setItem(row_idx, 1, QTableWidgetItem(fila["tipo_id"]))
            tabla.setItem(row_idx, 2, QTableWidgetItem(fila["identificacion"]))
            tabla.setItem(row_idx, 3, QTableWidgetItem(fila["fecha"]))
            tabla.setItem(row_idx, 4, QTableWidgetItem(fila["hora"]))
            tabla.setItem(row_idx, 5, QTableWidgetItem(fila["examenes"]))

            combo = QComboBox()
            for estado_opcion in EstadoCita:
                combo.addItem(estado_opcion.value, estado_opcion)
            combo.setCurrentText(fila["estado"].value)
            combo.currentTextChanged.connect(
                lambda index, id_cita=fila["id_cita"], c=combo: self._on_estado_changed(id_cita, c)
            )
            tabla.setCellWidget(row_idx, 6, combo)

            btn_editar = QPushButton("Editar Exámenes")
            puede_editar = fila["estado"] in (
                EstadoCita.AGENDADA, EstadoCita.EN_ESPERA, EstadoCita.EN_ATENCION
            )
            btn_editar.setEnabled(puede_editar)
            btn_editar.clicked.connect(
                lambda checked = False, id_cita = fila["id_cita"], examenes = fila["examenes_detalle"]:
                    self._abrir_editar_examenes(id_cita, examenes)
            )
            tabla.setCellWidget(row_idx, 7, btn_editar)

    def _on_estado_changed(self, id_cita: int, combo: QComboBox):
        nuevo_estado = combo.currentData()

        db = SessionLocal()
        try:
            update_estado_cita(db, id_cita, nuevo_estado)
        finally:
            db.close()

        self.refresh_agenda()

    def _abrir_editar_examenes(self, id_cita: int, examenes_detalle: list[dict]):
        dialog = EditarExamenesDialog(id_cita, examenes_detalle, self)
        if dialog.exec() == EditarExamenesDialog.DialogCode.Accepted:
            self.refresh_agenda()

