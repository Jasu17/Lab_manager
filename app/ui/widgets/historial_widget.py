from PySide6.QtWidgets import (
    QLabel, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
)
from PySide6.QtCore import Qt
from app.database.session import SessionLocal
from app.services.paciente_service import search_pacientes
from app.services.examen_service import get_historial_paciente

PACIENTES_COLUMNS = ["Nombre", "Tipo ID", "Identificación"]
HISTORIAL_COLUMNS = ["Tipo de examen", "Resultado", "Observaciones", "Estado", "Fecha"]

class HistorialWidget(QWidget):
    def __init__(self):
        super().__init__()

        # -- Busqueda de paciente
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por nombre o identificación...")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.handle_buscar)

        busqueda_layout = QHBoxLayout()
        busqueda_layout.addWidget(self.input_busqueda)
        busqueda_layout.addWidget(btn_buscar)

        self.tabla_pacientes = QTableWidget()
        self.tabla_pacientes.setColumnCount(len(PACIENTES_COLUMNS))
        self.tabla_pacientes.setHorizontalHeaderLabels(PACIENTES_COLUMNS)
        self.tabla_pacientes.horizontalHeader().setStretchLastSection(True)
        self.tabla_pacientes.itemSelectionChanged.connect(self.handle_seleccionar_paciente)

        # -- Tabla de historial
        self.label_paciente_actual = QLabel("Ningún paciente seleccionado.")
        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(len(HISTORIAL_COLUMNS))
        self.tabla_historial.setHorizontalHeaderLabels(HISTORIAL_COLUMNS)
        self.tabla_historial.horizontalHeader().setStretchLastSection(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Buscar Paciente"))
        layout.addLayout(busqueda_layout)
        layout.addWidget(self.tabla_pacientes)
        layout.addWidget(self.label_paciente_actual)
        layout.addWidget(QLabel("Historial de examenes"))
        layout.addWidget(self.tabla_historial)
        self.setLayout(layout)

    def handle_buscar(self):
        query = self.input_busqueda.text().strip()
        if not query:
            return

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

        self.tabla_pacientes.setRowCount(len(resultados))
        for row_idx, p in enumerate(resultados):
            item_nombre = QTableWidgetItem(p["nombre"])
            item_nombre.setData(Qt.ItemDataRole.UserRole, p)
            self.tabla_pacientes.setItem(row_idx, 0, item_nombre)
            self.tabla_pacientes.setItem(row_idx, 1, QTableWidgetItem(p["tipo_id"]))
            self.tabla_pacientes.setItem(row_idx, 2, QTableWidgetItem(p["identificacion"]))

    def handle_seleccionar_paciente(self):
        fila = self.tabla_pacientes.currentRow()
        if fila < 0:
            return

        paciente = self.tabla_pacientes.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        self.label_paciente_actual.setText(
            f"Historial de: {paciente['nombre']} ({paciente['identificacion']})"
        )

        db = SessionLocal()
        try:
            examenes = get_historial_paciente(db, paciente["id_paciente"])
            filas = [
                {
                    "tipo_examen_nombre": e.tipo_examen.nombre,
                    "resultado": e.resultado or "",
                    "observaciones": e.observaciones or "",
                    "estado": e.estado.value,
                    "fecha": e.created_at.strftime("%Y-%m-%d %H:%M"),
                }
                for e in examenes
            ]
        finally:
            db.close()

        self.tabla_historial.setRowCount(len(filas))
        for row_idx, f in enumerate(filas):
            self.tabla_historial.setItem(row_idx, 0, QTableWidgetItem(f["tipo_examen_nombre"]))
            self.tabla_historial.setItem(row_idx, 1, QTableWidgetItem(f["resultado"]))
            self.tabla_historial.setItem(row_idx, 2, QTableWidgetItem(f["observaciones"]))
            self.tabla_historial.setItem(row_idx, 3, QTableWidgetItem(f["estado"]))
            self.tabla_historial.setItem(row_idx, 4, QTableWidgetItem(f["fecha"]))
