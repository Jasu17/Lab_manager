from PySide6.QtWidgets import (
    QCheckBox, QDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout,
)

from app.database.session import SessionLocal
from app.services.cita_service import add_examen_to_cita, remove_examen_from_cita
from app.services.examen_service import get_all_tipos_examen

class EditarExamenesDialog(QDialog):
    def __init__(self, id_cita: int, examenes_actuales: list[dict], parent=None):
        """
        examenes_actuales: lista de dicts con al menos
            {"id_examen": int, "id_tipo_examen": int}
        """
        super().__init__(parent)
        self.id_cita = id_cita
        self.examenes_actuales = examenes_actuales
        self.setWindowTitle("Editar exámenes de la cita")
        self.setFixedSize(320, 400)

        self.checkboxes = {} # id_tipo_examen -> QCheckBox

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Seleccione los exámenes para esta cita:"))

        db = SessionLocal()
        try:
            tipos = get_all_tipos_examen(db)
            ids_actuales = {e["id_tipo_examen"] for e in examenes_actuales}

            for t in tipos:
                checkbox = QCheckBox(t.nombre)
                checkbox.setChecked(t.id_tipo_examen in ids_actuales)
                self.checkboxes[t.id_tipo_examen] = checkbox
                layout.addWidget(checkbox)
        finally:
            db.close()

        btn_guardar = QPushButton("Guardar Cambios")
        btn_guardar.clicked.connect(self.handle_guardar)
        layout.addWidget(btn_guardar)

        self.setLayout(layout)

    def handle_guardar(self):
        ids_actuales = {e["id_tipo_examen"]: e["id_examen"] for e in self.examenes_actuales}
        ids_marcados = {
            id_tipo for id_tipo, checkbox in self.checkboxes.items()
            if checkbox.isChecked()
        }

        a_agregar = ids_marcados - set(ids_actuales.keys())
        a_quitar = set(ids_actuales.keys()) - ids_marcados

        total_final = len(ids_actuales) - len(a_quitar) + len(a_agregar)

        db = SessionLocal()
        try:
            for id_tipo_examen in a_agregar:
                add_examen_to_cita(db, self.id_cita, id_tipo_examen)
            for id_tipo_examen in a_quitar:
                id_examen = ids_actuales[id_tipo_examen]
                remove_examen_from_cita(db, id_examen, self.id_cita, total_final)

            db.commit()
        except ValueError as e:
            db.rollback()
            QMessageBox.warning(self, "No se pudo guardar", str(e))
            return
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "error", f"Error inesperado: {e}")
            return
        finally:
            db.close()

        self.accept()