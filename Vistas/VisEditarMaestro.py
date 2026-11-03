
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QFormLayout,
    QCheckBox
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

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(35, 25, 35, 25)
        layout_principal.setSpacing(20)

        titulo = QLabel("EDITAR MAESTRO")

        titulo.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #001F3F;
        """)

        descripcion = QLabel(
            "Modifica la información del maestro seleccionado."
        )

        descripcion.setStyleSheet("""
            font-size: 14px;
            color: #666666;
        """)

        formulario = QFormLayout()
        formulario.setSpacing(15)

        self.txt_id = QLineEdit()
        self.txt_id.setReadOnly(True)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre(s) del maestro")

        self.txt_apellidos = QLineEdit()
        self.txt_apellidos.setPlaceholderText("Apellidos del maestro")

        campos = [
            self.txt_id,
            self.txt_nombre,
            self.txt_apellidos
        ]

        for campo in campos:

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

                QLineEdit:read-only {
                    background-color: #EEEEEE;
                    color: #555555;
                }
            """)

        formulario.addRow("ID:", self.txt_id)
        formulario.addRow("Nombre(s):", self.txt_nombre)
        formulario.addRow("Apellidos:", self.txt_apellidos)

        self.chk_activo = QCheckBox("Maestro activo")
        self.chk_activo.setStyleSheet("""
            font-size: 14px;
            color: #003B73;
        """)

        self.btn_guardar = QPushButton("GUARDAR CAMBIOS")
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
        layout_principal.addLayout(formulario)
        layout_principal.addWidget(self.chk_activo)
        layout_principal.addLayout(botones)
        layout_principal.addStretch()

    def cargar_datos(self):

        self.txt_id.setText(
            str(self.maestro.get("id", ""))
        )

        self.txt_nombre.setText(
            self.maestro.get("nombre", "")
        )

        self.txt_apellidos.setText(
            self.maestro.get("apellidos", "")
        )

        self.chk_activo.setChecked(
            self.maestro.get("activo", True)
        )

    def guardar(self):

        nombre = self.txt_nombre.text().strip()
        apellidos = self.txt_apellidos.text().strip()
        activo = self.chk_activo.isChecked()

        if not nombre or not apellidos:

            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes ingresar nombre y apellidos."
            )

            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar cambios",
            "¿Deseas guardar los cambios del maestro?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        self.btn_guardar.setEnabled(False)

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
                "Error",
                f"No se pudieron actualizar los datos:\n{error}"
            )

        finally:
            self.btn_guardar.setEnabled(True)
