
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QSizePolicy
)

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from Servicios.ServicioAlmacenamiento import cargar_maestros


class VisMaestros(QWidget):

    nuevo_maestro_solicitado = Signal()
    registro_rostro_solicitado = Signal(dict)
    editar_maestro_solicitado = Signal(dict)

    def __init__(self):
        super().__init__()

        self.maestros = []

        self.crear_interfaz()
        self.actualizar_lista()

    # =====================================================
    # INTERFAZ PRINCIPAL
    # =====================================================

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 22, 25, 22)
        layout_principal.setSpacing(18)

        # =================================================
        # ENCABEZADO
        # =================================================

        encabezado = QHBoxLayout()
        encabezado.setSpacing(15)

        contenedor_titulo = QVBoxLayout()
        contenedor_titulo.setSpacing(5)

        titulo = QLabel("Maestros")
        titulo.setStyleSheet("""
            font-size: 27px;
            font-weight: 800;
            color: #001F3F;
        """)

        descripcion = QLabel(
            "Administra la información y el registro facial del personal docente."
        )
        descripcion.setStyleSheet("""
            font-size: 13px;
            color: #64748B;
        """)

        contenedor_titulo.addWidget(titulo)
        contenedor_titulo.addWidget(descripcion)

        encabezado.addLayout(contenedor_titulo)
        encabezado.addStretch()

        self.btn_nuevo = QPushButton("+  Nuevo maestro")
        self.btn_nuevo.setMinimumHeight(43)
        self.btn_nuevo.setMinimumWidth(165)
        self.btn_nuevo.setCursor(Qt.PointingHandCursor)
        self.btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: #003B73;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0px 18px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1677C8;
            }

            QPushButton:pressed {
                background-color: #001F3F;
            }
        """)

        encabezado.addWidget(self.btn_nuevo)

        layout_principal.addLayout(encabezado)

        # =================================================
        # INDICADORES
        # =================================================

        indicadores = QGridLayout()
        indicadores.setSpacing(13)

        self.card_total, self.lbl_total = self.crear_tarjeta_indicador(
            "TOTAL DE MAESTROS",
            "0",
            "#003B73",
            "#EAF2FA"
        )

        self.card_activos, self.lbl_activos = self.crear_tarjeta_indicador(
            "MAESTROS ACTIVOS",
            "0",
            "#15803D",
            "#EAF7EF"
        )

        self.card_inactivos, self.lbl_inactivos = self.crear_tarjeta_indicador(
            "MAESTROS INACTIVOS",
            "0",
            "#D97706",
            "#FFF7E8"
        )

        indicadores.addWidget(self.card_total, 0, 0)
        indicadores.addWidget(self.card_activos, 0, 1)
        indicadores.addWidget(self.card_inactivos, 0, 2)

        indicadores.setColumnStretch(0, 1)
        indicadores.setColumnStretch(1, 1)
        indicadores.setColumnStretch(2, 1)

        layout_principal.addLayout(indicadores)

        # =================================================
        # CONTENEDOR DE TABLA
        # =================================================

        contenedor_tabla = QFrame()
        contenedor_tabla.setObjectName("contenedorTabla")

        contenedor_tabla.setStyleSheet("""
            QFrame#contenedorTabla {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)

        layout_tabla = QVBoxLayout(contenedor_tabla)
        layout_tabla.setContentsMargins(18, 17, 18, 15)
        layout_tabla.setSpacing(14)

        # =================================================
        # ENCABEZADO DE TABLA
        # =================================================

        encabezado_tabla = QHBoxLayout()

        titulo_tabla = QLabel("Directorio de maestros")
        titulo_tabla.setStyleSheet("""
            font-size: 17px;
            font-weight: bold;
            color: #001F3F;
            border: none;
        """)

        encabezado_tabla.addWidget(titulo_tabla)
        encabezado_tabla.addStretch()

        self.lbl_resultados = QLabel("0 registros")
        self.lbl_resultados.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #64748B;
            border: none;
        """)

        encabezado_tabla.addWidget(self.lbl_resultados)

        layout_tabla.addLayout(encabezado_tabla)

        # =================================================
        # BUSCADOR
        # =================================================

        barra_busqueda = QHBoxLayout()
        barra_busqueda.setSpacing(10)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar por nombre, apellidos o ID del maestro..."
        )
        self.txt_buscar.setMinimumHeight(42)
        self.txt_buscar.setClearButtonEnabled(True)

        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAFC;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
                padding: 0px 13px;
                font-size: 13px;
            }

            QLineEdit:focus {
                border: 1px solid #1677C8;
                background-color: white;
            }
        """)

        barra_busqueda.addWidget(self.txt_buscar)

        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.setMinimumHeight(42)
        self.btn_actualizar.setMinimumWidth(115)
        self.btn_actualizar.setCursor(Qt.PointingHandCursor)

        self.btn_actualizar.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #334155;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
                padding: 0px 14px;
                font-size: 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)

        barra_busqueda.addWidget(self.btn_actualizar)

        layout_tabla.addLayout(barra_busqueda)

        # =================================================
        # TABLA DE MAESTROS
        # =================================================

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(5)

        self.tabla.setHorizontalHeaderLabels([
            "ID",
            "Nombre",
            "Apellidos",
            "Estado",
            "Fecha de registro"
        ])

        self.tabla.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabla.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.tabla.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)
        self.tabla.setWordWrap(False)

        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(48)

        encabezado_horizontal = self.tabla.horizontalHeader()

        encabezado_horizontal.setSectionResizeMode(
            QHeaderView.Stretch
        )

        encabezado_horizontal.setMinimumSectionSize(75)

        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #F8FAFC;
                color: #1E293B;
                border: none;
                font-size: 13px;
                selection-background-color: #DBEAFE;
                selection-color: #001F3F;
                outline: none;
            }

            QHeaderView::section {
                background-color: #F1F5F9;
                color: #334155;
                padding: 13px 8px;
                border: none;
                border-bottom: 2px solid #CBD5E1;
                font-size: 11px;
                font-weight: bold;
            }

            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F1F5F9;
            }

            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #001F3F;
            }

            QScrollBar:vertical {
                background-color: #F8FAFC;
                width: 9px;
                margin: 0px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical {
                background-color: #CBD5E1;
                min-height: 25px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #94A3B8;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.tabla.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        layout_tabla.addWidget(self.tabla, 1)

        # =================================================
        # PIE DE TABLA
        # =================================================

        pie_tabla = QHBoxLayout()

        self.lbl_estado = QLabel(
            "Selecciona un maestro para ver sus acciones disponibles."
        )

        self.lbl_estado.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            border: none;
        """)

        pie_tabla.addWidget(self.lbl_estado)
        pie_tabla.addStretch()

        layout_tabla.addLayout(pie_tabla)

        layout_principal.addWidget(contenedor_tabla, 1)

        # =================================================
        # ACCIONES
        # =================================================

        contenedor_acciones = QFrame()
        contenedor_acciones.setObjectName("contenedorAcciones")

        contenedor_acciones.setStyleSheet("""
            QFrame#contenedorAcciones {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
        """)

        layout_acciones = QHBoxLayout(contenedor_acciones)
        layout_acciones.setContentsMargins(14, 11, 14, 11)
        layout_acciones.setSpacing(10)

        etiqueta_acciones = QLabel("ACCIONES:")
        etiqueta_acciones.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            font-weight: bold;
            border: none;
        """)

        layout_acciones.addWidget(etiqueta_acciones)
        layout_acciones.addStretch()

        self.btn_editar = QPushButton("Editar maestro")
        self.btn_rostro = QPushButton("Registrar rostro")

        for boton in (self.btn_editar, self.btn_rostro):
            boton.setMinimumHeight(39)
            boton.setMinimumWidth(145)
            boton.setCursor(Qt.PointingHandCursor)

        self.btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #FFF7E8;
                color: #B45309;
                border: 1px solid #FDE0A7;
                border-radius: 7px;
                padding: 0px 14px;
                font-size: 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #FEF0CE;
            }

            QPushButton:disabled {
                background-color: #F1F5F9;
                color: #94A3B8;
                border: 1px solid #E2E8F0;
            }
        """)

        self.btn_rostro.setStyleSheet("""
            QPushButton {
                background-color: #EAF7EF;
                color: #15803D;
                border: 1px solid #BBE5C9;
                border-radius: 7px;
                padding: 0px 14px;
                font-size: 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #D7F0DF;
            }

            QPushButton:disabled {
                background-color: #F1F5F9;
                color: #94A3B8;
                border: 1px solid #E2E8F0;
            }
        """)

        layout_acciones.addWidget(self.btn_editar)
        layout_acciones.addWidget(self.btn_rostro)

        layout_principal.addWidget(contenedor_acciones)

        # =================================================
        # CONEXIONES
        # =================================================

        self.btn_nuevo.clicked.connect(
            self.nuevo_maestro_solicitado.emit
        )

        self.btn_actualizar.clicked.connect(
            self.actualizar_lista
        )

        self.btn_editar.clicked.connect(
            self.abrir_edicion_maestro
        )

        self.btn_rostro.clicked.connect(
            self.abrir_registro_rostro
        )

        self.txt_buscar.textChanged.connect(
            self.filtrar_maestros
        )

        self.tabla.itemSelectionChanged.connect(
            self.actualizar_botones
        )

        self.btn_editar.setEnabled(False)
        self.btn_rostro.setEnabled(False)

    # =====================================================
    # TARJETAS DE INDICADORES
    # =====================================================

    def crear_tarjeta_indicador(
        self,
        titulo,
        valor,
        color,
        fondo
    ):

        tarjeta = QFrame()
        tarjeta.setMinimumHeight(105)
        tarjeta.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        tarjeta.setStyleSheet(f"""
            QFrame {{
                background-color: {fondo};
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(17, 13, 17, 13)
        layout.setSpacing(5)

        etiqueta = QLabel(titulo)
        etiqueta.setStyleSheet(f"""
            color: {color};
            font-size: 10px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)

        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet(f"""
            color: {color};
            font-size: 27px;
            font-weight: 800;
            border: none;
            background: transparent;
        """)

        layout.addWidget(etiqueta)
        layout.addWidget(lbl_valor)
        layout.addStretch()

        return tarjeta, lbl_valor

    # =====================================================
    # ACTUALIZAR LISTA
    # =====================================================

    def actualizar_lista(self):

        try:

            self.maestros = cargar_maestros() or []

            self.txt_buscar.clear()

            self.actualizar_indicadores()
            self.mostrar_maestros_en_tabla(self.maestros)

            self.tabla.clearSelection()
            self.tabla.setCurrentCell(-1, -1)

            self.actualizar_botones()

            self.lbl_estado.setText(
                "Selecciona un maestro para ver sus acciones disponibles."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al cargar maestros",
                f"No se pudo cargar la lista de maestros:\n\n{error}"
            )

    # =====================================================
    # ACTUALIZAR INDICADORES
    # =====================================================

    def actualizar_indicadores(self):

        total = len(self.maestros)

        activos = sum(
            1 for maestro in self.maestros
            if maestro.get("activo", True)
        )

        inactivos = total - activos

        self.lbl_total.setText(str(total))
        self.lbl_activos.setText(str(activos))
        self.lbl_inactivos.setText(str(inactivos))

    # =====================================================
    # MOSTRAR MAESTROS EN TABLA
    # =====================================================

    def mostrar_maestros_en_tabla(self, maestros):

        self.tabla.blockSignals(True)

        try:

            self.tabla.clearContents()
            self.tabla.setRowCount(len(maestros))

            for fila, maestro in enumerate(maestros):

                id_maestro = maestro.get("id", "")
                nombre = maestro.get("nombre", "")
                apellidos = maestro.get("apellidos", "")
                activo = maestro.get("activo", True)
                fecha = maestro.get("fecha_registro", "")

                estado = "ACTIVO" if activo else "INACTIVO"

                valores = [
                    id_maestro,
                    nombre,
                    apellidos,
                    estado,
                    fecha
                ]

                for columna, valor in enumerate(valores):

                    elemento = QTableWidgetItem(str(valor))

                    elemento.setTextAlignment(Qt.AlignCenter)

                    if columna == 0:
                        elemento.setForeground(
                            QColor("#003B73")
                        )
                        elemento.setFont(
                            self.tabla.font()
                        )

                    if columna == 3:

                        elemento.setTextAlignment(Qt.AlignCenter)

                        if activo:
                            elemento.setForeground(
                                QColor("#15803D")
                            )
                        else:
                            elemento.setForeground(
                                QColor("#D97706")
                            )

                    self.tabla.setItem(
                        fila,
                        columna,
                        elemento
                    )

            self.lbl_resultados.setText(
                f"{len(maestros)} registros"
            )

        finally:

            self.tabla.blockSignals(False)

    # =====================================================
    # BUSCADOR
    # =====================================================

    def filtrar_maestros(self, texto):

        texto = texto.strip().lower()

        if not texto:

            filtrados = self.maestros

        else:

            filtrados = []

            for maestro in self.maestros:

                id_maestro = str(
                    maestro.get("id", "")
                ).lower()

                nombre = str(
                    maestro.get("nombre", "")
                ).lower()

                apellidos = str(
                    maestro.get("apellidos", "")
                ).lower()

                nombre_completo = f"{nombre} {apellidos}"

                if (
                    texto in id_maestro
                    or texto in nombre
                    or texto in apellidos
                    or texto in nombre_completo
                ):

                    filtrados.append(maestro)

        self.mostrar_maestros_en_tabla(filtrados)

        self.tabla.clearSelection()
        self.tabla.setCurrentCell(-1, -1)

        self.actualizar_botones()

        if texto:
            self.lbl_estado.setText(
                f"Resultados de búsqueda: {len(filtrados)} maestro(s)."
            )
        else:
            self.lbl_estado.setText(
                "Selecciona un maestro para ver sus acciones disponibles."
            )

    # =====================================================
    # OBTENER MAESTRO SELECCIONADO
    # =====================================================

    def obtener_maestro_seleccionado(self):

        fila = self.tabla.currentRow()

        if fila < 0:
            return None

        elemento = self.tabla.item(fila, 0)

        if elemento is None:
            return None

        id_maestro = elemento.text()

        for maestro in self.maestros:

            if maestro.get("id") == id_maestro:
                return maestro

        return None

    # =====================================================
    # ACTUALIZAR BOTONES
    # =====================================================

    def actualizar_botones(self):

        maestro = self.obtener_maestro_seleccionado()

        seleccionado = maestro is not None

        self.btn_editar.setEnabled(seleccionado)

        self.btn_rostro.setEnabled(
            seleccionado and maestro.get("activo", True)
        )

        if seleccionado:

            nombre = maestro.get("nombre", "")
            apellidos = maestro.get("apellidos", "")

            self.lbl_estado.setText(
                f"Maestro seleccionado: {nombre} {apellidos}"
            )

        else:

            self.lbl_estado.setText(
                "Selecciona un maestro para ver sus acciones disponibles."
            )

    # =====================================================
    # ABRIR EDICIÓN
    # =====================================================

    def abrir_edicion_maestro(self):

        maestro = self.obtener_maestro_seleccionado()

        if maestro is None:

            QMessageBox.warning(
                self,
                "Selecciona un maestro",
                "Primero debes seleccionar un maestro de la tabla."
            )

            return

        self.editar_maestro_solicitado.emit(
            maestro.copy()
        )

    # =====================================================
    # ABRIR REGISTRO FACIAL
    # =====================================================

    def abrir_registro_rostro(self):

        maestro = self.obtener_maestro_seleccionado()

        if maestro is None:

            QMessageBox.warning(
                self,
                "Selecciona un maestro",
                "Primero debes seleccionar un maestro."
            )

            return

        if not maestro.get("activo", True):

            QMessageBox.warning(
                self,
                "Maestro inactivo",
                "No puedes registrar rostros de un maestro inactivo."
            )

            return

        self.registro_rostro_solicitado.emit({
            "id": maestro.get("id"),
            "nombre": maestro.get("nombre"),
            "apellidos": maestro.get("apellidos")
        })
