from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QTextEdit, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from app.config.lab_config import get_lab_config
from app.database.session import SessionLocal
from app.services.cita_service import get_agenda_bacteriologa
from app.services.examen_service import save_resultado
from app.reports.resultado_examen import calcular_edad, generar_pdf_resultado
from app.reports.comprobante_asistencia import generar_pdf_comprobante_asistencia
from app.services.usuario_service import get_usuario_by_id

CITAS_COLUMNS = ["Paciente", "Identificación", "Fecha", "Hora", "Localidad"]
EXAMENES_COLUMNS = ["Tipo de Examen", "Estado"]

class BacteriologaWidget(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.cita_actual = None # dict con datos de la cita seleccionada
        self.examen_actual = None  # dict con datos del examen seleccionado

        # -- Tabla de citas habilitadas
        self.tabla_citas = QTableWidget()
        self.tabla_citas.setColumnCount(len(CITAS_COLUMNS))
        self.tabla_citas.setHorizontalHeaderLabels(CITAS_COLUMNS)
        self.tabla_citas.horizontalHeader().setStretchLastSection(True)
        self.tabla_citas.itemSelectionChanged.connect(self.handle_seleccionar_cita)

        btn_comprobante = QPushButton()
        btn_comprobante.clicked.connect(self.handle_generar_comprobante)

        # -- Tabla de Examenes de la cita seleccionada
        self.tabla_examenes = QTableWidget()
        self.tabla_examenes.setColumnCount(len(EXAMENES_COLUMNS))
        self.tabla_examenes.setHorizontalHeaderLabels(EXAMENES_COLUMNS)
        self.tabla_examenes.horizontalHeader().setStretchLastSection(True)
        self.tabla_examenes.itemSelectionChanged.connect(self.handle_seleccionar_examen)

        # -- Formulario de resultado
        self.input_resultado = QTextEdit()
        self.input_observaciones = QTextEdit()

        self.btn_guardar_avance = QPushButton("Guardar avance")
        self.btn_guardar_avance.setEnabled(False)
        self.btn_guardar_avance.clicked.connect(lambda: self.handle_guardar_resultado(completar=False))

        self.btn_completar = QPushButton("Guardar y completar")
        self.btn_completar.setEnabled(False)
        self.btn_completar.clicked.connect(lambda: self.handle_guardar_resultado(completar=True))

        self.btn_pdf_resultado = QPushButton("Generar PDF de resultado")
        self.btn_pdf_resultado.setEnabled(False)
        self.btn_pdf_resultado.clicked.connect(self.handle_generar_pdf_resultado)

        btn_refrescar = QPushButton("Refrescar Agenda")
        btn_refrescar.clicked.connect(self.refresh_citas)

        # -- Layout General
        layout = QVBoxLayout()
        layout.addWidget(btn_refrescar)
        layout.addWidget(QLabel("Citas habilitadas"))
        layout.addWidget(self.tabla_citas)
        layout.addWidget(btn_comprobante)

        layout.addWidget(QLabel("Exámenes de la Cita"))
        layout.addWidget(self.tabla_examenes)

        layout.addWidget(QLabel("Resultado:"))
        layout.addWidget(self.input_resultado)
        layout.addWidget(QLabel("Observaciones:"))
        layout.addWidget(self.input_observaciones)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.btn_guardar_avance)
        botones_layout.addWidget(self.btn_completar)
        botones_layout.addWidget(self.btn_pdf_resultado)
        layout.addLayout(botones_layout)

        self.setLayout(layout)
        self.refresh_citas()

    def refresh_citas(self):
        db = SessionLocal()
        try:
            citas = get_agenda_bacteriologa(db)
            self._citas_cache = [
                {
                    "id_cita": c.id_cita,
                    "paciente_nombre": c.paciente.nombre,
                    "paciente_tipo_id": c.paciente.tipo_id,
                    "paciente_identificacion": c.paciente.identificacion,
                    "fecha": c.fecha.strftime("%Y-%m-%d"),
                    "hora": c.hora.strftime("%H:%M"),
                    "localidad": c.localidad,
                    "id_paciente": c.paciente.id_paciente,
                    "examenes": [
                        {
                            "id_examen": e.id_examen,
                            "id_tipo_examen": e.id_tipo_examen,
                            "tipo_examen_nombre": e.tipo_examen.nombre,
                            "referencia": e.tipo_examen.referencia,
                            "estado": e.estado.value,
                            "resultado": e.resultado,
                            "observaciones": e.observaciones,
                        }
                        for e in c.examenes
                    ],
                }
                for c in citas
            ]
        finally:
            db.close()

        self.tabla_citas.setRowCount(len(self._citas_cache))
        for row_idx, c in enumerate(self._citas_cache):
            item_paciente = QTableWidgetItem(c["paciente_nombre"])
            item_paciente.setData(Qt.ItemDataRole.UserRole, row_idx)
            self.tabla_citas.setItem(row_idx, 0, item_paciente)
            self.tabla_citas.setItem(row_idx, 1, QTableWidgetItem(c["paciente_identificacion"]))
            self.tabla_citas.setItem(row_idx, 2, QTableWidgetItem(c["fecha"]))
            self.tabla_citas.setItem(row_idx, 3, QTableWidgetItem(c["hora"]))
            self.tabla_citas.setItem(row_idx, 4, QTableWidgetItem(c["localidad"] or ""))

        self.tabla_examenes.setRowCount(0)
        self._limpiar_formulario_resultado()

    def handle_seleccionar_cita(self):
        fila = self.tabla_citas.currentRow()
        if fila < 0:
            return

        row_idx = self.tabla_citas.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        self.cita_actual = self._citas_cache[row_idx]

        examenes = self.cita_actual["examenes"]
        self.tabla_examenes.setRowCount(len(examenes))
        for row_idx_ex, e in enumerate(examenes):
            item_tipo = QTableWidgetItem(e["tipo_examen_nombre"])
            item_tipo.setData(Qt.ItemDataRole.UserRole, row_idx_ex)
            self.tabla_examenes.setItem(row_idx_ex, 0, item_tipo)
            self.tabla_examenes.setItem(row_idx_ex, 1, QTableWidgetItem(e["estado"]))

        self._limpiar_formulario_resultado()

    def handle_seleccionar_examen(self):
        fila = self.tabla_examenes.currentRow()
        if fila < 0:
            return

        row_idx_ex = self.tabla_examenes.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        self.examen_actual = self.cita_actual["examenes"][row_idx_ex]

        self.input_resultado.setPlainText(self.examen_actual["resultado"] or "")
        self.input_observaciones.setPlainText(self.examen_actual["observaciones"] or "")

        self.btn_guardar_avance.setEnabled(True)
        self.btn_completar.setEnabled(True)
        self.btn_pdf_resultado.setEnabled(True)
    
    def handle_guardar_resultado(self, completar: bool):
        if self.examen_actual is None:
            return

        db = SessionLocal()
        try:
            save_resultado(
                db,
                id_examen=self.examen_actual["id_examen"],
                id_usuario=self.usuario["id_usuario"],
                resultado=self.input_resultado.toPlainText().strip(),
                observaciones=self.input_observaciones.toPlainText().strip(),
                completar=completar,
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo gaurdar: {e}")
            return
        finally:
            db.close()

        QMessageBox.information(self, "Exito", "Resultado guardado correctamente")
        self.refresh_citas()

    def handle_generar_pdf_resultado(self):
        if self.examen_actual is None or self.cita_actual is None:
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF de resultado", "resultado.pdf", "PDF (*.pdf)" 
        )
        if not ruta:
            return

        db = SessionLocal()
        try:
            from app.services.paciente_service import get_paciente_by_id
            usuario_bacteriologa = get_usuario_by_id(db, self.usuario["id_usuario"])
            paciente = get_paciente_by_id(db, self.cita_actual["id_paciente"])
            
            lab_config = get_lab_config()

            edad = calcular_edad(paciente.fecha_nacimiento) if paciente else None

            datos = {
                "numero_cita": self.cita_actual["id_cita"],
                "fecha_cita": self.cita_actual["fecha"],
                "fecha_actual": datetime.now().strftime("%d/%m/%Y"),
                "hora_actual": datetime.now().strftime("%H:%M"),

                "paciente_nombre": self.cita_actual["paciente_nombre"],
                "paciente_documento": f"{self.cita_actual['paciente_tipo_id']} {self.cita_actual['paciente_identificacion']}",
                "paciente_edad": edad,
                "paciente_sexo": paciente.sexo if paciente else None,
                "paciente_estado_civil": paciente.estado_civil if paciente else None,
                "paciente_ciudad": paciente.ciudad if paciente else None,
                "paciente_telefono": paciente.telefono if paciente else None,
                "paciente_nacimiento": paciente.fecha_nacimiento.strftime("%d/%m/%Y") if paciente and paciente.fecha_nacimiento else None,

                "examen_nombre": self.examen_actual["tipo_examen_nombre"],
                "resultado": self.input_resultado.toPlainText().strip(),
                "referencia": self.examen_actual.get("referencia"),
                "fecha_examen": self.cita_actual["fecha"],

                "lab_nombre": lab_config["nombre_lab"],
                "lab_direccion": lab_config["direccion_lab"],
                "lab_ciudad": lab_config["ciudad_lab"],
                "lab_logo_path": lab_config["logo_path"],

                "bacteriologa_nombre": usuario_bacteriologa.nombre if usuario_bacteriologa else self.usuario["nombre"],
                "bacteriologa_registro": usuario_bacteriologa.registro_profesional if usuario_bacteriologa else None,
                "bacteriologa_firma_path": usuario_bacteriologa.firma_imagen if usuario_bacteriologa else None,
            }
        finally:
            db.close()
        
        try:
            generar_pdf_resultado(ruta, datos)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el PDF: {e}")
            return
        
        QMessageBox.information(self, "Éxito", f"PDF generado en : {ruta}")

    def handle_generar_comprobante(self):
        if self.cita_actual is None:
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Comprobante de asistencia", "comprobante.pdf", "PDF (*.pdf)"
        )
        if not ruta:
            return

        try:
            generar_pdf_comprobante_asistencia(ruta, self.cita_actual)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el comprobante: {e}")
            return

        QMessageBox.information(self, "Exito", f"Comprobante guardado en: {ruta}")

    def _limpiar_formulario_resultado(self):
        self.examen_actual = None
        self.input_resultado.clear()
        self.input_observaciones.clear()
        self.btn_guardar_avance.setEnabled(False)
        self.btn_completar.setEnabled(False)
        self.btn_pdf_resultado.setEnabled(False)