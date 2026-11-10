
# ==========================================================
# VISTA DE MATERIAS
# Archivo: Vistas/VisMaterias.py
# ==========================================================

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFrame,
    QAbstractItemView,
    QSizePolicy
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from Configuracion.Firebase import db

from Servicios.ServicioMaterias import (
    registrar_materia,
    cargar_materias,
    actualizar_materia,
    desactivar_materia
)


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

COLECCION_MATERIAS = "tblMaterias"
COLECCION_HORARIOS = "tblHorarios"

CARRERAS = {
    "LAET": "Administración de Empresas Turísticas",
    "LCON": "Contaduría",
    "LDER": "Derecho"
}

CUATRIMESTRES = [
    "PRIMERO",
    "SEGUNDO",
    "TERCERO",
    "CUARTO",
    "QUINTO",
    "SEXTO",
    "SÉPTIMO",
    "OCTAVO",
    "NOVENO"
]


# ==========================================================
# VISTA
# ==========================================================

class VisMaterias(QWidget):

    def __init__(self):

        super().__init__()

        self.materias = []
        self.materias_filtradas = []
        self.materia_seleccionada = None

        self.crear_interfaz()
        self.cargar_lista_materias()

    # ======================================================
    # INTERFAZ PRINCIPAL
    # ======================================================

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)

        layout_principal.setContentsMargins(
            25, 22, 25, 22
        )

        layout_principal.setSpacing(17)

        # ==================================================
        # ENCABEZADO
        # ==================================================

        encabezado = QHBoxLayout()
        encabezado.setSpacing(15)

        bloque_titulo = QVBoxLayout()
        bloque_titulo.setSpacing(5)

        titulo = QLabel("Materias")

        titulo.setStyleSheet("""
            font-size: 27px;
            font-weight: 800;
            color: #001F3F;
        """)

        subtitulo = QLabel(
            "Administra las materias de los programas académicos de ARKOS."
        )

        subtitulo.setStyleSheet("""
            font-size: 13px;
            color: #64748B;
        """)

        bloque_titulo.addWidget(titulo)
        bloque_titulo.addWidget(subtitulo)

        encabezado.addLayout(bloque_titulo)
        encabezado.addStretch()

        self.lbl_estado_general = QLabel("PLAN ACADÉMICO")
        self.lbl_estado_general.setAlignment(Qt.AlignCenter)
        self.lbl_estado_general.setMinimumHeight(32)

        self.lbl_estado_general.setStyleSheet("""
            QLabel {
                background-color: #EAF2FA;
                color: #003B73;
                border: 1px solid #C9DDF0;
                border-radius: 7px;
                padding: 5px 13px;
                font-size: 10px;
                font-weight: bold;
            }
        """)

        encabezado.addWidget(self.lbl_estado_general)

        layout_principal.addLayout(encabezado)

        # ==================================================
        # INDICADORES
        # ==================================================

        indicadores = QGridLayout()
        indicadores.setSpacing(13)

        self.card_total, self.lbl_total = self.crear_tarjeta_indicador(
            "TOTAL DE MATERIAS",
            "0",
            "#003B73",
            "#EAF2FA"
        )

        self.card_activas, self.lbl_activas = self.crear_tarjeta_indicador(
            "MATERIAS ACTIVAS",
            "0",
            "#15803D",
            "#EAF7EF"
        )

        self.card_inactivas, self.lbl_inactivas = self.crear_tarjeta_indicador(
            "MATERIAS INACTIVAS",
            "0",
            "#D97706",
            "#FFF7E8"
        )

        indicadores.addWidget(self.card_total, 0, 0)
        indicadores.addWidget(self.card_activas, 0, 1)
        indicadores.addWidget(self.card_inactivas, 0, 2)

        for columna in range(3):
            indicadores.setColumnStretch(columna, 1)

        layout_principal.addLayout(indicadores)

        # ==================================================
        # FORMULARIO
        # ==================================================

        self.marco_formulario = QFrame()
        self.marco_formulario.setObjectName("marcoFormulario")

        layout_formulario = QVBoxLayout(self.marco_formulario)
        layout_formulario.setContentsMargins(18, 15, 18, 15)
        layout_formulario.setSpacing(13)

        encabezado_formulario = QHBoxLayout()

        bloque_formulario = QVBoxLayout()
        bloque_formulario.setSpacing(4)

        titulo_formulario = QLabel("Datos de la materia")
        titulo_formulario.setStyleSheet("""
            color: #001F3F;
            font-size: 17px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)

        descripcion_formulario = QLabel(
            "Registra una nueva materia o selecciona una para modificarla."
        )

        descripcion_formulario.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            border: none;
            background: transparent;
        """)

        bloque_formulario.addWidget(titulo_formulario)
        bloque_formulario.addWidget(descripcion_formulario)

        encabezado_formulario.addLayout(bloque_formulario)
        encabezado_formulario.addStretch()

        self.lbl_modo = QLabel("NUEVO REGISTRO")
        self.lbl_modo.setAlignment(Qt.AlignCenter)
        self.lbl_modo.setStyleSheet("""
            background-color: #EAF2FA;
            color: #003B73;
            border-radius: 6px;
            padding: 6px 11px;
            font-size: 10px;
            font-weight: bold;
        """)

        encabezado_formulario.addWidget(self.lbl_modo)

        layout_formulario.addLayout(encabezado_formulario)

        # CAMPOS

        formulario = QGridLayout()
        formulario.setHorizontalSpacing(15)
        formulario.setVerticalSpacing(7)

        etiqueta_nombre = QLabel("Nombre de la materia")
        etiqueta_carrera = QLabel("Carrera")
        etiqueta_cuatrimestre = QLabel("Cuatrimestre")

        for etiqueta in (
            etiqueta_nombre,
            etiqueta_carrera,
            etiqueta_cuatrimestre
        ):
            etiqueta.setStyleSheet("""
                color: #334155;
                font-size: 11px;
                font-weight: bold;
                border: none;
                background: transparent;
            """)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText(
            "Ej. Administración de empresas"
        )
        self.txt_nombre.setMinimumHeight(41)

        self.cmb_carrera = QComboBox()
        self.cmb_carrera.setMinimumHeight(41)

        for clave, nombre in CARRERAS.items():
            self.cmb_carrera.addItem(
                f"{clave} - {nombre}",
                clave
            )

        self.cmb_cuatrimestre = QComboBox()
        self.cmb_cuatrimestre.setMinimumHeight(41)
        self.cmb_cuatrimestre.addItems(CUATRIMESTRES)

        formulario.addWidget(etiqueta_nombre, 0, 0)
        formulario.addWidget(etiqueta_carrera, 0, 1)
        formulario.addWidget(etiqueta_cuatrimestre, 0, 2)

        formulario.addWidget(self.txt_nombre, 1, 0)
        formulario.addWidget(self.cmb_carrera, 1, 1)
        formulario.addWidget(self.cmb_cuatrimestre, 1, 2)

        formulario.setColumnStretch(0, 2)
        formulario.setColumnStretch(1, 2)
        formulario.setColumnStretch(2, 1)

        layout_formulario.addLayout(formulario)

        # ==================================================
        # BOTONES DEL FORMULARIO
        # ==================================================

        fila_botones = QHBoxLayout()
        fila_botones.setSpacing(9)

        self.btn_registrar = QPushButton("+ Agregar materia")
        self.btn_modificar = QPushButton("Guardar cambios")
        self.btn_desactivar = QPushButton("Desactivar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_limpiar = QPushButton("Limpiar")

        self.configurar_boton(
            self.btn_registrar,
            "#003B73",
            "#1677C8"
        )

        self.configurar_boton(
            self.btn_modificar,
            "#D97706",
            "#B45309"
        )

        self.configurar_boton(
            self.btn_desactivar,
            "#64748B",
            "#475569"
        )

        self.configurar_boton(
            self.btn_eliminar,
            "#B91C1C",
            "#991B1B"
        )

        self.configurar_boton(
            self.btn_limpiar,
            "#E2E8F0",
            "#CBD5E1",
            "#334155"
        )

        for boton in (
            self.btn_registrar,
            self.btn_modificar,
            self.btn_desactivar,
            self.btn_eliminar,
            self.btn_limpiar
        ):
            boton.setMinimumHeight(39)

        fila_botones.addWidget(self.btn_registrar)
        fila_botones.addWidget(self.btn_modificar)
        fila_botones.addWidget(self.btn_desactivar)
        fila_botones.addWidget(self.btn_eliminar)
        fila_botones.addStretch()
        fila_botones.addWidget(self.btn_limpiar)

        layout_formulario.addLayout(fila_botones)

        layout_principal.addWidget(self.marco_formulario)

        # ==================================================
        # DIRECTORIO DE MATERIAS
        # ==================================================

        marco_tabla = QFrame()
        marco_tabla.setObjectName("marcoTabla")

        layout_tabla = QVBoxLayout(marco_tabla)
        layout_tabla.setContentsMargins(18, 15, 18, 15)
        layout_tabla.setSpacing(12)

        encabezado_tabla = QHBoxLayout()

        bloque_titulo_tabla = QVBoxLayout()
        bloque_titulo_tabla.setSpacing(4)

        titulo_tabla = QLabel("Directorio de materias")
        titulo_tabla.setStyleSheet("""
            color: #001F3F;
            font-size: 17px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)

        subtitulo_tabla = QLabel(
            "Consulta las materias registradas en los programas académicos."
        )

        subtitulo_tabla.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            border: none;
            background: transparent;
        """)

        bloque_titulo_tabla.addWidget(titulo_tabla)
        bloque_titulo_tabla.addWidget(subtitulo_tabla)

        encabezado_tabla.addLayout(bloque_titulo_tabla)
        encabezado_tabla.addStretch()

        self.lbl_resultados = QLabel("0 registros")
        self.lbl_resultados.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)

        encabezado_tabla.addWidget(self.lbl_resultados)

        layout_tabla.addLayout(encabezado_tabla)

        # ==================================================
        # BUSCADOR Y FILTROS
        # ==================================================

        barra_busqueda = QHBoxLayout()
        barra_busqueda.setSpacing(9)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar materia, carrera o cuatrimestre..."
        )
        self.txt_buscar.setClearButtonEnabled(True)
        self.txt_buscar.setMinimumHeight(40)

        barra_busqueda.addWidget(self.txt_buscar, 1)

        self.btn_actualizar = QPushButton("Actualizar lista")
        self.btn_actualizar.setMinimumHeight(40)
        self.btn_actualizar.setMinimumWidth(125)

        self.configurar_boton(
            self.btn_actualizar,
            "#E2E8F0",
            "#CBD5E1",
            "#334155"
        )

        barra_busqueda.addWidget(self.btn_actualizar)

        layout_tabla.addLayout(barra_busqueda)

        # ==================================================
        # TABLA
        # ==================================================

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(5)

        self.tabla.setHorizontalHeaderLabels([
            "ID",
            "MATERIA",
            "CARRERA",
            "CUATRIMESTRE",
            "ESTADO"
        ])

        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabla.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.tabla.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)

        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(43)

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla.setMinimumHeight(190)
        self.tabla.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.tabla.itemSelectionChanged.connect(
            self.seleccionar_materia
        )

        layout_tabla.addWidget(self.tabla, 1)

        # ==================================================
        # PIE
        # ==================================================

        pie_tabla = QHBoxLayout()

        self.lbl_estado = QLabel(
            "Selecciona una materia para consultar o modificar sus datos."
        )

        self.lbl_estado.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            border: none;
            background: transparent;
        """)

        pie_tabla.addWidget(self.lbl_estado)
        pie_tabla.addStretch()

        layout_tabla.addLayout(pie_tabla)

        layout_principal.addWidget(marco_tabla, 1)

        # ==================================================
        # CONEXIONES
        # ==================================================

        self.btn_registrar.clicked.connect(self.registrar)
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_desactivar.clicked.connect(self.desactivar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        self.btn_actualizar.clicked.connect(
            self.cargar_lista_materias
        )

        self.txt_buscar.textChanged.connect(
            self.filtrar_materias
        )

        self.aplicar_estilos()
        self.actualizar_estado_botones()

    # ======================================================
    # ESTILOS
    # ======================================================

    def aplicar_estilos(self):

        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                color: #1E293B;
            }

            QFrame#marcoFormulario,
            QFrame#marcoTabla {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 11px;
            }

            QLineEdit {
                color: #1E293B;
                background-color: #F8FAFC;
                selection-color: #FFFFFF;
                selection-background-color: #003B73;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
                padding: 8px 11px;
                font-size: 12px;
            }

            QLineEdit:focus {
                border: 1px solid #1677C8;
                background-color: #FFFFFF;
            }

            QComboBox {
                color: #1E293B;
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
                padding: 7px 10px;
                font-size: 12px;
            }

            QComboBox:focus {
                border: 1px solid #1677C8;
                background-color: #FFFFFF;
            }

            QComboBox QAbstractItemView {
                color: #1E293B;
                background-color: #FFFFFF;
                selection-color: #FFFFFF;
                selection-background-color: #003B73;
                border: 1px solid #CBD5E1;
                outline: none;
            }

            QTableWidget {
                color: #1E293B;
                background-color: #FFFFFF;
                alternate-background-color: #F8FAFC;
                border: none;
                font-size: 12px;
                selection-background-color: #DBEAFE;
                selection-color: #001F3F;
                outline: none;
            }

            QTableWidget::item {
                padding: 7px;
                border-bottom: 1px solid #F1F5F9;
            }

            QTableWidget::item:selected {
                color: #001F3F;
                background-color: #DBEAFE;
            }

            QHeaderView::section {
                color: #334155;
                background-color: #F1F5F9;
                padding: 11px 7px;
                border: none;
                border-bottom: 2px solid #CBD5E1;
                font-size: 10px;
                font-weight: bold;
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

    # ======================================================
    # CONFIGURAR BOTONES
    # ======================================================

    def configurar_boton(
        self,
        boton,
        color,
        color_hover,
        color_texto="#FFFFFF"
    ):

        boton.setCursor(Qt.PointingHandCursor)

        boton.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {color_texto};
                border: none;
                border-radius: 7px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {color_hover};
            }}

            QPushButton:disabled {{
                background-color: #E2E8F0;
                color: #94A3B8;
            }}
        """)

    # ======================================================
    # TARJETAS DE INDICADORES
    # ======================================================

    def crear_tarjeta_indicador(
        self,
        titulo,
        valor,
        color,
        fondo
    ):

        tarjeta = QFrame()
        tarjeta.setMinimumHeight(88)
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
        layout.setContentsMargins(16, 11, 16, 11)
        layout.setSpacing(4)

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
            font-size: 25px;
            font-weight: 800;
            border: none;
            background: transparent;
        """)

        layout.addWidget(etiqueta)
        layout.addWidget(lbl_valor)

        return tarjeta, lbl_valor

    # ======================================================
    # ACTUALIZAR INDICADORES
    # ======================================================

    def actualizar_indicadores(self):

        total = len(self.materias)

        activas = sum(
            1
            for materia in self.materias
            if materia.get("activo", True)
        )

        inactivas = total - activas

        self.lbl_total.setText(str(total))
        self.lbl_activas.setText(str(activas))
        self.lbl_inactivas.setText(str(inactivas))

    # ======================================================
    # CARGAR MATERIAS
    # ======================================================

    def cargar_lista_materias(self):

        try:

            resultado = cargar_materias(
                solo_activas=False
            )

            self.materias = (
                resultado
                if isinstance(resultado, list)
                else []
            )

            self.materias = [
                materia
                for materia in self.materias
                if isinstance(materia, dict)
            ]

            self.actualizar_indicadores()

            self.txt_buscar.clear()

            self.mostrar_materias_en_tabla(
                self.materias
            )

            self.materia_seleccionada = None

            self.actualizar_estado_botones()

            self.lbl_estado.setText(
                "Selecciona una materia para consultar o modificar sus datos."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al cargar materias",
                f"No se pudieron cargar las materias:\n\n{error}"
            )

    # ======================================================
    # MOSTRAR MATERIAS EN TABLA
    # ======================================================

    def mostrar_materias_en_tabla(self, materias):

        self.tabla.blockSignals(True)

        try:

            self.tabla.clearSpans()
            self.tabla.clearContents()
            self.tabla.setRowCount(len(materias))

            for fila, materia in enumerate(materias):

                identificador = str(
                    materia.get("id", "")
                )

                nombre = materia.get("nombre", "")
                carrera = materia.get("carrera", "")
                cuatrimestre = materia.get("cuatrimestre", "")

                activa = materia.get("activo", True)

                estado = (
                    "ACTIVA"
                    if activa
                    else "INACTIVA"
                )

                valores = [
                    identificador,
                    nombre,
                    carrera,
                    cuatrimestre,
                    estado
                ]

                for columna, valor in enumerate(valores):

                    elemento = QTableWidgetItem(
                        str(valor)
                    )

                    elemento.setTextAlignment(
                        Qt.AlignCenter
                    )

                    if columna == 0:
                        elemento.setForeground(
                            QColor("#003B73")
                        )

                    elif columna == 4:

                        if activa:
                            elemento.setForeground(
                                QColor("#15803D")
                            )
                        else:
                            elemento.setForeground(
                                QColor("#D97706")
                            )

                    else:
                        elemento.setForeground(
                            QColor("#334155")
                        )

                    self.tabla.setItem(
                        fila,
                        columna,
                        elemento
                    )

            if not materias:

                self.tabla.setRowCount(1)

                elemento = QTableWidgetItem(
                    "No se encontraron materias."
                )

                elemento.setTextAlignment(
                    Qt.AlignCenter
                )

                elemento.setForeground(
                    QColor("#64748B")
                )

                self.tabla.setItem(0, 0, elemento)
                self.tabla.setSpan(0, 0, 1, 5)

            self.lbl_resultados.setText(
                f"{len(materias)} registros"
            )

        finally:

            self.tabla.blockSignals(False)

    # ======================================================
    # BUSCADOR
    # ======================================================

    def filtrar_materias(self, texto):

        texto = texto.strip().lower()

        if not texto:

            filtradas = self.materias

        else:

            filtradas = []

            for materia in self.materias:

                nombre = str(
                    materia.get("nombre", "")
                ).lower()

                carrera = str(
                    materia.get("carrera", "")
                ).lower()

                cuatrimestre = str(
                    materia.get("cuatrimestre", "")
                ).lower()

                identificador = str(
                    materia.get("id", "")
                ).lower()

                nombre_carrera = CARRERAS.get(
                    materia.get("carrera", ""),
                    ""
                ).lower()

                if (
                    texto in nombre
                    or texto in carrera
                    or texto in nombre_carrera
                    or texto in cuatrimestre
                    or texto in identificador
                ):

                    filtradas.append(materia)

        self.mostrar_materias_en_tabla(filtradas)

        self.materia_seleccionada = None
        self.tabla.clearSelection()

        self.actualizar_estado_botones()

        self.lbl_estado.setText(
            f"Resultados encontrados: {len(filtradas)} materia(s)."
            if texto
            else "Selecciona una materia para consultar o modificar sus datos."
        )

    # ======================================================
    # SELECCIONAR MATERIA
    # ======================================================

    def seleccionar_materia(self):

        fila = self.tabla.currentRow()

        if fila < 0:
            self.materia_seleccionada = None
            self.actualizar_estado_botones()
            return

        elemento = self.tabla.item(fila, 0)

        if elemento is None:
            self.materia_seleccionada = None
            self.actualizar_estado_botones()
            return

        identificador = elemento.text()

        self.materia_seleccionada = next(
            (
                materia
                for materia in self.materias
                if str(materia.get("id", "")) == identificador
            ),
            None
        )

        if not self.materia_seleccionada:
            self.actualizar_estado_botones()
            return

        materia = self.materia_seleccionada

        self.txt_nombre.setText(
            materia.get("nombre", "")
        )

        indice_carrera = self.cmb_carrera.findData(
            materia.get("carrera")
        )

        if indice_carrera >= 0:
            self.cmb_carrera.setCurrentIndex(
                indice_carrera
            )

        indice_cuatrimestre = self.cmb_cuatrimestre.findText(
            materia.get("cuatrimestre", "")
        )

        if indice_cuatrimestre >= 0:
            self.cmb_cuatrimestre.setCurrentIndex(
                indice_cuatrimestre
            )

        self.actualizar_estado_botones()

        self.lbl_estado.setText(
            f"Materia seleccionada: {materia.get('nombre', '')}"
        )

    # ======================================================
    # ESTADO DE BOTONES
    # ======================================================

    def actualizar_estado_botones(self):

        seleccionada = self.materia_seleccionada is not None

        activa = (
            seleccionada
            and self.materia_seleccionada.get("activo", True)
        )

        self.btn_modificar.setEnabled(activa)
        self.btn_desactivar.setEnabled(activa)
        self.btn_eliminar.setEnabled(seleccionada)

        if seleccionada:

            self.lbl_modo.setText("MATERIA SELECCIONADA")

        else:

            self.lbl_modo.setText("NUEVO REGISTRO")

    # ======================================================
    # REGISTRAR
    # ======================================================

    def registrar(self):

        nombre = self.txt_nombre.text().strip()

        carrera = self.cmb_carrera.currentData()

        cuatrimestre = self.cmb_cuatrimestre.currentText()

        if not nombre:

            QMessageBox.warning(
                self,
                "Campo obligatorio",
                "Escribe el nombre de la materia."
            )

            self.txt_nombre.setFocus()
            return

        try:

            identificador = registrar_materia(
                nombre,
                carrera,
                cuatrimestre
            )

            QMessageBox.information(
                self,
                "Materia registrada",
                "La materia se registró correctamente.\n\n"
                f"ID: {identificador}"
            )

            self.limpiar_formulario()
            self.cargar_lista_materias()

        except Exception as error:

            QMessageBox.warning(
                self,
                "No se pudo registrar",
                str(error)
            )

    # ======================================================
    # MODIFICAR
    # ======================================================

    def modificar(self):

        if not self.materia_seleccionada:

            QMessageBox.warning(
                self,
                "Selecciona una materia",
                "Selecciona una materia de la tabla."
            )

            return

        nombre = self.txt_nombre.text().strip()

        if not nombre:

            QMessageBox.warning(
                self,
                "Campo obligatorio",
                "Escribe el nombre de la materia."
            )

            self.txt_nombre.setFocus()
            return

        if not self.materia_seleccionada.get("activo", True):

            QMessageBox.warning(
                self,
                "Materia inactiva",
                "No puedes modificar una materia desactivada."
            )

            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar modificación",
            "¿Deseas guardar los cambios de esta materia?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        try:

            actualizar_materia(
                self.materia_seleccionada["id"],
                nombre,
                self.cmb_carrera.currentData(),
                self.cmb_cuatrimestre.currentText()
            )

            QMessageBox.information(
                self,
                "Materia modificada",
                "Los cambios se guardaron correctamente."
            )

            self.limpiar_formulario()
            self.cargar_lista_materias()

        except Exception as error:

            QMessageBox.warning(
                self,
                "No se pudo modificar",
                str(error)
            )

    # ======================================================
    # DESACTIVAR
    # ======================================================

    def desactivar(self):

        if not self.materia_seleccionada:

            QMessageBox.warning(
                self,
                "Selecciona una materia",
                "Selecciona una materia de la tabla."
            )

            return

        if not self.materia_seleccionada.get("activo", True):

            QMessageBox.information(
                self,
                "Materia inactiva",
                "Esta materia ya está desactivada."
            )

            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar desactivación",
            "¿Deseas desactivar esta materia?\n\n"
            "La información se conservará en Firebase.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        try:

            desactivar_materia(
                self.materia_seleccionada["id"]
            )

            QMessageBox.information(
                self,
                "Materia desactivada",
                "La materia se desactivó correctamente."
            )

            self.limpiar_formulario()
            self.cargar_lista_materias()

        except Exception as error:

            QMessageBox.warning(
                self,
                "Error",
                str(error)
            )

    # ======================================================
    # ELIMINAR DEFINITIVAMENTE
    # ======================================================

    def eliminar(self):

        if not self.materia_seleccionada:

            QMessageBox.warning(
                self,
                "Selecciona una materia",
                "Selecciona una materia de la tabla."
            )

            return

        identificador = self.materia_seleccionada.get("id")
        nombre = self.materia_seleccionada.get("nombre", "")

        respuesta = QMessageBox.warning(
            self,
            "Eliminar materia",
            f"¿Estás seguro de eliminar esta materia?\n\n"
            f"Materia: {nombre}\n"
            f"ID: {identificador}\n\n"
            "Esta acción eliminará definitivamente el registro "
            "de Firebase y no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        try:

            horarios = (
                db.collection(COLECCION_HORARIOS)
                .where("id_materia", "==", identificador)
                .stream()
            )

            tiene_horarios = any(
                True for _ in horarios
            )

            if tiene_horarios:

                QMessageBox.warning(
                    self,
                    "No se puede eliminar",
                    "Esta materia tiene horarios asociados.\n\n"
                    "Para conservar el historial académico, "
                    "primero debes revisar esos horarios.\n\n"
                    "Puedes desactivar la materia en lugar de eliminarla."
                )

                return

            db.collection(
                COLECCION_MATERIAS
            ).document(
                identificador
            ).delete()

            QMessageBox.information(
                self,
                "Materia eliminada",
                "La materia se eliminó definitivamente de Firebase."
            )

            self.limpiar_formulario()
            self.cargar_lista_materias()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al eliminar",
                f"No se pudo eliminar la materia:\n\n{error}"
            )

    # ======================================================
    # LIMPIAR FORMULARIO
    # ======================================================

    def limpiar_formulario(self):

        self.txt_nombre.clear()

        self.cmb_carrera.setCurrentIndex(0)
        self.cmb_cuatrimestre.setCurrentIndex(0)

        self.materia_seleccionada = None

        self.tabla.clearSelection()

        self.actualizar_estado_botones()

        self.lbl_estado.setText(
            "Formulario listo para registrar una nueva materia."
        )

        self.txt_nombre.setFocus()
