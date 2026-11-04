from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, Signal


class VisLogin(QWidget):

    login_exitoso = Signal()

    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                font-family: Segoe UI;
            }
        """)

        self.crear_interfaz()

    def crear_interfaz(self):

        principal = QHBoxLayout(self)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        # PANEL IZQUIERDO
        panel_izquierdo = QFrame()
        panel_izquierdo.setStyleSheet("""
            QFrame {
                background-color: #001F3F;
            }
        """)

        layout_izquierdo = QVBoxLayout(panel_izquierdo)
        layout_izquierdo.setAlignment(Qt.AlignCenter)

        logo = QLabel("ARKOS")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            color: white;
            font-size: 48px;
            font-weight: bold;
            letter-spacing: 5px;
        """)

        subtitulo = QLabel("CHECADOR DOCENTE")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("""
            color: #FF851B;
            font-size: 17px;
            font-weight: bold;
            letter-spacing: 2px;
        """)

        descripcion = QLabel(
            "Sistema de control de asistencia\n"
            "mediante reconocimiento facial"
        )
        descripcion.setAlignment(Qt.AlignCenter)
        descripcion.setStyleSheet("""
            color: #DCE6F1;
            font-size: 14px;
            margin-top: 20px;
        """)

        layout_izquierdo.addWidget(logo)
        layout_izquierdo.addWidget(subtitulo)
        layout_izquierdo.addWidget(descripcion)

        # PANEL DERECHO
        panel_derecho = QFrame()
        panel_derecho.setStyleSheet("""
            QFrame {
                background-color: #F4F6F9;
            }
        """)

        layout_derecho = QVBoxLayout(panel_derecho)
        layout_derecho.setContentsMargins(70, 50, 70, 50)
        layout_derecho.setAlignment(Qt.AlignCenter)

        titulo = QLabel("Bienvenido")
        titulo.setStyleSheet("""
            color: #001F3F;
            font-size: 32px;
            font-weight: bold;
        """)

        texto = QLabel("Inicia sesión para continuar")
        texto.setStyleSheet("""
            color: #64748B;
            font-size: 14px;
            margin-bottom: 20px;
        """)

        etiqueta_usuario = QLabel("Usuario")
        etiqueta_usuario.setStyleSheet("color: #001F3F; font-weight: bold;")

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Ingresa tu usuario")
        self.txt_usuario.setMinimumHeight(45)

        etiqueta_password = QLabel("Contraseña")
        etiqueta_password.setStyleSheet("color: #001F3F; font-weight: bold;")

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Ingresa tu contraseña")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setMinimumHeight(45)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("""
            color: #DC2626;
            font-size: 12px;
        """)

        btn_ingresar = QPushButton("INICIAR SESIÓN")
        btn_ingresar.setMinimumHeight(48)
        btn_ingresar.setCursor(Qt.PointingHandCursor)
        btn_ingresar.setStyleSheet("""
            QPushButton {
                background-color: #003B73;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #1677C8;
            }
        """)

        btn_ingresar.clicked.connect(self.validar_login)
        self.txt_password.returnPressed.connect(self.validar_login)

        aviso = QLabel("ARKOS | Sistema interno")
        aviso.setAlignment(Qt.AlignCenter)
        aviso.setStyleSheet("""
            color: #94A3B8;
            font-size: 11px;
            margin-top: 25px;
        """)

        layout_derecho.addWidget(titulo)
        layout_derecho.addWidget(texto)
        layout_derecho.addSpacing(15)
        layout_derecho.addWidget(etiqueta_usuario)
        layout_derecho.addWidget(self.txt_usuario)
        layout_derecho.addSpacing(15)
        layout_derecho.addWidget(etiqueta_password)
        layout_derecho.addWidget(self.txt_password)
        layout_derecho.addWidget(self.lbl_error)
        layout_derecho.addSpacing(15)
        layout_derecho.addWidget(btn_ingresar)
        layout_derecho.addWidget(aviso)

        principal.addWidget(panel_izquierdo, 1)
        principal.addWidget(panel_derecho, 1)

    def validar_login(self):

        usuario = self.txt_usuario.text().strip()
        password = self.txt_password.text()

        # Credenciales provisionales para desarrollo
        if usuario == "admin" and password == "Arkos2026!":

            self.lbl_error.setText("")
            self.login_exitoso.emit()

        else:

            self.lbl_error.setText(
                "Usuario o contraseña incorrectos."
            )