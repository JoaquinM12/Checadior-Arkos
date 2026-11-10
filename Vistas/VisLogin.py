
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy
)

from PySide6.QtCore import Qt, Signal


class VisLogin(QWidget):

    login_exitoso = Signal()

    def __init__(self):
        super().__init__()

        self.crear_interfaz()
        self.aplicar_estilos()

    def crear_interfaz(self):

        principal = QHBoxLayout(self)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        # ==================================================
        # PANEL IZQUIERDO
        # ==================================================

        self.panel_izquierdo = QFrame()
        self.panel_izquierdo.setObjectName("panelIzquierdo")

        layout_izquierdo = QVBoxLayout(self.panel_izquierdo)
        layout_izquierdo.setContentsMargins(45, 45, 45, 35)
        layout_izquierdo.setSpacing(0)

        marca = QHBoxLayout()
        marca.setSpacing(10)

        icono_marca = QLabel("A")
        icono_marca.setObjectName("iconoMarca")
        icono_marca.setAlignment(Qt.AlignCenter)
        icono_marca.setFixedSize(48, 48)

        textos_marca = QVBoxLayout()
        textos_marca.setSpacing(1)

        nombre_marca = QLabel("ARKOS")
        nombre_marca.setObjectName("nombreMarca")

        subtitulo_marca = QLabel("CHECADOR DOCENTE")
        subtitulo_marca.setObjectName("subtituloMarca")

        textos_marca.addWidget(nombre_marca)
        textos_marca.addWidget(subtitulo_marca)

        marca.addWidget(icono_marca)
        marca.addLayout(textos_marca)
        marca.addStretch()

        layout_izquierdo.addLayout(marca)
        layout_izquierdo.addStretch(2)

        etiqueta_sistema = QLabel("SISTEMA INSTITUCIONAL")
        etiqueta_sistema.setObjectName("etiquetaSistema")

        titulo_izquierdo = QLabel(
            "Control docente\ninteligente."
        )
        titulo_izquierdo.setObjectName("tituloIzquierdo")
        titulo_izquierdo.setWordWrap(True)

        descripcion_izquierda = QLabel(
            "Una plataforma diseñada para gestionar la asistencia "
            "docente de manera ágil, segura y eficiente mediante "
            "tecnología de reconocimiento facial."
        )
        descripcion_izquierda.setObjectName("descripcionIzquierda")
        descripcion_izquierda.setWordWrap(True)

        layout_izquierdo.addWidget(etiqueta_sistema)
        layout_izquierdo.addSpacing(18)
        layout_izquierdo.addWidget(titulo_izquierdo)
        layout_izquierdo.addSpacing(18)
        layout_izquierdo.addWidget(descripcion_izquierda)
        layout_izquierdo.addSpacing(40)

        caracteristicas = [
            ("01", "Reconocimiento facial"),
            ("02", "Registro de asistencia"),
            ("03", "Administración académica")
        ]

        for numero, texto in caracteristicas:

            fila = QHBoxLayout()
            fila.setSpacing(13)

            lbl_numero = QLabel(numero)
            lbl_numero.setObjectName("numeroCaracteristica")
            lbl_numero.setFixedSize(32, 32)
            lbl_numero.setAlignment(Qt.AlignCenter)

            lbl_texto = QLabel(texto)
            lbl_texto.setObjectName("textoCaracteristica")

            fila.addWidget(lbl_numero)
            fila.addWidget(lbl_texto)
            fila.addStretch()

            layout_izquierdo.addLayout(fila)
            layout_izquierdo.addSpacing(12)

        layout_izquierdo.addStretch(2)

        pie_izquierdo = QLabel(
            "ARKOS CHECADOR  |  PLATAFORMA DE CONTROL"
        )
        pie_izquierdo.setObjectName("pieIzquierdo")

        layout_izquierdo.addWidget(pie_izquierdo)

        # ==================================================
        # PANEL DERECHO
        # ==================================================

        panel_derecho = QFrame()
        panel_derecho.setObjectName("panelDerecho")

        layout_derecho = QVBoxLayout(panel_derecho)
        layout_derecho.setContentsMargins(35, 30, 35, 25)
        layout_derecho.setAlignment(Qt.AlignCenter)

        # TARJETA DE ACCESO
        tarjeta_login = QFrame()
        tarjeta_login.setObjectName("tarjetaLogin")

        tarjeta_login.setMinimumWidth(460)
        tarjeta_login.setMaximumWidth(540)

        tarjeta_login.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        formulario = QVBoxLayout(tarjeta_login)
        formulario.setContentsMargins(42, 42, 42, 38)
        formulario.setSpacing(0)

        # ENCABEZADO
        etiqueta_acceso = QLabel("ACCESO AL SISTEMA")
        etiqueta_acceso.setObjectName("etiquetaAcceso")

        titulo_login = QLabel("Bienvenido")
        titulo_login.setObjectName("tituloLogin")

        descripcion_login = QLabel(
            "Ingresa tus credenciales para continuar."
        )
        descripcion_login.setObjectName("descripcionLogin")
        descripcion_login.setWordWrap(True)

        formulario.addWidget(etiqueta_acceso)
        formulario.addSpacing(15)
        formulario.addWidget(titulo_login)
        formulario.addSpacing(8)
        formulario.addWidget(descripcion_login)
        formulario.addSpacing(35)

        # USUARIO
        etiqueta_usuario = QLabel("USUARIO")
        etiqueta_usuario.setObjectName("etiquetaCampo")

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setObjectName("campoLogin")
        self.txt_usuario.setPlaceholderText("Ingresa tu usuario")
        self.txt_usuario.setMinimumHeight(56)
        self.txt_usuario.setClearButtonEnabled(True)

        formulario.addWidget(etiqueta_usuario)
        formulario.addSpacing(10)
        formulario.addWidget(self.txt_usuario)
        formulario.addSpacing(25)

        # CONTRASEÑA
        etiqueta_password = QLabel("CONTRASEÑA")
        etiqueta_password.setObjectName("etiquetaCampo")

        contenedor_password = QFrame()
        contenedor_password.setObjectName("contenedorPassword")
        contenedor_password.setMinimumHeight(56)

        layout_password = QHBoxLayout(contenedor_password)
        layout_password.setContentsMargins(0, 0, 10, 0)
        layout_password.setSpacing(0)

        self.txt_password = QLineEdit()
        self.txt_password.setObjectName("campoPassword")
        self.txt_password.setPlaceholderText("Ingresa tu contraseña")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setMinimumHeight(54)

        self.btn_ver_password = QPushButton("VER")
        self.btn_ver_password.setObjectName("btnVerPassword")
        self.btn_ver_password.setCursor(Qt.PointingHandCursor)
        self.btn_ver_password.setFixedWidth(75)
        self.btn_ver_password.setCheckable(True)

        self.btn_ver_password.toggled.connect(
            self.cambiar_visibilidad_password
        )

        layout_password.addWidget(self.txt_password, 1)
        layout_password.addWidget(self.btn_ver_password)

        formulario.addWidget(etiqueta_password)
        formulario.addSpacing(10)
        formulario.addWidget(contenedor_password)
        formulario.addSpacing(12)

        # MENSAJE DE ERROR
        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("lblError")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setMinimumHeight(25)

        formulario.addWidget(self.lbl_error)
        formulario.addSpacing(15)

        # BOTÓN DE INGRESO
        self.btn_ingresar = QPushButton("INICIAR SESIÓN")
        self.btn_ingresar.setObjectName("btnIngresar")
        self.btn_ingresar.setMinimumHeight(56)
        self.btn_ingresar.setCursor(Qt.PointingHandCursor)

        formulario.addWidget(self.btn_ingresar)
        formulario.addSpacing(28)

        # PIE DE TARJETA
        separador = QFrame()
        separador.setObjectName("separador")
        separador.setFixedHeight(1)

        formulario.addWidget(separador)
        formulario.addSpacing(20)

        pie_tarjeta = QLabel(
            "Acceso exclusivo para personal autorizado."
        )
        pie_tarjeta.setObjectName("pieTarjeta")
        pie_tarjeta.setAlignment(Qt.AlignCenter)
        pie_tarjeta.setWordWrap(True)

        formulario.addWidget(pie_tarjeta)

        layout_derecho.addWidget(
            tarjeta_login,
            alignment=Qt.AlignCenter
        )

        layout_derecho.addStretch()

        pie_derecho = QLabel(
            "ARKOS CHECADOR  •  SISTEMA INTERNO"
        )
        pie_derecho.setObjectName("pieDerecho")
        pie_derecho.setAlignment(Qt.AlignCenter)

        layout_derecho.addWidget(pie_derecho)

        # AGREGAR PANELES
        principal.addWidget(self.panel_izquierdo, 5)
        principal.addWidget(panel_derecho, 6)

        # ==================================================
        # CONEXIONES
        # ==================================================

        self.btn_ingresar.clicked.connect(self.validar_login)

        self.txt_password.returnPressed.connect(
            self.validar_login
        )

        self.txt_usuario.returnPressed.connect(
            self.txt_password.setFocus
        )

    # ======================================================
    # ESTILOS
    # ======================================================

    def aplicar_estilos(self):

        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI";
            }

            QFrame#panelIzquierdo {
                background-color: #001F3F;
                border: none;
            }

            QLabel#iconoMarca {
                background-color: #FF851B;
                color: #001F3F;
                border-radius: 12px;
                font-size: 27px;
                font-weight: 900;
            }

            QLabel#nombreMarca {
                color: #FFFFFF;
                font-size: 23px;
                font-weight: 900;
                letter-spacing: 3px;
            }

            QLabel#subtituloMarca {
                color: #FF851B;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 2px;
            }

            QLabel#etiquetaSistema {
                color: #FF9B43;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 2px;
            }

            QLabel#tituloIzquierdo {
                color: #FFFFFF;
                font-size: 42px;
                font-weight: 800;
            }

            QLabel#descripcionIzquierda {
                color: #C5D3E2;
                font-size: 14px;
            }

            QLabel#numeroCaracteristica {
                background-color: #173B5C;
                color: #FF9B43;
                border: 1px solid #315573;
                border-radius: 8px;
                font-size: 11px;
                font-weight: 800;
            }

            QLabel#textoCaracteristica {
                color: #E2EAF2;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#pieIzquierdo {
                color: #91A8BE;
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 1px;
            }

            QFrame#panelDerecho {
                background-color: #F2F5F9;
                border: none;
            }

            QFrame#tarjetaLogin {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 18px;
            }

            QLabel#etiquetaAcceso {
                color: #D66A0A;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 2px;
            }

            QLabel#tituloLogin {
                color: #001F3F;
                font-size: 36px;
                font-weight: 800;
            }

            QLabel#descripcionLogin {
                color: #64748B;
                font-size: 14px;
            }

            QLabel#etiquetaCampo {
                color: #334155;
                font-size: 12px;
                font-weight: 800;
                letter-spacing: 1px;
            }

            QLineEdit#campoLogin {
                background-color: #F8FAFC;
                border: 1px solid #D8E0E9;
                border-radius: 9px;
                padding: 0 16px;
                color: #1E293B;
                font-size: 15px;
                selection-background-color: #1677C8;
            }

            QLineEdit#campoLogin:hover {
                border: 1px solid #A8BBD0;
                background-color: #FFFFFF;
            }

            QLineEdit#campoLogin:focus {
                border: 2px solid #1677C8;
                background-color: #FFFFFF;
            }

            QFrame#contenedorPassword {
                background-color: #F8FAFC;
                border: 1px solid #D8E0E9;
                border-radius: 9px;
            }

            QFrame#contenedorPassword:focus-within {
                border: 2px solid #1677C8;
                background-color: #FFFFFF;
            }

            QLineEdit#campoPassword {
                background-color: transparent;
                border: none;
                padding: 0 16px;
                color: #1E293B;
                font-size: 15px;
            }

            QPushButton#btnVerPassword {
                background-color: transparent;
                color: #64748B;
                border: none;
                font-size: 11px;
                font-weight: 800;
            }

            QPushButton#btnVerPassword:hover {
                color: #1677C8;
            }

            QLabel#lblError {
                color: #DC2626;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#btnIngresar {
                background-color: #003B73;
                color: #FFFFFF;
                border: none;
                border-radius: 9px;
                font-size: 14px;
                font-weight: 800;
                letter-spacing: 1px;
            }

            QPushButton#btnIngresar:hover {
                background-color: #07569B;
            }

            QPushButton#btnIngresar:pressed {
                background-color: #001F3F;
            }

            QPushButton#btnIngresar:disabled {
                background-color: #94A3B8;
                color: #E2E8F0;
            }

            QFrame#separador {
                background-color: #E8EDF3;
                border: none;
            }

            QLabel#pieTarjeta {
                color: #94A3B8;
                font-size: 12px;
            }

            QLabel#pieDerecho {
                color: #94A3B8;
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 1px;
            }
        """)

    # ======================================================
    # MOSTRAR / OCULTAR CONTRASEÑA
    # ======================================================

    def cambiar_visibilidad_password(self, visible):

        if visible:
            self.txt_password.setEchoMode(QLineEdit.Normal)
            self.btn_ver_password.setText("OCULTAR")
        else:
            self.txt_password.setEchoMode(QLineEdit.Password)
            self.btn_ver_password.setText("VER")

    # ======================================================
    # VALIDAR LOGIN
    # ======================================================

    def validar_login(self):

        usuario = self.txt_usuario.text().strip()
        password = self.txt_password.text()

        self.lbl_error.setText("")

        if not usuario or not password:

            self.lbl_error.setText(
                "Ingresa tu usuario y contraseña para continuar."
            )

            if not usuario:
                self.txt_usuario.setFocus()
            else:
                self.txt_password.setFocus()

            return

        # Credenciales provisionales para desarrollo
        if usuario == "admin" and password == "Arkos2026!":

            self.btn_ingresar.setEnabled(False)
            self.btn_ingresar.setText("INICIANDO SESIÓN...")

            self.login_exitoso.emit()

            self.btn_ingresar.setEnabled(True)
            self.btn_ingresar.setText("INICIAR SESIÓN")

        else:

            self.lbl_error.setText(
                "Usuario o contraseña incorrectos."
            )

            self.txt_password.clear()
            self.txt_password.setFocus()
