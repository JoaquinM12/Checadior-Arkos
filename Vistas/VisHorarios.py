
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTimeEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFrame,
    QAbstractItemView
)

from PySide6.QtCore import Qt, QTime

from Configuracion.Firebase import db
from Servicios.ServicioAlmacenamiento import cargar_maestros


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

COLECCION_HORARIOS = "tblHorarios"

DIAS = [
    "LUNES",
    "MARTES",
    "MIÉRCOLES",
    "JUEVES",
    "VIERNES",
    "SÁBADO"
]

CARRERAS = [
    "LAET",
    "LCON",
    "LDER"
]

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
# VENTANA DE HORARIOS
# ==========================================================

class VisHorarios(QWidget):

    def __init__(self):
        super().__init__()

        self.horarios = []
        self.maestros = []

        self.crear_interfaz()
        self.cargar_lista_maestros()
        self.cargar_horarios()

    # ======================================================
    # INTERFAZ
    # ======================================================

    def crear_interfaz(self):

        principal = QVBoxLayout(self)
        principal.setContentsMargins(25, 20, 25, 20)
        principal.setSpacing(15)

        # TÍTULO

        titulo = QLabel("ADMINISTRACIÓN DE HORARIOS")
        titulo.setStyleSheet("""
            font-size: 23px;
            font-weight: bold;
            color: #001F3F;
        """)

        principal.addWidget(titulo)

        descripcion = QLabel(
            "Registra y consulta los horarios de los maestros."
        )

        descripcion.setStyleSheet("""
            color: #64748B;
            font-size: 13px;
        """)

        principal.addWidget(descripcion)

        # FORMULARIO

        formulario = QFrame()
        formulario.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #DCE3EA;
                border-radius: 10px;
            }

            QLabel {
                color: #334155;
                font-weight: bold;
                border: none;
            }

            QLineEdit, QComboBox, QTimeEdit {
                background-color: #F8FAFC;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px;
                min-height: 22px;
            }

            QComboBox {
                selection-background-color: #003B73;
                selection-color: white;
            }

            QComboBox::drop-down {
                border: none;
                width: 28px;
            }

            QComboBox QAbstractItemView {
                background-color: white;
                color: #1E293B;
                selection-background-color: #003B73;
                selection-color: white;
                border: 1px solid #CBD5E1;
                outline: none;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QTimeEdit:focus {
                border: 1px solid #0074D9;
            }
        """)

        layout_formulario = QVBoxLayout(formulario)
        layout_formulario.setContentsMargins(18, 18, 18, 18)

        titulo_formulario = QLabel("REGISTRAR NUEVO HORARIO")
        titulo_formulario.setStyleSheet("""
            font-size: 16px;
            color: #001F3F;
        """)

        layout_formulario.addWidget(titulo_formulario)

        formulario_campos = QFormLayout()
        formulario_campos.setSpacing(12)

        # MAESTRO

        self.combo_maestro = QComboBox()
        self.combo_maestro.setMinimumHeight(38)

        formulario_campos.addRow(
            "Maestro:",
            self.combo_maestro
        )

        # DÍA

        self.combo_dia = QComboBox()
        self.combo_dia.setMinimumHeight(38)
        self.combo_dia.addItems(DIAS)

        formulario_campos.addRow(
            "Día:",
            self.combo_dia
        )

        # HORAS

        self.hora_inicio = QTimeEdit()
        self.hora_inicio.setDisplayFormat("HH:mm")
        self.hora_inicio.setTime(QTime(17, 0))

        self.hora_fin = QTimeEdit()
        self.hora_fin.setDisplayFormat("HH:mm")
        self.hora_fin.setTime(QTime(19, 0))

        formulario_campos.addRow(
            "Hora de inicio:",
            self.hora_inicio
        )

        formulario_campos.addRow(
            "Hora de fin:",
            self.hora_fin
        )

        # MATERIA

        self.input_materia = QLineEdit()
        self.input_materia.setPlaceholderText(
            "Nombre de la materia"
        )

        formulario_campos.addRow(
            "Materia:",
            self.input_materia
        )

        # CARRERA

        self.combo_carrera = QComboBox()
        self.combo_carrera.setMinimumHeight(38)
        self.combo_carrera.addItems(CARRERAS)

        formulario_campos.addRow(
            "Carrera:",
            self.combo_carrera
        )

        # CUATRIMESTRE

        self.combo_cuatrimestre = QComboBox()
        self.combo_cuatrimestre.setMinimumHeight(38)
        self.combo_cuatrimestre.addItems(CUATRIMESTRES)

        formulario_campos.addRow(
            "Cuatrimestre:",
            self.combo_cuatrimestre
        )

        layout_formulario.addLayout(formulario_campos)

        # BOTÓN GUARDAR

        self.btn_guardar = QPushButton("GUARDAR HORARIO")
        self.btn_guardar.setCursor(Qt.PointingHandCursor)

        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #003B73;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 11px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #0074D9;
            }

            QPushButton:disabled {
                background-color: #94A3B8;
            }
        """)

        self.btn_guardar.clicked.connect(
            self.registrar_horario
        )

        layout_formulario.addWidget(self.btn_guardar)

        principal.addWidget(formulario)

        # TABLA

        titulo_tabla = QLabel("HORARIOS REGISTRADOS")

        titulo_tabla.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #001F3F;
        """)

        principal.addWidget(titulo_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)

        self.tabla.setHorizontalHeaderLabels([
            "ID",
            "MAESTRO",
            "DÍA",
            "INICIO",
            "FIN",
            "MATERIA",
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

        self.tabla.verticalHeader().setVisible(False)

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        self.tabla.horizontalHeader().setStretchLastSection(
            True
        )

        self.tabla.setAlternatingRowColors(True)

        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: #1E293B;
                alternate-background-color: #F1F5F9;
                border: 1px solid #DCE3EA;
                border-radius: 8px;
                gridline-color: #E2E8F0;
            }

            QHeaderView::section {
                background-color: #001F3F;
                color: white;
                padding: 9px;
                border: none;
                font-weight: bold;
            }
        """)

        principal.addWidget(self.tabla)

        # BOTONES INFERIORES

        botones = QHBoxLayout()

        self.btn_actualizar = QPushButton("ACTUALIZAR LISTA")
        self.btn_actualizar.setCursor(Qt.PointingHandCursor)

        self.btn_actualizar.clicked.connect(
            self.cargar_horarios
        )

        self.btn_actualizar.setStyleSheet("""
            QPushButton {
                background-color: #64748B;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px 18px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #475569;
            }
        """)

        botones.addWidget(self.btn_actualizar)
        botones.addStretch()

        principal.addLayout(botones)

    # ======================================================
    # CARGAR MAESTROS
    # ======================================================

    def cargar_lista_maestros(self):

        self.combo_maestro.clear()

        try:

            self.maestros = cargar_maestros() or []

            maestros_activos = []

            for maestro in self.maestros:

                if not isinstance(maestro, dict):
                    continue

                activo = maestro.get(
                    "activo",
                    maestro.get("Activo", True)
                )

                if activo is False:
                    continue

                identificador = maestro.get("id", "")
                nombre = maestro.get("nombre", "")
                apellidos = maestro.get("apellidos", "")

                nombre_completo = f"{nombre} {apellidos}".strip()

                if not identificador or not nombre_completo:
                    continue

                maestros_activos.append(maestro)

                self.combo_maestro.addItem(
                    f"{identificador} - {nombre_completo}",
                    maestro
                )

            if not maestros_activos:

                self.combo_maestro.addItem(
                    "No hay maestros activos",
                    None
                )

        except Exception as error:

            self.combo_maestro.addItem(
                "Error al cargar maestros",
                None
            )

            QMessageBox.critical(
                self,
                "Error al cargar maestros",
                f"No fue posible consultar los maestros en Firebase:\n\n{error}"
            )

    # ======================================================
    # GENERAR ID DE HORARIO
    # ======================================================

    def generar_id_horario(self):

        documentos = db.collection(
            COLECCION_HORARIOS
        ).stream()

        mayor = 0

        for documento in documentos:

            identificador = documento.id

            if identificador.startswith("HOR-"):

                try:
                    numero = int(
                        identificador.replace("HOR-", "")
                    )

                    mayor = max(mayor, numero)

                except ValueError:
                    continue

        return f"HOR-{mayor + 1:04d}"

    # ======================================================
    # REGISTRAR HORARIO
    # ======================================================

    def registrar_horario(self):

        maestro = self.combo_maestro.currentData()

        if maestro is None:

            QMessageBox.warning(
                self,
                "Maestro requerido",
                "Primero debes registrar un maestro activo."
            )

            return

        materia = self.input_materia.text().strip()

        hora_inicio = self.hora_inicio.time()
        hora_fin = self.hora_fin.time()

        if not materia:

            QMessageBox.warning(
                self,
                "Campo requerido",
                "Escribe el nombre de la materia."
            )

            self.input_materia.setFocus()
            return

        if hora_inicio >= hora_fin:

            QMessageBox.warning(
                self,
                "Horario incorrecto",
                "La hora de inicio debe ser anterior a la hora de fin."
            )

            return

        try:

            self.btn_guardar.setEnabled(False)

            identificador = self.generar_id_horario()

            datos = {
                "id": identificador,
                "id_maestro": maestro["id"],
                "maestro": (
                    maestro.get("nombre", "") + " " +
                    maestro.get("apellidos", "")
                ).strip(),
                "dia": self.combo_dia.currentText(),
                "hora_inicio": hora_inicio.toString("HH:mm"),
                "hora_fin": hora_fin.toString("HH:mm"),
                "materia": materia,
                "carrera": self.combo_carrera.currentText(),
                "cuatrimestre": self.combo_cuatrimestre.currentText(),
                "activo": True
            }

            db.collection(
                COLECCION_HORARIOS
            ).document(identificador).create(datos)

            QMessageBox.information(
                self,
                "Registro correcto",
                f"Horario registrado correctamente.\n\nID: {identificador}"
            )

            self.limpiar_formulario()
            self.cargar_horarios()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al guardar",
                f"No fue posible guardar el horario:\n\n{error}"
            )

        finally:

            self.btn_guardar.setEnabled(True)

    # ======================================================
    # CARGAR HORARIOS DESDE FIREBASE
    # ======================================================

    def cargar_horarios(self):

        try:

            self.btn_actualizar.setEnabled(False)

            documentos = db.collection(
                COLECCION_HORARIOS
            ).stream()

            self.horarios = []

            for documento in documentos:

                horario = documento.to_dict() or {}
                horario["id"] = documento.id

                if horario.get("activo", True):
                    self.horarios.append(horario)

            self.horarios.sort(
                key=lambda horario: (
                    horario.get("dia", ""),
                    horario.get("hora_inicio", "")
                )
            )

            self.mostrar_horarios()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No fue posible cargar los horarios:\n\n{error}"
            )

        finally:

            self.btn_actualizar.setEnabled(True)

    # ======================================================
    # MOSTRAR HORARIOS EN TABLA
    # ======================================================

    def mostrar_horarios(self):

        self.tabla.setRowCount(len(self.horarios))

        for fila, horario in enumerate(self.horarios):

            valores = [
                horario.get("id", ""),
                horario.get("maestro", ""),
                horario.get("dia", ""),
                horario.get("hora_inicio", ""),
                horario.get("hora_fin", ""),
                horario.get("materia", ""),
                horario.get("carrera", ""),
                horario.get("cuatrimestre", "")
            ]

            for columna, valor in enumerate(valores):

                elemento = QTableWidgetItem(str(valor))

                elemento.setTextAlignment(Qt.AlignCenter)

                self.tabla.setItem(
                    fila,
                    columna,
                    elemento
                )

        self.tabla.resizeRowsToContents()

    # ======================================================
    # LIMPIAR FORMULARIO
    # ======================================================

    def limpiar_formulario(self):

        self.input_materia.clear()

        self.combo_dia.setCurrentIndex(0)

        self.hora_inicio.setTime(QTime(17, 0))
        self.hora_fin.setTime(QTime(19, 0))

        self.combo_carrera.setCurrentIndex(0)
        self.combo_cuatrimestre.setCurrentIndex(0)
