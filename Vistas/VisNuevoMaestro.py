
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QFormLayout,
    QFrame,
    QSizePolicy,
    QSpacerItem
)

from PySide6.QtCore import Qt, Signal

from Servicios.ServicioAlmacenamiento import registrar_maestro


class VisNuevoMaestro(QWidget):

    maestro_guardado = Signal(dict)
    cancelar_solicitado = Signal()

    def __init__(self):
        super().__init__()

        self.crear_interfaz()
        self.aplicar_estilos()

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(30, 25, 30, 25)
        layout_principal.setSpacing(20)

        # ==================================================
        # ENCABEZADO
        # ==================================================

        encabezado = QHBoxLayout()
        encabezado.setSpacing(15)

        bloque_titulo = QVBoxLayout()
        bloque_titulo.setSpacing(5)

        titulo = QLabel("Registrar maestro")
        titulo.setObjectName("tituloPrincipal")

        descripcion = QLabel(
            "Incorpora un nuevo docente al sistema ARKOS CHECADOR."
        )
        descripcion.setObjectName("descripcionPrincipal")
        descripcion.setWordWrap(True)

        bloque_titulo.addWidget(titulo)
        bloque_titulo.addWidget(descripcion)

        encabezado.addLayout(bloque_titulo)
        encabezado.addStretch()

        etiqueta_estado = QLabel("NUEVO REGISTRO")
        etiqueta_estado.setObjectName("etiquetaEstado")
        etiqueta_estado.setAlignment(Qt.AlignCenter)

        encabezado.addWidget(etiqueta_estado)

        layout_principal.addLayout(encabezado)

        # ==================================================
        # CONTENEDOR DEL FORMULARIO
        # ==================================================

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaFormulario")
        tarjeta.setMaximumWidth(850)
        tarjeta.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        layout_tarjeta = QVBoxLayout(tarjeta)
        layout_tarjeta.setContentsMargins(30, 28, 30, 28)
        layout_tarjeta.setSpacing(22)

        # Encabezado de tarjeta

        encabezado_formulario = QHBoxLayout()

        icono = QLabel("01")
        icono.setObjectName("numeroSeccion")
        icono.setAlignment(Qt.AlignCenter)
        icono.setFixedSize(42, 42)

        textos_formulario = QVBoxLayout()
        textos_formulario.setSpacing(3)

        titulo_formulario = QLabel("Información del docente")
        titulo_formulario.setObjectName("tituloSeccion")

        subtitulo_formulario = QLabel(
            "Completa los datos básicos para dar de alta al maestro."
        )
        subtitulo_formulario.setObjectName("subtituloSeccion")
        subtitulo_formulario.setWordWrap(True)

        textos_formulario.addWidget(titulo_formulario)
        textos_formulario.addWidget(subtitulo_formulario)

        encabezado_formulario.addWidget(icono)
        encabezado_formulario.addLayout(textos_formulario)
        encabezado_formulario.addStretch()

        layout_tarjeta.addLayout(encabezado_formulario)

        separador = QFrame()
        separador.setObjectName("separador")
        separador.setFixedHeight(1)

        layout_tarjeta.addWidget(separador)

        # ==================================================
        # CAMPOS
        # ==================================================

        formulario = QFormLayout()
        formulario.setSpacing(18)
        formulario.setHorizontalSpacing(25)
        formulario.setVerticalSpacing(18)
        formulario.setLabelAlignment(Qt.AlignLeft)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej. Joaquín Martín")
        self.txt_nombre.setMinimumHeight(48)
        self.txt_nombre.setClearButtonEnabled(True)

        self.txt_apellidos = QLineEdit()
        self.txt_apellidos.setPlaceholderText("Ej. Huerta de León")
        self.txt_apellidos.setMinimumHeight(48)
        self.txt_apellidos.setClearButtonEnabled(True)

        formulario.addRow(
            self.crear_etiqueta_campo("Nombre(s)", "Escribe el nombre del docente"),
            self.txt_nombre
        )

        formulario.addRow(
            self.crear_etiqueta_campo("Apellidos", "Escribe los apellidos"),
            self.txt_apellidos
        )

        layout_tarjeta.addLayout(formulario)

        # ==================================================
        # INFORMACIÓN DEL ID
        # ==================================================

        tarjeta_id = QFrame()
        tarjeta_id.setObjectName("tarjetaId")

        layout_id = QHBoxLayout(tarjeta_id)
        layout_id.setContentsMargins(15, 13, 15, 13)
        layout_id.setSpacing(12)

        icono_id = QLabel("ID")
        icono_id.setObjectName("iconoId")
        icono_id.setAlignment(Qt.AlignCenter)
        icono_id.setFixedSize(38, 38)

        textos_id = QVBoxLayout()
        textos_id.setSpacing(3)

        titulo_id = QLabel("Identificador del maestro")
        titulo_id.setObjectName("tituloId")

        self.lbl_id = QLabel(
            "Se generará automáticamente al guardar el registro."
        )
        self.lbl_id.setObjectName("descripcionId")
        self.lbl_id.setWordWrap(True)

        textos_id.addWidget(titulo_id)
        textos_id.addWidget(self.lbl_id)

        layout_id.addWidget(icono_id)
        layout_id.addLayout(textos_id, 1)

        layout_tarjeta.addWidget(tarjeta_id)

        # ==================================================
        # BOTONES
        # ==================================================

        botones = QHBoxLayout()
        botones.setSpacing(12)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btnCancelar")
        self.btn_cancelar.setMinimumHeight(48)
        self.btn_cancelar.setCursor(Qt.PointingHandCursor)

        self.btn_guardar = QPushButton("Guardar maestro")
        self.btn_guardar.setObjectName("btnGuardar")
        self.btn_guardar.setMinimumHeight(48)
        self.btn_guardar.setCursor(Qt.PointingHandCursor)

        botones.addStretch()
        botones.addWidget(self.btn_cancelar)
        botones.addWidget(self.btn_guardar)

        layout_tarjeta.addLayout(botones)

        layout_principal.addWidget(
            tarjeta,
            alignment=Qt.AlignHCenter
        )

        layout_principal.addStretch()

        # ==================================================
        # CONEXIONES
        # ==================================================

        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(
            self.cancelar_solicitado.emit
        )

        self.txt_nombre.returnPressed.connect(
            self.txt_apellidos.setFocus
        )

        self.txt_apellidos.returnPressed.connect(
            self.guardar
        )

    def crear_etiqueta_campo(self, titulo, descripcion):

        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        etiqueta = QLabel(titulo)
        etiqueta.setObjectName("etiquetaCampo")

        ayuda = QLabel(descripcion)
        ayuda.setObjectName("ayudaCampo")
        ayuda.setWordWrap(True)

        layout.addWidget(etiqueta)
        layout.addWidget(ayuda)

        contenedor.setMinimumWidth(190)

        return contenedor

    def aplicar_estilos(self):

        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI";
                color: #243447;
            }

            QWidget#tarjetaFormulario {
                background-color: #FFFFFF;
                border: 1px solid #E1E8F0;
                border-radius: 14px;
            }

            QLabel#tituloPrincipal {
                color: #001F3F;
                font-size: 27px;
                font-weight: 800;
            }

            QLabel#descripcionPrincipal {
                color: #64748B;
                font-size: 13px;
            }

            QLabel#etiquetaEstado {
                background-color: #FFF2E5;
                color: #B85C00;
                border: 1px solid #FFD7B0;
                border-radius: 8px;
                padding: 9px 13px;
                font-size: 10px;
                font-weight: 800;
            }

            QLabel#numeroSeccion {
                background-color: #EAF2FA;
                color: #003B73;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 800;
            }

            QLabel#tituloSeccion {
                color: #001F3F;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#subtituloSeccion {
                color: #64748B;
                font-size: 12px;
            }

            QFrame#separador {
                background-color: #E8EDF3;
                border: none;
            }

            QLabel#etiquetaCampo {
                color: #243447;
                font-size: 13px;
                font-weight: 700;
            }

            QLabel#ayudaCampo {
                color: #8492A6;
                font-size: 11px;
            }

            QLineEdit {
                background-color: #F8FAFC;
                border: 1px solid #D8E0E9;
                border-radius: 8px;
                padding: 0 13px;
                color: #1E293B;
                font-size: 14px;
                selection-background-color: #1677C8;
            }

            QLineEdit:hover {
                border: 1px solid #A8BBD0;
                background-color: #FFFFFF;
            }

            QLineEdit:focus {
                border: 2px solid #1677C8;
                background-color: #FFFFFF;
            }

            QFrame#tarjetaId {
                background-color: #F0F6FC;
                border: 1px solid #D9E8F7;
                border-radius: 10px;
            }

            QLabel#iconoId {
                background-color: #003B73;
                color: #FFFFFF;
                border-radius: 9px;
                font-size: 12px;
                font-weight: 800;
            }

            QLabel#tituloId {
                color: #003B73;
                font-size: 12px;
                font-weight: 700;
            }

            QLabel#descripcionId {
                color: #64748B;
                font-size: 11px;
            }

            QPushButton {
                border-radius: 8px;
                padding: 0 22px;
                font-size: 13px;
                font-weight: 700;
            }

            QPushButton#btnGuardar {
                background-color: #003B73;
                color: #FFFFFF;
                border: none;
                min-width: 170px;
            }

            QPushButton#btnGuardar:hover {
                background-color: #07569B;
            }

            QPushButton#btnGuardar:pressed {
                background-color: #001F3F;
            }

            QPushButton#btnGuardar:disabled {
                background-color: #94A3B8;
                color: #E2E8F0;
            }

            QPushButton#btnCancelar {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                min-width: 110px;
            }

            QPushButton#btnCancelar:hover {
                background-color: #F1F5F9;
                border-color: #94A3B8;
            }

            QPushButton#btnCancelar:disabled {
                color: #94A3B8;
                background-color: #F1F5F9;
            }
        """)

    def guardar(self):

        nombre = self.txt_nombre.text().strip()
        apellidos = self.txt_apellidos.text().strip()

        if not nombre or not apellidos:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes ingresar el nombre y los apellidos del maestro."
            )

            if not nombre:
                self.txt_nombre.setFocus()
            else:
                self.txt_apellidos.setFocus()

            return

        self.btn_guardar.setEnabled(False)
        self.btn_cancelar.setEnabled(False)
        self.btn_guardar.setText("Guardando...")

        try:
            maestro = registrar_maestro(nombre, apellidos)

            self.lbl_id.setText(
                f"ID asignado correctamente: {maestro['id']}"
            )

            QMessageBox.information(
                self,
                "Registro exitoso",
                "El maestro se registró correctamente.\n\n"
                f"Nombre: {maestro['nombre']} {maestro['apellidos']}\n"
                f"ID: {maestro['id']}"
            )

            self.txt_nombre.clear()
            self.txt_apellidos.clear()

            self.maestro_guardado.emit(maestro)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error de registro",
                f"No se pudo registrar al maestro:\n\n{error}"
            )

        finally:
            self.btn_guardar.setEnabled(True)
            self.btn_cancelar.setEnabled(True)
            self.btn_guardar.setText("Guardar maestro")
