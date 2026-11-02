
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QFormLayout
)

from PySide6.QtCore import Qt, Signal

from Servicios.ServicioAlmacenamiento import registrar_maestro


class VisNuevoMaestro(QWidget):

    maestro_guardado = Signal(dict)
    cancelar_solicitado = Signal()

    def __init__(self):
        super().__init__()

        self.crear_interfaz()

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(35, 25, 35, 25)
        layout_principal.setSpacing(20)

        titulo = QLabel("REGISTRAR NUEVO MAESTRO")
        titulo.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #001F3F;
        """)

        descripcion = QLabel(
            "Ingresa los datos del maestro para registrarlo en el sistema."
        )

        descripcion.setStyleSheet("""
            font-size: 14px;
            color: #666666;
        """)

        formulario = QFormLayout()
        formulario.setSpacing(15)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre(s) del maestro")

        self.txt_apellidos = QLineEdit()
        self.txt_apellidos.setPlaceholderText("Apellidos del maestro")

        for campo in (self.txt_nombre, self.txt_apellidos):
            campo.setMinimumHeight(42)
            campo.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #CCCCCC;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #1677C8;
                }
            """)

        formulario.addRow("Nombre(s):", self.txt_nombre)
        formulario.addRow("Apellidos:", self.txt_apellidos)

        self.lbl_id = QLabel(
            "El ID se asignará automáticamente al guardar."
        )
        self.lbl_id.setStyleSheet("""
            color: #003B73;
            font-size: 13px;
            padding: 5px;
        """)

        self.btn_guardar = QPushButton("GUARDAR MAESTRO")
        self.btn_guardar.setMinimumHeight(45)
        self.btn_guardar.setCursor(Qt.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #003B73;
                color: white;
                font-weight: bold;
                border-radius: 7px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1677C8;
            }
        """)

        self.btn_cancelar = QPushButton("CANCELAR")
        self.btn_cancelar.setMinimumHeight(45)
        self.btn_cancelar.setCursor(Qt.PointingHandCursor)

        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(
            self.cancelar_solicitado.emit
        )

        botones = QHBoxLayout()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(descripcion)
        layout_principal.addSpacing(10)
        layout_principal.addLayout(formulario)
        layout_principal.addWidget(self.lbl_id)
        layout_principal.addLayout(botones)
        layout_principal.addStretch()

    def guardar(self):

        nombre = self.txt_nombre.text().strip()
        apellidos = self.txt_apellidos.text().strip()

        if not nombre or not apellidos:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes ingresar el nombre y los apellidos del maestro."
            )
            return

        try:
            maestro = registrar_maestro(nombre, apellidos)

            self.lbl_id.setText(
                f"ID asignado: {maestro['id']}"
            )

            QMessageBox.information(
                self,
                "Registro exitoso",
                f"El maestro se registró correctamente.\n\n"
                f"Nombre: {maestro['nombre']} {maestro['apellidos']}\n"
                f"ID: {maestro['id']}"
            )

            self.txt_nombre.clear()
            self.txt_apellidos.clear()

            self.maestro_guardado.emit(maestro)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo registrar al maestro:\n{error}"
            )
