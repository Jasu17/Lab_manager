from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QTextEdit, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from app.database.session import SessionLocal
from app.services.cita_service import get_agenda_bacteriologa
from app.services.examen_service import save_resultado
from app.reports.resultado_examen import generar_pdf_resultado
from app.reports.comprobante_asistencia import generar_pdf_comprobante_asistencia

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

        # -- Layout General
        layout = QVBoxLayout()
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
                    "examenes": [
                        {
                            "id_examen": e.id_examen,
                            "tipo_examen_nombre": e.tipo_examen.nombre,
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

        datos = {
            "paciente_nombre": self.cita_actual["paciente_nombre"],
            "paciente_tipo_id": self.cita_actual["paciente_tipo_id"],
            "paciente_identificacion": self.cita_actual["paciente_identificacion"],
            "tipo_examen_nombre": self.cita_actual["tipo_examen_nombre"],
            "resultado": self.input_resultado.toPlainText().strip(),
            "observaciones": self.input_observaciones.toPlainText().strip(),
            "fecha": self.cita_actual["fecha"],
            "usuario_nombre": self.usuario["nombre"],
        }

        try:
            generar_pdf_resultado(ruta, datos)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el PDF: {e}")
            return

        QMessageBox.information(self, "Exito", f"PDF generado en: {ruta}")

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