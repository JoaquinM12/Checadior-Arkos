
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QFormLayout,
    QCheckBox,
    QFrame,
    QSizePolicy
)

from PySide6.QtCore import Qt, Signal

from Servicios.ServicioAlmacenamiento import actualizar_maestro


class VisEditarMaestro(QWidget):

    maestro_actualizado = Signal(dict)
    cancelar_solicitado = Signal()

    def __init__(self, maestro):
        super().__init__()

        self.maestro = maestro

        self.crear_interfaz()
        self.cargar_datos()
        self.aplicar_estilos()

    # ======================================================
    # INTERFAZ
    # ======================================================

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(30, 25, 30, 25)
        layout_principal.setSpacing(20)

        # ENCABEZADO
        encabezado = QHBoxLayout()
        encabezado.setSpacing(15)

        bloque_titulo = QVBoxLayout()
        bloque_titulo.setSpacing(5)

        titulo = QLabel("Editar maestro")
        titulo.setObjectName("tituloPrincipal")

        descripcion = QLabel(
            "Actualiza la información y el estado del docente seleccionado."
        )
        descripcion.setObjectName("descripcionPrincipal")
        descripcion.setWordWrap(True)

        bloque_titulo.addWidget(titulo)
        bloque_titulo.addWidget(descripcion)

        encabezado.addLayout(bloque_titulo)
        encabezado.addStretch()

        self.lbl_estado = QLabel("EDICIÓN DE REGISTRO")
        self.lbl_estado.setObjectName("etiquetaEstado")
        self.lbl_estado.setAlignment(Qt.AlignCenter)

        encabezado.addWidget(self.lbl_estado)

        layout_principal.addLayout(encabezado)

        # TARJETA PRINCIPAL
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

        # TÍTULO DE SECCIÓN
        encabezado_formulario = QHBoxLayout()

        numero = QLabel("01")
        numero.setObjectName("numeroSeccion")
        numero.setAlignment(Qt.AlignCenter)
        numero.setFixedSize(42, 42)

        textos = QVBoxLayout()
        textos.setSpacing(3)

        titulo_formulario = QLabel("Información del docente")
        titulo_formulario.setObjectName("tituloSeccion")

        subtitulo = QLabel(
            "Los datos identifican al maestro dentro del sistema."
        )
        subtitulo.setObjectName("subtituloSeccion")
        subtitulo.setWordWrap(True)

        textos.addWidget(titulo_formulario)
        textos.addWidget(subtitulo)

        encabezado_formulario.addWidget(numero)
        encabezado_formulario.addLayout(textos)
        encabezado_formulario.addStretch()

        layout_tarjeta.addLayout(encabezado_formulario)

        separador = QFrame()
        separador.setObjectName("separador")
        separador.setFixedHeight(1)

        layout_tarjeta.addWidget(separador)

        # FORMULARIO
        formulario = QFormLayout()
        formulario.setSpacing(18)
        formulario.setHorizontalSpacing(25)
        formulario.setVerticalSpacing(18)
        formulario.setLabelAlignment(Qt.AlignLeft)

        self.txt_id = QLineEdit()
        self.txt_id.setReadOnly(True)
        self.txt_id.setMinimumHeight(46)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej. Joaquín Martín")
        self.txt_nombre.setMinimumHeight(46)
        self.txt_nombre.setClearButtonEnabled(True)

        self.txt_apellidos = QLineEdit()
        self.txt_apellidos.setPlaceholderText("Ej. Huerta de León")
        self.txt_apellidos.setMinimumHeight(46)
        self.txt_apellidos.setClearButtonEnabled(True)

        formulario.addRow(
            self.crear_etiqueta_campo(
                "Identificador",
                "Código único del docente"
            ),
            self.txt_id
        )

        formulario.addRow(
            self.crear_etiqueta_campo(
                "Nombre(s)",
                "Nombre del maestro"
            ),
            self.txt_nombre
        )

        formulario.addRow(
            self.crear_etiqueta_campo(
                "Apellidos",
                "Apellidos del maestro"
            ),
            self.txt_apellidos
        )

        layout_tarjeta.addLayout(formulario)

        # ESTADO DEL MAESTRO
        separador_estado = QFrame()
        separador_estado.setObjectName("separador")
        separador_estado.setFixedHeight(1)

        layout_tarjeta.addWidget(separador_estado)

        encabezado_estado = QVBoxLayout()
        encabezado_estado.setSpacing(4)

        titulo_estado = QLabel("Estado del docente")
        titulo_estado.setObjectName("tituloSeccion")

        ayuda_estado = QLabel(
            "Controla si el maestro puede aparecer en las asignaciones activas."
        )
        ayuda_estado.setObjectName("subtituloSeccion")
        ayuda_estado.setWordWrap(True)

        encabezado_estado.addWidget(titulo_estado)
        encabezado_estado.addWidget(ayuda_estado)

        layout_tarjeta.addLayout(encabezado_estado)

        tarjeta_estado = QFrame()
        tarjeta_estado.setObjectName("tarjetaEstado")

        layout_estado = QHBoxLayout(tarjeta_estado)
        layout_estado.setContentsMargins(16, 13, 16, 13)
        layout_estado.setSpacing(12)

        self.chk_activo = QCheckBox()
        self.chk_activo.setObjectName("checkActivo")
        self.chk_activo.setCursor(Qt.PointingHandCursor)

        textos_estado = QVBoxLayout()
        textos_estado.setSpacing(3)

        self.lbl_estado_maestro = QLabel("Maestro activo")
        self.lbl_estado_maestro.setObjectName("tituloEstado")

        self.lbl_descripcion_estado = QLabel(
            "El docente está habilitado en el sistema."
        )
        self.lbl_descripcion_estado.setObjectName("descripcionEstado")
        self.lbl_descripcion_estado.setWordWrap(True)

        textos_estado.addWidget(self.lbl_estado_maestro)
        textos_estado.addWidget(self.lbl_descripcion_estado)

        layout_estado.addWidget(self.chk_activo)
        layout_estado.addLayout(textos_estado, 1)

        layout_tarjeta.addWidget(tarjeta_estado)

        self.chk_activo.toggled.connect(
            self.actualizar_texto_estado
        )

        # BOTONES
        botones = QHBoxLayout()
        botones.setSpacing(12)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btnCancelar")
        self.btn_cancelar.setMinimumHeight(48)
        self.btn_cancelar.setCursor(Qt.PointingHandCursor)

        self.btn_guardar = QPushButton("Guardar cambios")
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

        # CONEXIONES
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

    # ======================================================
    # ETIQUETAS
    # ======================================================

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

    # ======================================================
    # CARGAR DATOS
    # ======================================================

    def cargar_datos(self):

        self.txt_id.setText(
            str(self.maestro.get("id", ""))
        )

        self.txt_nombre.setText(
            str(self.maestro.get("nombre", ""))
        )

        self.txt_apellidos.setText(
            str(self.maestro.get("apellidos", ""))
        )

        self.chk_activo.setChecked(
            self.maestro.get("activo", True)
        )

        self.actualizar_texto_estado(
            self.chk_activo.isChecked()
        )

    # ======================================================
    # ESTADO
    # ======================================================

    def actualizar_texto_estado(self, activo):

        if activo:
            self.lbl_estado_maestro.setText("Maestro activo")
            self.lbl_descripcion_estado.setText(
                "El docente está habilitado en el sistema."
            )
        else:
            self.lbl_estado_maestro.setText("Maestro inactivo")
            self.lbl_descripcion_estado.setText(
                "El docente no estará disponible para nuevas asignaciones."
            )

    # ======================================================
    # ESTILOS
    # ======================================================

    def aplicar_estilos(self):

        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI";
                color: #243447;
            }

            QFrame#tarjetaFormulario {
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
                background-color: #EAF2FA;
                color: #003B73;
                border: 1px solid #C9DDF1;
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
                font-size: 16px;
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

            QLineEdit:read-only {
                background-color: #EDF2F7;
                color: #64748B;
                border: 1px solid #D8E0E9;
                font-weight: 700;
            }

            QFrame#tarjetaEstado {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }

            QCheckBox#checkActivo {
                spacing: 8px;
            }

            QCheckBox#checkActivo::indicator {
                width: 22px;
                height: 22px;
                border: 1px solid #94A3B8;
                border-radius: 6px;
                background-color: #FFFFFF;
            }

            QCheckBox#checkActivo::indicator:hover {
                border: 1px solid #1677C8;
            }

            QCheckBox#checkActivo::indicator:checked {
                background-color: #16834A;
                border: 1px solid #16834A;
            }

            QLabel#tituloEstado {
                color: #243447;
                font-size: 13px;
                font-weight: 700;
            }

            QLabel#descripcionEstado {
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

    # ======================================================
    # GUARDAR CAMBIOS
    # ======================================================

    def guardar(self):

        nombre = self.txt_nombre.text().strip()
        apellidos = self.txt_apellidos.text().strip()
        activo = self.chk_activo.isChecked()

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

        respuesta = QMessageBox.question(
            self,
            "Confirmar cambios",
            "¿Deseas guardar los cambios del maestro?\n\n"
            f"Maestro: {nombre} {apellidos}\n"
            f"Estado: {'Activo' if activo else 'Inactivo'}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        self.btn_guardar.setEnabled(False)
        self.btn_cancelar.setEnabled(False)
        self.btn_guardar.setText("Guardando...")

        try:

            maestro_actualizado = actualizar_maestro(
                self.maestro["id"],
                nombre,
                apellidos,
                activo
            )

            QMessageBox.information(
                self,
                "Actualización exitosa",
                "Los datos del maestro se actualizaron correctamente."
            )

            self.maestro_actualizado.emit(maestro_actualizado)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error de actualización",
                f"No se pudieron actualizar los datos:\n\n{error}"
            )

        finally:
            self.btn_guardar.setEnabled(True)
            self.btn_cancelar.setEnabled(True)
            self.btn_guardar.setText("Guardar cambios")
