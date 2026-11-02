
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

    def __init__(self):
        super().__init__()

        self.crear_interfaz()
        self.actualizar_lista()

    def crear_interfaz(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(18)

        # =====================================
        # TÍTULO
        # =====================================

        titulo = QLabel("ADMINISTRACIÓN DE MAESTROS")
        titulo.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #001F3F;
        """)

        descripcion = QLabel(
            "Consulta y administra los maestros registrados en ARKOS."
        )

        descripcion.setStyleSheet("""
            font-size: 14px;
            color: #64748B;
        """)

        # =====================================
        # BOTONES
        # =====================================

        botones = QHBoxLayout()

        self.btn_nuevo = QPushButton("+ NUEVO MAESTRO")
        self.btn_actualizar = QPushButton("ACTUALIZAR")
        self.btn_registrar_rostro = QPushButton("REGISTRAR ROSTRO")

        for boton in (
            self.btn_nuevo,
            self.btn_actualizar,
            self.btn_registrar_rostro
        ):
            boton.setMinimumHeight(42)
            boton.setCursor(Qt.PointingHandCursor)

        self.btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: #003B73;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1677C8;
            }
        """)

        self.btn_actualizar.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                color: #001F3F;
                border: none;
                border-radius: 7px;
                padding: 10px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #CBD5E1;
            }
        """)

        self.btn_registrar_rostro.setStyleSheet("""
            QPushButton {
                background-color: #1677C8;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003B73;
            }
            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #64748B;
            }
        """)

        self.btn_nuevo.clicked.connect(
            self.nuevo_maestro_solicitado.emit
        )

        self.btn_actualizar.clicked.connect(
            self.actualizar_lista
        )

        self.btn_registrar_rostro.clicked.connect(
            self.abrir_registro_rostro
        )

        self.btn_registrar_rostro.setEnabled(False)

        botones.addWidget(self.btn_nuevo)
        botones.addWidget(self.btn_actualizar)
        botones.addWidget(self.btn_registrar_rostro)
        botones.addStretch()

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

        self.tabla.setRowCount(0)

        self.tabla.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.tabla.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabla.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.tabla.verticalHeader().setVisible(False)

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla.setMinimumHeight(300)

        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: #1E293B;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #E2E8F0;
                font-size: 13px;
            }

            QHeaderView::section {
                background-color: #003B73;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }

            QTableWidget::item {
                padding: 8px;
            }

            QTableWidget::item:selected {
                background-color: #DCEBFA;
                color: #001F3F;
            }
        """)

        self.tabla.itemSelectionChanged.connect(
            self.actualizar_estado_boton
        )

        # =====================================
        # TOTAL
        # =====================================

        self.lbl_total = QLabel("Total de maestros: 0")

        self.lbl_total.setStyleSheet("""
            color: #003B73;
            font-size: 14px;
            font-weight: bold;
        """)

        # =====================================
        # AGREGAR ELEMENTOS
        # =====================================

        layout.addWidget(titulo)
        layout.addWidget(descripcion)
        layout.addLayout(botones)
        layout.addWidget(self.tabla, 1)
        layout.addWidget(self.lbl_total)

    # =====================================
    # ACTUALIZAR LISTA
    # =====================================

    def actualizar_lista(self):

        try:

            maestros = cargar_maestros()

            self.tabla.clearContents()
            self.tabla.setRowCount(0)

            for maestro in maestros:

                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)

                valores = [
                    maestro.get("id", ""),
                    maestro.get("nombre", ""),
                    maestro.get("apellidos", ""),
                    "Activo" if maestro.get("activo", True) else "Inactivo",
                    maestro.get("fecha_registro", "")
                ]

                for columna, valor in enumerate(valores):

                    elemento = QTableWidgetItem(str(valor))

                    elemento.setTextAlignment(Qt.AlignCenter)

                    self.tabla.setItem(
                        fila,
                        columna,
                        elemento
                    )

            self.lbl_total.setText(
                f"Total de maestros: {self.tabla.rowCount()}"
            )

            self.tabla.resizeRowsToContents()

            self.btn_registrar_rostro.setEnabled(False)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar la lista de maestros:\n{error}"
            )

    # =====================================
    # VALIDAR SELECCIÓN
    # =====================================

    def actualizar_estado_boton(self):

        fila = self.tabla.currentRow()

        if fila < 0:
            self.btn_registrar_rostro.setEnabled(False)
            return

        estado = self.tabla.item(fila, 3)

        activo = estado is not None and estado.text() == "Activo"

        self.btn_registrar_rostro.setEnabled(activo)

    # =====================================
    # ABRIR REGISTRO FACIAL
    # =====================================

    def abrir_registro_rostro(self):

        fila = self.tabla.currentRow()

        if fila < 0:
            QMessageBox.warning(
                self,
                "Selecciona un maestro",
                "Primero debes seleccionar un maestro de la tabla."
            )
            return

        maestro = {
            "id": self.tabla.item(fila, 0).text(),
            "nombre": self.tabla.item(fila, 1).text(),
            "apellidos": self.tabla.item(fila, 2).text()
        }

        self.registro_rostro_solicitado.emit(maestro)
