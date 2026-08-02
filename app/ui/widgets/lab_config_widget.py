import os
import shutil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QFileDialog, QMessageBox
)
from app.config.lab_config import get_lab_config, save_lab_config

class LabConfigWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.input_nombre = QLineEdit()
        self.input_direccion = QLineEdit()
        self.input_ciudad = QLineEdit()

        self.label_logo_actual = QLabel("Sin logo cargado")
        self.btn_seleccionar_logo = QPushButton("Cargar logo (imagen)")
        self.btn_seleccionar_logo.clicked.connect(self.handle_seleccionar_logo)
        self._ruta_logo_nueva = None

        btn_guardar = QPushButton("Guardar configuración")
        btn_guardar.clicked.connect(self.handle_guardar)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Nombre del laboratorio:"))
        layout.addWidget(self.input_nombre)
        layout.addWidget(QLabel("Dirección:"))
        layout.addWidget(self.input_direccion)
        layout.addWidget(QLabel("Ciudad:"))
        layout.addWidget(self.input_ciudad)
        layout.addWidget(QLabel("Logo:"))
        layout.addWidget(self.label_logo_actual)
        layout.addWidget(self.btn_seleccionar_logo)
        layout.addWidget(btn_guardar)
        self.setLayout(layout)

        self._cargar_config_actual()

    def _cargar_config_actual(self):
        config = get_lab_config()
        self.input_nombre.setText(config["nombre_lab"])
        self.input_direccion.setText(config["direccion_lab"])
        self.input_ciudad.setText(config["ciudad_lab"])

        if config["logo_path"]:
            self.label_logo_actual.setText(f"Logo cargado: {os.path.basename(config['logo_path'])}")
        else:
            self.label_logo_actual.setText("Sin logo cargado.")

    def handle_seleccionar_logo(self):
        ruta_origen , _ = QFileDialog.getOpenFileName(
            self, "Seleccionar logo", "", "Imágenes (*.png *.jpg *.jpeg)"
        )
        if not ruta_origen:
            return
        
        self._ruta_logo_nueva = ruta_origen
        self.label_logo_actual.setText(f"Nuevo logo seleccionado: {os.path.basename(ruta_origen)}")

    def handle_guardar(self):
        config = get_lab_config()
        config["nombre_lab"] = self.input_nombre.text().strip()
        config["direccion_lab"] = self.input_direccion.text().strip()
        config["ciudad_lab"] = self.input_ciudad.text().strip()

        if self._ruta_logo_nueva:
            carpeta_logo = os.path.join("app", "resources", "logo")
            os.makedirs(carpeta_logo, exist_ok=True)
            extension = os.path.splitext(self._ruta_logo_nueva)[1]
            ruta_destino = os.path.join(carpeta_logo, f"logo{extension}")
            shutil.copy(self._ruta_logo_nueva, ruta_destino)
            config["logo_path"] = ruta_destino
            self._ruta_logo_nueva = None

        try:
            save_lab_config(config)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
            return

        QMessageBox.information(self, "Éxito", "Configuración guardada correctamente")