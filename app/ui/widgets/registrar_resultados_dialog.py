from shlex import join

from PySide6.QtWidgets import(
    QCheckBox, QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget
)

from app.database.session import SessionLocal
from app.models.examen import EstadoExamen
from app.services.examen_service import save_resultado

class RegistrarResultadosDialog(QDialog):
    def __init__(self, cita_actual: dict, id_usuario: int, parent = None):
        super().__init__(parent)
        self.cita_actual = cita_actual
        self.id_usuario = id_usuario
        self.setWindowTitle("Registrar Resultados de la cita")
        self.setMinimumSize(600, 500)

        # Estructuras por examen: inputs de resultado (uno por línea de referencia)
        self._examenes_widgets = {}

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        contenido = QWidget()
        contenido_layout = QVBoxLayout()

        for examen in cita_actual["examenes"]:
            contenido_layout.addWidget(self._construir_bloque_examen(examen))
        
        contenido.setLayout(contenido_layout)
        scroll.setWidget(contenido)

        btn_guardar_todo = QPushButton("Guardar todo")
        btn_guardar_todo.clicked.connect(self.handle_guardar_todo)

        layout_principal = QVBoxLayout()
        layout_principal.addWidget(scroll)
        layout_principal.addWidget(btn_guardar_todo)
        self.setLayout(layout_principal)

    def _construir_bloque_examen(self, examen: dict)-> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"<b>{examen['tipo_examen_nombre']}</b>"))

        lineas_referencia = (examen.get("referencia") or "").split("\n")
        lineas_resultado_previas = (examen.get("resultado") or "").split("\n")

        inputs_resultado = []
        for idx, linea_ref in enumerate(lineas_referencia):
            fila_layout = QHBoxLayout()
            fila_layout.addWidget(QLabel(linea_ref.strip()))

            input_resultado = QLineEdit()
            if idx < len(lineas_resultado_previas):
                input_resultado.setText(lineas_resultado_previas[idx].strip())
            fila_layout.addWidget(input_resultado)

            inputs_resultado.append(input_resultado)
            layout.addLayout(fila_layout)

        layout.addWidget(QLabel("Observaciones (Opcional):"))
        input_observaciones = QLineEdit()
        input_observaciones.setText(examen.get("observaciones") or "")
        layout.addWidget(input_observaciones)

        checkbox_completado = QCheckBox("Marcar como completado")
        checkbox_completado.setChecked(examen["estado"] == EstadoExamen.COMPLETADO.value)
        layout.addWidget(checkbox_completado)

        frame.setLayout(layout)

        self._examenes_widgets[examen["id_examen"]] = {
            "inputs_resultado": inputs_resultado,
            "input_observaciones": input_observaciones,
            "checkbox_completado": checkbox_completado,
        }
        return frame

    def handle_guardar_todo(self):
        db = SessionLocal()
        try:
            for id_examen, widgets in self._examenes_widgets.items():
                resultado_completo = "\n".join(
                    inp.text().strip() for inp in widgets["inputs_resultado"]
                )
                observaciones = widgets["input_observaciones"].text().strip()
                completar = widgets["checkbox_completado"].isChecked()

                save_resultado(
                    db,
                    id_examen=id_examen,
                    id_usuario=self.id_usuario,
                    resultado=resultado_completo,
                    observaciones=observaciones,
                    completar=completar,
                )

            db.commit()

        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
            return
        finally:
            db.close()

        QMessageBox.information(self, "Éxito", "Resultados guardados completamente.")
        self.accept()