from PySide6.QtWidgets import(
    QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QMenu, QMessageBox
)
from sqlalchemy.orm import joinedload
from app.database.session import SessionLocal
from app.models.cita import Cita, EstadoCita
from app.services.cita_service import update_estado_cita
from app.models.examen import ExamenRealizado
from app.ui.widgets.editar_examenes_dialog import EditarExamenesDialog
from app.config.lab_config import get_lab_config
from app.services.whatsapp_service import (
    enviar_bienvenida, enviar_cita_asignada, enviar_confirmar_cita, TelefonoInvalidoError
)

COLUMNS = ["Nombre", "Tipo ID", "Identificación", "Fecha", "Hora", "Exámenes", "Estado", "Acciones", "WhatsApp"]

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

        btn_refrescar = QPushButton("Refrescar agenda")
        btn_refrescar.clicked.connect(self.refresh_agenda)


        layout = QVBoxLayout()
        layout.addWidget(btn_refrescar)
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
                    "telefono": cita.paciente.telefono,
                    "fecha_obj": cita.fecha,
                    "fecha": cita.fecha.strftime("%Y-%m-%d"),
                    "hora": cita.hora.strftime("%H:%M"),
                    "localidad": cita.localidad,
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
            btn_whatsapp = QPushButton("WhatsApp")
            btn_whatsapp.clicked.connect(
                lambda checked = False, f=fila: self._mostrar_menu_whatsapp(f, btn_whatsapp)
            )
            tabla.setCellWidget(row_idx, 8, btn_whatsapp)

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

    def _mostrar_menu_whatsapp(self, fila: dict, boton: QPushButton):
        menu = QMenu(self)
        accion_bienvenida = menu.addAction("Enviar bienvenida")
        accion_cita_asignada = menu.addAction("Enviar cita asignada")
        accion_confirmar = menu.addAction("Enviar comfimar cita")

        accion_bienvenida.triggered.connect(lambda: self._enviar_whatsapp("bienvenida", fila))
        accion_cita_asignada.triggered.connect(lambda: self._enviar_whatsapp("cita_asignada", fila))
        accion_confirmar.triggered.connect(lambda: self._enviar_whatsapp("confirmar", fila))

        menu.exec(boton.mapToGlobal(boton.rect().bottomLeft()))

    def _enviar_whatsapp(self, tipo: str, fila:dict):
        lab_config = get_lab_config()
        nombre_lab = lab_config["nombre_lab"]

        try:
            if tipo == "bienvenida":
                enviar_bienvenida(fila["telefono"], fila["nombre"], nombre_lab)
            elif tipo == "cita_asignada":
                enviar_cita_asignada(
                    fila["telefono"], fila["nombre"], nombre_lab,
                    fila["fecha_obj"], fila["hora"], fila.get("localidad") or "N/A"
                )
            elif tipo == "confirmar":
                enviar_confirmar_cita(
                    fila["telefono"], fila["nombre"], nombre_lab,
                    fila["fecha_obj"], fila["hora"], fila.get("localidad") or "N/A"
                )
        except TelefonoInvalidoError as e:
            QMessageBox.warning(self, "Teléfono inválido", str(e))
