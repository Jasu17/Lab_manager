from PySide6.QtWidgets import(
    QDialog, QFormLayout, QLineEdit, QPushButton, QLabel, QVBoxLayout
)
from app.database.session import SessionLocal
from app.services.paciente_service import create_paciente

class PacienteFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Nuevo Paciente")
        self.setFixedSize(320, 220)
        self.paciente_creado = None

        self.input_identificacion=QLineEdit()
        self.input_tipo_id=QLineEdit()
        self.input_nombre = QLineEdit()

        self.label_error = QLabel("")
        self.label_error.setStyleSheet("color: red")

        form_layout = QFormLayout()
        form_layout.addRow("Identificacion:", self.input_identificacion)
        form_layout.addRow("Tipo ID:", self.input_tipo_id)
        form_layout.addRow("Nombre:", self.input_nombre)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.handle_guardar)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.label_error)
        layout.addWidget(btn_guardar)
        self.setLayout(layout)

    def handle_guardar(self):
        identificacion = self.input_identificacion.text().strip()
        tipo_id = self.input_tipo_id.text().strip()
        nombre = self.input_nombre.text().strip()

        if not identificacion or not tipo_id or not nombre:
            self.label_error.setText("Todos los campos son obligatorios")
            return
        
        db = SessionLocal()
        try:
            paciente = create_paciente(
                db, identificacion=identificacion,tipo_id=tipo_id,nombre=nombre 
            )
            self.paciente_creado = {
                "id_paciente":paciente.id_paciente,
                "nombre":paciente.nombre,
                "tipo_id":paciente.tipo_id,
                "identificacion":paciente.identificacion,
            }
        except Exception as e:
            self.label_error.setText(f"Error al guardar {e}")
            return
        finally:
            db.close()

        self.accept()
