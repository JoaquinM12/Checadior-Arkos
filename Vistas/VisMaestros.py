
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox
)

from PySide6.QtCore import Qt, Signal

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

    # =====================================
    # INTERFAZ
    # =====================================

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(30, 25, 30, 25)
        layout_principal.setSpacing(18)

        titulo = QLabel("ADMINISTRACIÓN DE MAESTROS")

        titulo.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #001F3F;
        """)

        descripcion = QLabel(
            "Consulta, registra y administra los maestros del sistema."
        )

        descripcion.setStyleSheet("""
            font-size: 14px;
            color: #64748B;
        """)

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(descripcion)

        # =====================================
        # BOTONES
        # =====================================

        botones = QHBoxLayout()
        botones.setSpacing(10)

        self.btn_nuevo = QPushButton("+ NUEVO MAESTRO")
        self.btn_actualizar = QPushButton("ACTUALIZAR")
        self.btn_editar = QPushButton("EDITAR MAESTRO")
        self.btn_rostro = QPushButton("REGISTRAR ROSTRO")

        for boton in (
            self.btn_nuevo,
            self.btn_actualizar,
            self.btn_editar,
            self.btn_rostro
        ):

            boton.setMinimumHeight(42)
            boton.setCursor(Qt.PointingHandCursor)

        self.btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: #003B73;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1677C8;
            }
        """)

        self.btn_actualizar.setStyleSheet("""
            QPushButton {
                background-color: #64748B;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #475569;
            }
        """)

        self.btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #D97706;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #B45309;
            }

            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #64748B;
            }
        """)

        self.btn_rostro.setStyleSheet("""
            QPushButton {
                background-color: #15803D;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #166534;
            }

            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #64748B;
            }
        """)

        botones.addWidget(self.btn_nuevo)
        botones.addWidget(self.btn_actualizar)
        botones.addWidget(self.btn_editar)
        botones.addWidget(self.btn_rostro)

        layout_principal.addLayout(botones)

        # =====================================
        # TABLA
        # =====================================

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

        self.tabla.verticalHeader().setVisible(False)

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 7px;
                gridline-color: #E2E8F0;
                font-size: 13px;
                color: #1E293B;
            }

            QHeaderView::section {
                background-color: #003B73;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }

            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #001F3F;
            }
        """)

        layout_principal.addWidget(self.tabla)

        # =====================================
        # TOTAL DE MAESTROS
        # =====================================

        self.lbl_total = QLabel("Total de maestros: 0")

        self.lbl_total.setStyleSheet("""
            color: #64748B;
            font-size: 13px;
            font-weight: bold;
        """)

        layout_principal.addWidget(self.lbl_total)

        # =====================================
        # CONEXIONES
        # =====================================

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

        self.tabla.itemSelectionChanged.connect(
            self.actualizar_botones
        )

        self.btn_editar.setEnabled(False)
        self.btn_rostro.setEnabled(False)

    # =====================================
    # ACTUALIZAR LISTA
    # =====================================

    def actualizar_lista(self):

        try:

            self.maestros = cargar_maestros()

            # Evitar señales mientras se llena la tabla
            self.tabla.blockSignals(True)

            self.tabla.clearContents()
            self.tabla.setRowCount(len(self.maestros))

            for fila, maestro in enumerate(self.maestros):

                id_maestro = maestro.get("id", "")
                nombre = maestro.get("nombre", "")
                apellidos = maestro.get("apellidos", "")
                activo = maestro.get("activo", True)
                fecha = maestro.get("fecha_registro", "")

                estado = "Activo" if activo else "Inactivo"

                valores = [
                    id_maestro,
                    nombre,
                    apellidos,
                    estado,
                    fecha
                ]

                for columna, valor in enumerate(valores):

                    elemento = QTableWidgetItem(str(valor))

                    elemento.setTextAlignment(
                        Qt.AlignCenter
                    )

                    self.tabla.setItem(
                        fila,
                        columna,
                        elemento
                    )

            # Restaurar señales
            self.tabla.blockSignals(False)

            # Actualizar total
            self.lbl_total.setText(
                f"Total de maestros: {len(self.maestros)}"
            )

            # Limpiar selección anterior
            self.tabla.clearSelection()
            self.tabla.setCurrentCell(-1, -1)

            self.actualizar_botones()

        except Exception as error:

            self.tabla.blockSignals(False)

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar la lista de maestros:\n{error}"
            )

    # =====================================
    # OBTENER MAESTRO SELECCIONADO
    # =====================================

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

    # =====================================
    # ACTUALIZAR BOTONES
    # =====================================

    def actualizar_botones(self):

        maestro = self.obtener_maestro_seleccionado()

        seleccionado = maestro is not None

        self.btn_editar.setEnabled(seleccionado)

        self.btn_rostro.setEnabled(
            seleccionado and maestro.get("activo", True)
        )

    # =====================================
    # ABRIR EDICIÓN
    # =====================================

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

    # =====================================
    # ABRIR REGISTRO FACIAL
    # =====================================

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
