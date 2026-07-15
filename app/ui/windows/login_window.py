from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Signal
from app.database.session import SessionLocal
from app.services.auth_service import autenticate

class LoginWindow(QWidget):
    login_success = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab Manager - Iniciar Sesión")
        self.setFixedSize(320,180)

        self.input_identificacion = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.label_error = QLabel("")
        self.label_error.setStyleSheet("color: red")

        self.btn_login = QPushButton("Iniciar Sesión")
        self.btn_login.clicked.connect(self.handle_login)

        form_layout = QFormLayout()
        form_layout.addRow("Identificacion:", self.input_identificacion)
        form_layout.addRow("contraseña:", self.input_password)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.label_error)
        main_layout.addWidget(self.btn_login)

        self.setLayout(main_layout)

    def handle_login(self):
        identificacion = self.input_identificacion.text().strip()
        password = self.input_password.text()

        if not identificacion or not password:
            self.label_error.setText("Complete los dos campos")
            return

        db = SessionLocal()

        try:
            usuario = autenticate(db, identificacion, password)
        finally:
            db.close()

        if usuario is None:
            self.label_error.setText("Credenciales inválidas o Usuario inactivo.")
            return

        self.label_error.setText("")
        self.login_success.emit(usuario)