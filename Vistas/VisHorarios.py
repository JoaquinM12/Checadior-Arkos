
# ==========================================================
# VISTA DE HORARIOS
# Archivo: Vistas/VisHorarios.py
# BASE DE DATOS: MYSQL
# ==========================================================

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QCompleter,
    QTimeEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFrame,
    QAbstractItemView,
    QLineEdit,
    QSizePolicy
)

from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QColor

from Configuracion.ConexionMySQL import obtener_conexion


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

DIAS = [
    "LUNES",
    "MARTES",
    "MIÉRCOLES",
    "JUEVES",
    "VIERNES",
    "SÁBADO"
]


# ==========================================================
# VENTANA DE HORARIOS
# ==========================================================

class VisHorarios(QWidget):

    def __init__(self):

        super().__init__()

        self.maestros = []
        self.materias = []
        self.horarios = []
        self.horarios_filtrados = []

        self.id_seleccionado = None

        self.crear_interfaz()
        self.cargar_datos()
        self.cargar_horarios()

    # ======================================================
    # CONEXIÓN MYSQL
    # ======================================================

    def obtener_conexion_mysql(self):

        conexion = obtener_conexion()

        if conexion is None:
            raise ConnectionError(
                "No fue posible conectar con MySQL."
            )

        return conexion

    # ======================================================
    # CONVERTIR ID DE MAESTRO
    # ======================================================

    def convertir_numero_a_id(self, numero):

        return f"MST-{int(numero):04d}"

    def convertir_id_a_numero(self, identificador):

        identificador = str(identificador).strip()

        if identificador.upper().startswith("MST-"):
            identificador = identificador[4:]

        return int(identificador)

    # ======================================================
    # INTERFAZ PRINCIPAL
    # ======================================================

    def crear_interfaz(self):

        principal = QVBoxLayout(self)

        principal.setContentsMargins(25, 22, 25, 22)
        principal.setSpacing(16)

        # ==================================================
        # ENCABEZADO
        # ==================================================

        encabezado = QHBoxLayout()
        encabezado.setSpacing(15)

        bloque_titulo = QVBoxLayout()
        bloque_titulo.setSpacing(5)

        titulo = QLabel("Horarios")

        titulo.setStyleSheet("""
            font-size: 27px;
            font-weight: 800;
            color: #001F3F;
        """)

        descripcion = QLabel(
            "Organiza las asignaciones académicas y los horarios de los maestros."
        )

        descripcion.setStyleSheet("""
            font-size: 13px;
            color: #64748B;
        """)

        bloque_titulo.addWidget(titulo)
        bloque_titulo.addWidget(descripcion)

        encabezado.addLayout(bloque_titulo)
        encabezado.addStretch()

        self.lbl_periodo = QLabel("GESTIÓN ACADÉMICA")
        self.lbl_periodo.setAlignment(Qt.AlignCenter)
        self.lbl_periodo.setMinimumHeight(32)

        self.lbl_periodo.setStyleSheet("""
            background-color: #EAF2FA;
            color: #003B73;
            border: 1px solid #C9DDF0;
            border-radius: 7px;
            padding: 5px 13px;
            font-size: 10px;
            font-weight: bold;
        """)

        encabezado.addWidget(self.lbl_periodo)

        principal.addLayout(encabezado)

        # ==================================================
        # INDICADORES
        # ==================================================

        indicadores = QGridLayout()
        indicadores.setSpacing(13)

        self.card_horarios, self.lbl_total_horarios = (
            self.crear_tarjeta_indicador(
                "HORARIOS REGISTRADOS",
                "0",
                "#003B73",
                "#EAF2FA"
            )
        )

        self.card_maestros, self.lbl_total_maestros = (
            self.crear_tarjeta_indicador(
                "MAESTROS DISPONIBLES",
                "0",
                "#15803D",
                "#EAF7EF"
            )
        )

        self.card_materias, self.lbl_total_materias = (
            self.crear_tarjeta_indicador(
                "MATERIAS DISPONIBLES",
                "0",
                "#D97706",
                "#FFF7E8"
            )
        )

        indicadores.addWidget(self.card_horarios, 0, 0)
        indicadores.addWidget(self.card_maestros, 0, 1)
        indicadores.addWidget(self.card_materias, 0, 2)

        for columna in range(3):
            indicadores.setColumnStretch(columna, 1)

        principal.addLayout(indicadores)

        # ==================================================
        # FORMULARIO
        # ==================================================

        marco_formulario = QFrame()
        marco_formulario.setObjectName("marcoFormulario")

        layout_formulario = QVBoxLayout(marco_formulario)

        layout_formulario.setContentsMargins(18, 15, 18, 15)
        layout_formulario.setSpacing(13)

        encabezado_formulario = QHBoxLayout()

        bloque_formulario = QVBoxLayout()
        bloque_formulario.setSpacing(4)

        titulo_formulario = QLabel("Asignación de horario")

        titulo_formulario.setStyleSheet("""
            color: #001F3F;
            font-size: 17px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)

        subtitulo_formulario = QLabel(
            "Selecciona un maestro, una materia y define los horarios de clase."
        )

        subtitulo_formulario.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            border: none;
            background: transparent;
        """)

        bloque_formulario.addWidget(titulo_formulario)
        bloque_formulario.addWidget(subtitulo_formulario)

        encabezado_formulario.addLayout(bloque_formulario)
        encabezado_formulario.addStretch()

        self.lbl_modo = QLabel("NUEVA ASIGNACIÓN")
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

        # ==================================================
        # CAMPOS
        # ==================================================

        campos = QGridLayout()

        campos.setHorizontalSpacing(14)
        campos.setVerticalSpacing(7)

        etiqueta_maestro = self.crear_etiqueta("Maestro")
        etiqueta_materia = self.crear_etiqueta("Materia")

        self.combo_maestro = QComboBox()
        self.combo_maestro.setMinimumHeight(40)
        self.combo_maestro.setEditable(True)
        self.combo_maestro.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_maestro.setPlaceholderText(
            "Escribe el nombre o número del maestro para buscar"
        )
        buscador_maestros = QCompleter(self.combo_maestro.model(), self)
        buscador_maestros.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        buscador_maestros.setFilterMode(Qt.MatchFlag.MatchContains)
        buscador_maestros.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.combo_maestro.setCompleter(buscador_maestros)

        self.combo_materia = QComboBox()
        self.combo_materia.setMinimumHeight(40)
        self.combo_materia.setEditable(True)
        self.combo_materia.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_materia.setPlaceholderText(
            "Escribe materia, carrera o cuatrimestre para buscar"
        )
        buscador_materias = QCompleter(self.combo_materia.model(), self)
        buscador_materias.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        buscador_materias.setFilterMode(Qt.MatchFlag.MatchContains)
        buscador_materias.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.combo_materia.setCompleter(buscador_materias)

        self.combo_materia.currentIndexChanged.connect(
            self.actualizar_informacion_materia
        )
        self.combo_materia.editTextChanged.connect(
            self.actualizar_informacion_materia
        )

        campos.addWidget(etiqueta_maestro, 0, 0)
        campos.addWidget(etiqueta_materia, 0, 1)

        campos.addWidget(self.combo_maestro, 1, 0)
        campos.addWidget(self.combo_materia, 1, 1)

        campos.setColumnStretch(0, 1)
        campos.setColumnStretch(1, 1)

        layout_formulario.addLayout(campos)

        # ==================================================
        # INFORMACIÓN ACADÉMICA
        # ==================================================

        informacion = QGridLayout()
        informacion.setSpacing(12)

        self.card_carrera, self.lbl_carrera = (
            self.crear_campo_informacion(
                "CARRERA",
                "Selecciona una materia"
            )
        )

        self.card_cuatrimestre, self.lbl_cuatrimestre = (
            self.crear_campo_informacion(
                "CUATRIMESTRE",
                "Selecciona una materia"
            )
        )

        informacion.addWidget(self.card_carrera, 0, 0)
        informacion.addWidget(self.card_cuatrimestre, 0, 1)

        informacion.setColumnStretch(0, 1)
        informacion.setColumnStretch(1, 1)

        layout_formulario.addLayout(informacion)

        # ==================================================
        # DÍA Y HORAS
        # ==================================================

        campos_horario = QGridLayout()

        campos_horario.setHorizontalSpacing(14)
        campos_horario.setVerticalSpacing(7)

        etiqueta_dia = self.crear_etiqueta("Día de clase")
        etiqueta_inicio = self.crear_etiqueta("Hora de inicio")
        etiqueta_fin = self.crear_etiqueta("Hora de fin")

        self.combo_dia = QComboBox()
        self.combo_dia.setMinimumHeight(40)
        self.combo_dia.addItems(DIAS)

        self.hora_inicio = QTimeEdit()
        self.hora_inicio.setDisplayFormat("HH:mm")
        self.hora_inicio.setTime(QTime(17, 0))
        self.hora_inicio.setMinimumHeight(40)
        self.hora_inicio.setMinimumWidth(125)
        self.hora_inicio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hora_inicio.setToolTip("Selecciona la hora de inicio de la clase")

        self.hora_fin = QTimeEdit()
        self.hora_fin.setDisplayFormat("HH:mm")
        self.hora_fin.setTime(QTime(19, 0))
        self.hora_fin.setMinimumHeight(40)
        self.hora_fin.setMinimumWidth(125)
        self.hora_fin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hora_fin.setToolTip("Selecciona la hora de fin de la clase")

        campos_horario.addWidget(etiqueta_dia, 0, 0)
        campos_horario.addWidget(etiqueta_inicio, 0, 1)
        campos_horario.addWidget(etiqueta_fin, 0, 2)

        campos_horario.addWidget(self.combo_dia, 1, 0)
        campos_horario.addWidget(self.hora_inicio, 1, 1)
        campos_horario.addWidget(self.hora_fin, 1, 2)

        for columna in range(3):
            campos_horario.setColumnStretch(columna, 1)

        layout_formulario.addLayout(campos_horario)

        # ==================================================
        # BOTONES DEL FORMULARIO
        # ==================================================

        botones_formulario = QHBoxLayout()
        botones_formulario.setSpacing(9)

        self.btn_guardar = QPushButton("+ Registrar horario")
        self.btn_modificar = QPushButton("Guardar cambios")
        self.btn_limpiar = QPushButton("Limpiar formulario")

        self.configurar_boton(
            self.btn_guardar,
            "#003B73",
            "#1677C8"
        )

        self.configurar_boton(
            self.btn_modificar,
            "#D97706",
            "#B45309"
        )

        self.configurar_boton(
            self.btn_limpiar,
            "#E2E8F0",
            "#CBD5E1",
            "#334155"
        )

        for boton in (
            self.btn_guardar,
            self.btn_modificar,
            self.btn_limpiar
        ):
            boton.setMinimumHeight(39)

        botones_formulario.addWidget(self.btn_guardar)
        botones_formulario.addWidget(self.btn_modificar)
        botones_formulario.addStretch()
        botones_formulario.addWidget(self.btn_limpiar)

        layout_formulario.addLayout(botones_formulario)

        principal.addWidget(marco_formulario)

        # ==================================================
        # TABLA DE HORARIOS
        # ==================================================

        marco_tabla = QFrame()
        marco_tabla.setObjectName("marcoTabla")

        layout_tabla = QVBoxLayout(marco_tabla)

        layout_tabla.setContentsMargins(18, 15, 18, 15)
        layout_tabla.setSpacing(12)

        encabezado_tabla = QHBoxLayout()

        bloque_titulo_tabla = QVBoxLayout()
        bloque_titulo_tabla.setSpacing(4)

        titulo_tabla = QLabel("Directorio de horarios")

        titulo_tabla.setStyleSheet("""
            color: #001F3F;
            font-size: 17px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)

        subtitulo_tabla = QLabel(
            "Consulta y administra las asignaciones académicas registradas."
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
        # BUSCADOR
        # ==================================================

        barra_busqueda = QHBoxLayout()
        barra_busqueda.setSpacing(9)

        self.txt_buscar = QLineEdit()

        self.txt_buscar.setPlaceholderText(
            "Buscar por maestro, materia, día o carrera..."
        )

        self.txt_buscar.setClearButtonEnabled(True)
        self.txt_buscar.setMinimumHeight(40)

        self.btn_actualizar = QPushButton("Actualizar lista")
        self.btn_actualizar.setMinimumHeight(40)
        self.btn_actualizar.setMinimumWidth(125)

        self.configurar_boton(
            self.btn_actualizar,
            "#E2E8F0",
            "#CBD5E1",
            "#334155"
        )

        barra_busqueda.addWidget(self.txt_buscar, 1)
        barra_busqueda.addWidget(self.btn_actualizar)

        layout_tabla.addLayout(barra_busqueda)

        # ==================================================
        # TABLA
        # ==================================================

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(8)

        self.tabla.setHorizontalHeaderLabels([
            "ID",
            "MAESTRO",
            "MATERIA",
            "DÍA",
            "INICIO",
            "FIN",
            "CARRERA",
            "CUATRIMESTRE"
        ])

        self.tabla.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabla.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)

        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(43)

        encabezado_horizontal = self.tabla.horizontalHeader()

        encabezado_horizontal.setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        encabezado_horizontal.setStretchLastSection(True)

        encabezado_horizontal.setSectionResizeMode(
            1, QHeaderView.Stretch
        )

        encabezado_horizontal.setSectionResizeMode(
            2, QHeaderView.Stretch
        )

        self.tabla.setMinimumHeight(190)

        self.tabla.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.tabla.itemSelectionChanged.connect(
            self.seleccionar_horario
        )

        layout_tabla.addWidget(self.tabla, 1)

        # ==================================================
        # PIE DE TABLA
        # ==================================================

        pie_tabla = QHBoxLayout()

        self.lbl_estado = QLabel(
            "Selecciona un horario para modificarlo o desactivarlo."
        )

        self.lbl_estado.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            border: none;
            background: transparent;
        """)

        pie_tabla.addWidget(self.lbl_estado)
        pie_tabla.addStretch()

        self.btn_eliminar = QPushButton("Desactivar horario")
        self.btn_eliminar.setMinimumHeight(38)
        self.btn_eliminar.setMinimumWidth(150)

        self.configurar_boton(
            self.btn_eliminar,
            "#B91C1C",
            "#991B1B"
        )

        pie_tabla.addWidget(self.btn_eliminar)

        layout_tabla.addLayout(pie_tabla)

        principal.addWidget(marco_tabla, 1)

        # ==================================================
        # CONEXIONES
        # ==================================================

        self.btn_guardar.clicked.connect(
            self.registrar_horario
        )

        self.btn_modificar.clicked.connect(
            self.modificar_horario
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_formulario
        )

        self.btn_actualizar.clicked.connect(
            self.actualizar_listas
        )

        self.btn_eliminar.clicked.connect(
            self.eliminar_horario
        )

        self.txt_buscar.textChanged.connect(
            self.filtrar_horarios
        )

        self.btn_modificar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        self.aplicar_estilos()

    # ======================================================
    # CREAR ETIQUETA
    # ======================================================

    def crear_etiqueta(self, texto):

        etiqueta = QLabel(texto)

        etiqueta.setStyleSheet("""
            color: #334155;
            font-size: 11px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)

        return etiqueta

    # ======================================================
    # TARJETA DE INDICADOR
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
    # CAMPOS DE INFORMACIÓN
    # ======================================================

    def crear_campo_informacion(self, titulo, valor):

        tarjeta = QFrame()

        tarjeta.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 7px;
            }
        """)

        layout = QVBoxLayout(tarjeta)

        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(3)

        etiqueta = QLabel(titulo)

        etiqueta.setStyleSheet("""
            color: #64748B;
            font-size: 9px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)

        lbl_valor = QLabel(valor)

        lbl_valor.setStyleSheet("""
            color: #003B73;
            font-size: 12px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)

        lbl_valor.setWordWrap(True)

        layout.addWidget(etiqueta)
        layout.addWidget(lbl_valor)

        return tarjeta, lbl_valor

    # ======================================================
    # CONFIGURAR BOTÓN
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
                padding: 8px 13px;
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
    # ESTILOS GENERALES
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

            QComboBox {
                color: #1E293B;
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
                padding: 7px 10px;
                font-size: 12px;
            }

            QTimeEdit {
                color: #003B73;
                background-color: #FFFFFF;
                border: 1px solid #B8C9DB;
                border-radius: 8px;
                padding: 7px 12px;
                font-size: 15px;
                font-weight: 700;
            }

            QTimeEdit:focus {
                border: 2px solid #1677C8;
                background-color: #FFFFFF;
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

            QLineEdit {
                color: #1E293B;
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
                padding: 8px 11px;
                font-size: 12px;
            }

            QLineEdit:focus {
                border: 1px solid #1677C8;
                background-color: #FFFFFF;
            }

            QTableWidget {
                color: #1E293B;
                background-color: #FFFFFF;
                alternate-background-color: #F8FAFC;
                border: none;
                font-size: 11px;
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
                padding: 11px 6px;
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

            QScrollBar:horizontal {
                background-color: #F8FAFC;
                height: 9px;
                margin: 0px;
                border-radius: 4px;
            }

            QScrollBar::handle:horizontal {
                background-color: #CBD5E1;
                min-width: 25px;
                border-radius: 4px;
            }
        """)

    # ======================================================
    # CARGAR DATOS
    # ======================================================

    def cargar_datos(self):

        self.cargar_lista_maestros()
        self.cargar_lista_materias()

        self.actualizar_indicadores()

    # ======================================================
    # CARGAR MAESTROS DESDE MYSQL
    # ======================================================

    def cargar_lista_maestros(self):

        conexion = None
        cursor = None

        self.combo_maestro.clear()
        self.maestros = []

        try:

            conexion = self.obtener_conexion_mysql()

            cursor = conexion.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    id_maestro,
                    nombre,
                    apellido,
                    estado
                FROM tblMaestros
                WHERE estado = 'ACTIVO'
                ORDER BY apellido ASC, nombre ASC
            """)

            registros = cursor.fetchall()

            for registro in registros:

                numero = registro["id_maestro"]

                identificador = self.convertir_numero_a_id(numero)

                nombre_completo = (
                    f"{registro['nombre']} "
                    f"{registro['apellido']}"
                ).strip()

                maestro = {
                    "id": identificador,
                    "id_maestro": numero,
                    "nombre": registro["nombre"],
                    "apellidos": registro["apellido"],
                    "nombre_completo": nombre_completo,
                    "activo": True
                }

                self.maestros.append(maestro)

                self.combo_maestro.addItem(
                    f"{identificador} - {nombre_completo}",
                    numero
                )

            if self.combo_maestro.count() == 0:

                self.combo_maestro.addItem(
                    "No hay maestros activos",
                    None
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al cargar maestros",
                f"No fue posible consultar los maestros en MySQL:\n\n{error}"
            )

        finally:

            if cursor:
                cursor.close()

            if conexion:
                conexion.close()

    # ======================================================
    # CARGAR MATERIAS DESDE MYSQL
    # ======================================================

    def cargar_lista_materias(self):

        conexion = None
        cursor = None

        self.combo_materia.clear()
        self.materias = []

        try:

            conexion = self.obtener_conexion_mysql()

            cursor = conexion.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    id_materia,
                    nombre,
                    carrera,
                    cuatrimestre,
                    estado
                FROM tblMaterias
                WHERE estado = 'ACTIVA'
                ORDER BY carrera, cuatrimestre, nombre
            """)

            registros = cursor.fetchall()

            for registro in registros:

                materia = {
                    "id": str(registro["id_materia"]),
                    "id_materia": registro["id_materia"],
                    "nombre": registro["nombre"],
                    "carrera": registro["carrera"],
                    "cuatrimestre": registro["cuatrimestre"],
                    "activo": True
                }

                self.materias.append(materia)

                texto = (
                    f"{materia['nombre']} | "
                    f"{materia['carrera']} | "
                    f"{materia['cuatrimestre']}"
                )

                self.combo_materia.addItem(
                    texto,
                    registro["id_materia"]
                )

            if self.combo_materia.count() == 0:

                self.combo_materia.addItem(
                    "No hay materias activas",
                    None
                )

            self.actualizar_informacion_materia()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al cargar materias",
                f"No fue posible consultar las materias en MySQL:\n\n{error}"
            )

        finally:

            if cursor:
                cursor.close()

            if conexion:
                conexion.close()

    # ======================================================
    # ACTUALIZAR INDICADORES
    # ======================================================

    def actualizar_indicadores(self):

        self.lbl_total_horarios.setText(
            str(len(self.horarios))
        )

        self.lbl_total_maestros.setText(
            str(len(self.maestros))
        )

        self.lbl_total_materias.setText(
            str(len(self.materias))
        )

    # ======================================================
    # INFORMACIÓN DE MATERIA
    # ======================================================

    def actualizar_informacion_materia(self, indice=None):

        identificador = self.obtener_id_materia_seleccionada()

        materia = next(
            (
                m for m in self.materias
                if m.get("id_materia") == identificador
            ),
            None
        )

        if materia is None:

            self.lbl_carrera.setText("No disponible")
            self.lbl_cuatrimestre.setText("No disponible")

            return

        self.lbl_carrera.setText(
            materia.get("carrera", "")
        )

        self.lbl_cuatrimestre.setText(
            materia.get("cuatrimestre", "")
        )

    def obtener_id_materia_seleccionada(self):
        """Devuelve el ID solo si el texto corresponde a una materia real."""
        texto = self.combo_materia.currentText().strip()
        indice = self.combo_materia.findText(
            texto,
            Qt.MatchFlag.MatchFixedString
        )
        if indice < 0:
            return None
        return self.combo_materia.itemData(indice)

    def obtener_id_maestro_seleccionado(self):
        """Devuelve el ID solo si el texto corresponde a un maestro real."""
        texto = self.combo_maestro.currentText().strip()
        indice = self.combo_maestro.findText(
            texto,
            Qt.MatchFlag.MatchFixedString
        )
        if indice < 0:
            return None
        return self.combo_maestro.itemData(indice)

    # ======================================================
    # VALIDAR HORAS
    # ======================================================

    def validar_horas(self):

        inicio = self.hora_inicio.time()
        fin = self.hora_fin.time()

        if inicio >= fin:

            QMessageBox.warning(
                self,
                "Horario incorrecto",
                "La hora de inicio debe ser anterior a la hora de fin."
            )

            return False

        return True

    # ======================================================
    # VALIDAR EMPALMES
    # ======================================================

    def validar_empalme(
        self,
        id_maestro,
        dia,
        hora_inicio,
        hora_fin,
        id_excluir=None
    ):

        conexion = None
        cursor = None

        try:

            conexion = self.obtener_conexion_mysql()

            cursor = conexion.cursor(dictionary=True)

            consulta = """
                SELECT
                    id_horario,
                    hora_inicio,
                    hora_fin
                FROM tblHorarios
                WHERE id_maestro = %s
                AND dia = %s
                AND estado = 'ACTIVO'
                AND hora_inicio < %s
                AND hora_fin > %s
            """

            parametros = [
                id_maestro,
                dia,
                hora_fin,
                hora_inicio
            ]

            if id_excluir is not None:

                consulta += """
                    AND id_horario <> %s
                """

                parametros.append(id_excluir)

            cursor.execute(
                consulta,
                tuple(parametros)
            )

            empalme = cursor.fetchone()

            if empalme:

                return (
                    False,
                    "El maestro ya tiene otro horario registrado "
                    "que se empalma con este horario.\n\n"
                    f"Horario existente: "
                    f"{str(empalme['hora_inicio'])[:5]} - "
                    f"{str(empalme['hora_fin'])[:5]}"
                )

            return True, ""

        except Exception as error:

            return False, (
                f"No fue posible validar los horarios:\n\n{error}"
            )

        finally:

            if cursor:
                cursor.close()

            if conexion:
                conexion.close()

    # ======================================================
    # REGISTRAR HORARIO
    # ======================================================

    def registrar_horario(self):

        id_maestro = self.obtener_id_maestro_seleccionado()
        id_materia = self.obtener_id_materia_seleccionada()

        if not id_maestro:

            QMessageBox.warning(
                self,
                "Maestro requerido",
                "Selecciona un maestro activo."
            )

            return

        if not id_materia:

            QMessageBox.warning(
                self,
                "Materia requerida",
                "Primero debes registrar una materia activa."
            )

            return

        if not self.validar_horas():
            return

        inicio = self.hora_inicio.time().toString("HH:mm:ss")
        fin = self.hora_fin.time().toString("HH:mm:ss")

        dia = self.combo_dia.currentText()

        valido, mensaje = self.validar_empalme(
            id_maestro,
            dia,
            inicio,
            fin
        )

        if not valido:

            QMessageBox.warning(
                self,
                "Conflicto de horario",
                mensaje
            )

            return

        conexion = None
        cursor = None

        try:

            conexion = self.obtener_conexion_mysql()

            cursor = conexion.cursor()

            cursor.execute("""
                INSERT INTO tblHorarios (
                    id_maestro,
                    id_materia,
                    dia,
                    hora_inicio,
                    hora_fin,
                    turno,
                    estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                id_maestro,
                id_materia,
                dia,
                inicio,
                fin,
                "VESPERTINO",
                "ACTIVO"
            ))

            identificador = cursor.lastrowid

            conexion.commit()

            QMessageBox.information(
                self,
                "Registro correcto",
                "El horario se registró correctamente en MySQL.\n\n"
                f"ID del horario: {identificador}"
            )

            self.limpiar_formulario()
            self.cargar_horarios()

        except Exception as error:

            if conexion:
                conexion.rollback()

            QMessageBox.critical(
                self,
                "Error al registrar",
                f"No fue posible registrar el horario:\n\n{error}"
            )

        finally:

            if cursor:
                cursor.close()

            if conexion:
                conexion.close()

    # ======================================================
    # CARGAR HORARIOS DESDE MYSQL
    # ======================================================

    def cargar_horarios(self):

        conexion = None
        cursor = None

        try:

            conexion = self.obtener_conexion_mysql()

            cursor = conexion.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    h.id_horario,
                    h.id_maestro,
                    h.id_materia,
                    h.dia,
                    h.hora_inicio,
                    h.hora_fin,
                    h.turno,
                    h.estado,

                    m.nombre AS nombre_maestro,
                    m.apellido AS apellido_maestro,

                    ma.nombre AS nombre_materia,
                    ma.carrera,
                    ma.cuatrimestre

                FROM tblHorarios h

                INNER JOIN tblMaestros m
                    ON h.id_maestro = m.id_maestro

                INNER JOIN tblMaterias ma
                    ON h.id_materia = ma.id_materia

                WHERE h.estado = 'ACTIVO'

                ORDER BY
                    FIELD(
                        h.dia,
                        'LUNES',
                        'MARTES',
                        'MIÉRCOLES',
                        'JUEVES',
                        'VIERNES',
                        'SÁBADO'
                    ),
                    h.hora_inicio
            """)

            registros = cursor.fetchall()

            self.horarios = []

            for registro in registros:

                nombre_maestro = (
                    f"{registro['nombre_maestro']} "
                    f"{registro['apellido_maestro']}"
                ).strip()

                horario = {
                    "id": str(registro["id_horario"]),
                    "id_maestro": registro["id_maestro"],
                    "id_materia": registro["id_materia"],

                    "maestro": nombre_maestro,

                    "id_maestro_texto": self.convertir_numero_a_id(
                        registro["id_maestro"]
                    ),

                    "materia": registro["nombre_materia"],
                    "dia": registro["dia"],

                    "hora_inicio": str(
                        registro["hora_inicio"]
                    )[:5],

                    "hora_fin": str(
                        registro["hora_fin"]
                    )[:5],

                    "turno": registro["turno"],
                    "carrera": registro["carrera"],
                    "cuatrimestre": registro["cuatrimestre"],
                    "estado": registro["estado"]
                }

                self.horarios.append(horario)

            self.horarios_filtrados = self.horarios.copy()

            # Volver a mostrar los registros obtenidos de MySQL
            self.mostrar_horarios(self.horarios)

            self.actualizar_indicadores()

            self.id_seleccionado = None

            self.actualizar_estado_botones()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al cargar horarios",
                f"No fue posible consultar los horarios en MySQL:\n\n{error}"
            )

        finally:

            if cursor:
                cursor.close()

            if conexion:
                conexion.close()

    # ======================================================
    # MOSTRAR HORARIOS
    # CORREGIDO: LIMPIAR COMBINACIONES ANTERIORES
    # ======================================================

    def mostrar_horarios(self, horarios):

        self.tabla.blockSignals(True)

        try:

            # Eliminar combinaciones de columnas anteriores.
            # Esto evita que el mensaje de tabla vacía
            # impida visualizar los registros nuevos.
            self.tabla.clearSpans()

            self.tabla.clearContents()

            self.tabla.setRowCount(len(horarios))

            if horarios:

                for fila, horario in enumerate(horarios):

                    valores = [
                        horario.get("id", ""),
                        horario.get("maestro", ""),
                        horario.get("materia", ""),
                        horario.get("dia", ""),
                        horario.get("hora_inicio", ""),
                        horario.get("hora_fin", ""),
                        horario.get("carrera", ""),
                        horario.get("cuatrimestre", "")
                    ]

                    for columna, valor in enumerate(valores):

                        elemento = QTableWidgetItem(str(valor))

                        elemento.setTextAlignment(
                            Qt.AlignCenter
                        )

                        elemento.setForeground(
                            QColor("#334155")
                        )

                        if columna == 0:

                            elemento.setForeground(
                                QColor("#003B73")
                            )

                        self.tabla.setItem(
                            fila,
                            columna,
                            elemento
                        )

            else:

                self.tabla.setRowCount(1)

                elemento = QTableWidgetItem(
                    "No hay horarios registrados."
                )

                elemento.setTextAlignment(
                    Qt.AlignCenter
                )

                elemento.setForeground(
                    QColor("#64748B")
                )

                self.tabla.setItem(0, 0, elemento)

                self.tabla.setSpan(0, 0, 1, 8)

            self.lbl_resultados.setText(
                f"{len(horarios)} registros"
            )

        finally:

            self.tabla.blockSignals(False)

    # ======================================================
    # BUSCADOR
    # ======================================================

    def filtrar_horarios(self, texto):

        texto = texto.strip().lower()

        if not texto:

            filtrados = self.horarios

        else:

            filtrados = []

            for horario in self.horarios:

                valores = [
                    horario.get("id", ""),
                    horario.get("maestro", ""),
                    horario.get("materia", ""),
                    horario.get("dia", ""),
                    horario.get("hora_inicio", ""),
                    horario.get("hora_fin", ""),
                    horario.get("carrera", ""),
                    horario.get("cuatrimestre", "")
                ]

                if any(
                    texto in str(valor).lower()
                    for valor in valores
                ):

                    filtrados.append(horario)

        self.horarios_filtrados = filtrados

        self.mostrar_horarios(filtrados)

        self.id_seleccionado = None

        self.tabla.clearSelection()

        self.actualizar_estado_botones()

        self.lbl_estado.setText(
            f"Resultados encontrados: {len(filtrados)} horario(s)."
            if texto
            else "Selecciona un horario para modificarlo o desactivarlo."
        )

    # ======================================================
    # SELECCIONAR HORARIO
    # ======================================================

    def seleccionar_horario(self):

        filas = self.tabla.selectionModel().selectedRows()

        if not filas:

            self.id_seleccionado = None

            self.actualizar_estado_botones()

            return

        fila = filas[0].row()

        elemento = self.tabla.item(fila, 0)

        if elemento is None:
            return

        self.id_seleccionado = elemento.text()

        horario = next(
            (
                h for h in self.horarios_filtrados
                if str(h.get("id", "")) == self.id_seleccionado
            ),
            None
        )

        if horario is None:
            return

        # MAESTRO

        indice_maestro = self.combo_maestro.findData(
            horario.get("id_maestro")
        )

        if indice_maestro >= 0:

            self.combo_maestro.setCurrentIndex(
                indice_maestro
            )

        # MATERIA

        indice_materia = self.combo_materia.findData(
            horario.get("id_materia")
        )

        if indice_materia >= 0:

            self.combo_materia.setCurrentIndex(
                indice_materia
            )

        # DÍA

        indice_dia = self.combo_dia.findText(
            horario.get("dia", "")
        )

        if indice_dia >= 0:

            self.combo_dia.setCurrentIndex(
                indice_dia
            )

        # HORA DE INICIO

        hora_inicio = QTime.fromString(
            horario.get("hora_inicio", "17:00"),
            "HH:mm"
        )

        if hora_inicio.isValid():
            self.hora_inicio.setTime(hora_inicio)

        # HORA DE FIN

        hora_fin = QTime.fromString(
            horario.get("hora_fin", "19:00"),
            "HH:mm"
        )

        if hora_fin.isValid():
            self.hora_fin.setTime(hora_fin)

        self.actualizar_estado_botones()

        self.lbl_estado.setText(
            f"Horario seleccionado: {horario.get('maestro', '')} - "
            f"{horario.get('materia', '')}"
        )

    # ======================================================
    # ESTADO DE BOTONES
    # ======================================================

    def actualizar_estado_botones(self):

        seleccionado = self.id_seleccionado is not None

        self.btn_modificar.setEnabled(seleccionado)
        self.btn_eliminar.setEnabled(seleccionado)

        if seleccionado:

            self.lbl_modo.setText("MODIFICANDO HORARIO")

        else:

            self.lbl_modo.setText("NUEVA ASIGNACIÓN")

    # ======================================================
    # MODIFICAR HORARIO
    # ======================================================

    def modificar_horario(self):

        if not self.id_seleccionado:

            QMessageBox.warning(
                self,
                "Selecciona un horario",
                "Selecciona un horario de la tabla."
            )

            return

        id_maestro = self.obtener_id_maestro_seleccionado()
        id_materia = self.obtener_id_materia_seleccionada()

        if not id_maestro or not id_materia:

            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Selecciona un maestro y una materia."
            )

            return

        if not self.validar_horas():
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar modificación",
            "¿Deseas guardar los cambios de este horario?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        inicio = self.hora_inicio.time().toString("HH:mm:ss")
        fin = self.hora_fin.time().toString("HH:mm:ss")

        dia = self.combo_dia.currentText()

        valido, mensaje = self.validar_empalme(
            id_maestro,
            dia,
            inicio,
            fin,
            int(self.id_seleccionado)
        )

        if not valido:

            QMessageBox.warning(
                self,
                "Conflicto de horario",
                mensaje
            )

            return

        conexion = None
        cursor = None

        try:

            conexion = self.obtener_conexion_mysql()

            cursor = conexion.cursor()

            cursor.execute("""
                UPDATE tblHorarios
                SET
                    id_maestro = %s,
                    id_materia = %s,
                    dia = %s,
                    hora_inicio = %s,
                    hora_fin = %s
                WHERE id_horario = %s
                AND estado = 'ACTIVO'
            """, (
                id_maestro,
                id_materia,
                dia,
                inicio,
                fin,
                int(self.id_seleccionado)
            ))

            if cursor.rowcount == 0:

                cursor.execute("""
                    SELECT id_horario
                    FROM tblHorarios
                    WHERE id_horario = %s
                    AND estado = 'ACTIVO'
                """, (
                    int(self.id_seleccionado),
                ))

                if not cursor.fetchone():

                    raise ValueError(
                        "No se encontró el horario seleccionado."
                    )

            conexion.commit()

            QMessageBox.information(
                self,
                "Actualización correcta",
                "El horario se modificó correctamente en MySQL."
            )

            self.limpiar_formulario()
            self.cargar_horarios()

        except Exception as error:

            if conexion:
                conexion.rollback()

            QMessageBox.critical(
                self,
                "Error al modificar",
                f"No fue posible modificar el horario:\n\n{error}"
            )

        finally:

            if cursor:
                cursor.close()

            if conexion:
                conexion.close()

    # ======================================================
    # DESACTIVAR HORARIO
    # ======================================================

    def eliminar_horario(self):

        if not self.id_seleccionado:

            QMessageBox.warning(
                self,
                "Selecciona un horario",
                "Selecciona un horario de la tabla."
            )

            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar desactivación",
            "¿Deseas desactivar este horario?\n\n"
            "El registro dejará de aparecer entre los horarios activos, "
            "pero se conservará en MySQL para proteger el historial.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        conexion = None
        cursor = None

        try:

            conexion = self.obtener_conexion_mysql()

            cursor = conexion.cursor()

            cursor.execute("""
                UPDATE tblHorarios
                SET estado = 'INACTIVO'
                WHERE id_horario = %s
                AND estado = 'ACTIVO'
            """, (
                int(self.id_seleccionado),
            ))

            if cursor.rowcount == 0:

                raise ValueError(
                    "No se encontró un horario activo con ese identificador."
                )

            conexion.commit()

            QMessageBox.information(
                self,
                "Horario desactivado",
                "El horario se desactivó correctamente en MySQL."
            )

            self.limpiar_formulario()
            self.cargar_horarios()

        except Exception as error:

            if conexion:
                conexion.rollback()

            QMessageBox.critical(
                self,
                "Error al desactivar",
                f"No fue posible desactivar el horario:\n\n{error}"
            )

        finally:

            if cursor:
                cursor.close()

            if conexion:
                conexion.close()

    # ======================================================
    # ACTUALIZAR LISTAS
    # ======================================================

    def actualizar_listas(self):

        self.cargar_datos()
        self.cargar_horarios()

        self.txt_buscar.clear()

    # ======================================================
    # LIMPIAR FORMULARIO
    # ======================================================

    def limpiar_formulario(self):

        self.id_seleccionado = None

        self.tabla.clearSelection()

        if self.combo_maestro.count() > 0:
            self.combo_maestro.setCurrentIndex(0)

        if self.combo_materia.count() > 0:
            self.combo_materia.setCurrentIndex(0)

        self.combo_dia.setCurrentIndex(0)

        self.hora_inicio.setTime(
            QTime(17, 0)
        )

        self.hora_fin.setTime(
            QTime(19, 0)
        )

        self.actualizar_informacion_materia()
        self.actualizar_estado_botones()

        self.lbl_estado.setText(
            "Formulario listo para registrar una nueva asignación."
        )

    # ======================================================
    # ACTUALIZAR AL ENTRAR A LA SECCIÓN
    # ======================================================

    def showEvent(self, event):

        super().showEvent(event)

        self.actualizar_listas()
