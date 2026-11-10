
# ==========================================================
# VENTANA DE REGISTRO DE CLASE
# Archivo: Vistas/VisRegistroClase.py
# ==========================================================

from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QFrame,
    QMessageBox
)

from PySide6.QtCore import Qt

from Servicios.ServicioClasesImpartidas import (
    registrar_clase_impartida
)


class VisRegistroClase(QDialog):

    def __init__(
        self,
        maestro,
        horario,
        fecha_hora_reconocimiento,
        parent=None
    ):

        super().__init__(parent)

        self.maestro = maestro
        self.horario = horario

        self.fecha_hora_reconocimiento = (
            fecha_hora_reconocimiento
        )

        self.registro_guardado = False

        self.crear_interfaz()

    # ======================================================
    # INTERFAZ
    # ======================================================

    def crear_interfaz(self):

        self.setWindowTitle(
            "Registro de clase - ARKOS"
        )

        self.setMinimumSize(650, 650)

        self.setStyleSheet("""
            QDialog {
                background-color: #F4F6F9;
            }

            QLabel {
                color: #001F3F;
            }

            QTextEdit {
                background-color: white;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }

            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        principal = QVBoxLayout(self)

        principal.setContentsMargins(
            30, 25, 30, 25
        )

        principal.setSpacing(15)

        # TÍTULO

        titulo = QLabel(
            "REGISTRO DE CLASE"
        )

        titulo.setAlignment(Qt.AlignCenter)

        titulo.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #001F3F;
        """)

        principal.addWidget(titulo)

        # MAESTRO

        nombre = (
            self.maestro.get("nombre")
            or self.horario.get("maestro")
            or self.maestro.get("id", "")
        )

        lbl_maestro = QLabel(
            f"Maestro: {nombre}"
        )

        lbl_maestro.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
        """)

        principal.addWidget(lbl_maestro)

        # INFORMACIÓN DE LA CLASE

        tarjeta = QFrame()

        tarjeta.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)

        layout_tarjeta = QVBoxLayout(tarjeta)

        layout_tarjeta.setContentsMargins(
            20, 15, 20, 15
        )

        materia = self.horario.get(
            "materia",
            "Materia no disponible"
        )

        carrera = self.horario.get(
            "carrera",
            ""
        )

        cuatrimestre = self.horario.get(
            "cuatrimestre",
            ""
        )

        dia = self.horario.get(
            "dia",
            ""
        )

        inicio = self.horario.get(
            "hora_inicio",
            ""
        )

        fin = self.horario.get(
            "hora_fin",
            ""
        )

        hora_asistencia = (
            self.fecha_hora_reconocimiento.strftime(
                "%H:%M:%S"
            )
        )

        datos = [
            ("Materia", materia),
            ("Carrera", carrera),
            ("Cuatrimestre", cuatrimestre),
            ("Día", dia),
            ("Horario", f"{inicio} - {fin}"),
            ("Hora de asistencia", hora_asistencia)
        ]

        for etiqueta, valor in datos:

            fila = QHBoxLayout()

            lbl_etiqueta = QLabel(etiqueta)

            lbl_etiqueta.setStyleSheet("""
                color: #64748B;
                font-size: 13px;
            """)

            lbl_valor = QLabel(str(valor))

            lbl_valor.setStyleSheet("""
                color: #001F3F;
                font-size: 14px;
                font-weight: bold;
            """)

            fila.addWidget(lbl_etiqueta)

            fila.addStretch()

            fila.addWidget(lbl_valor)

            layout_tarjeta.addLayout(fila)

        principal.addWidget(tarjeta)

        # TEMAS

        lbl_temas = QLabel(
            "TEMAS QUE SE IMPARTIRÁN EN ESTA CLASE"
        )

        lbl_temas.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
        """)

        principal.addWidget(lbl_temas)

        self.txt_temas = QTextEdit()

        self.txt_temas.setPlaceholderText(
            "Escribe los temas que impartirás en esta clase...\n\n"
            "Ejemplo:\n"
            "1. Introducción al tema.\n"
            "2. Desarrollo de conceptos.\n"
            "3. Actividad práctica."
        )

        principal.addWidget(
            self.txt_temas,
            1
        )

        # BOTONES

        botones = QHBoxLayout()

        self.btn_cancelar = QPushButton(
            "CANCELAR"
        )

        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #64748B;
                color: white;
            }

            QPushButton:hover {
                background-color: #475569;
            }
        """)

        self.btn_guardar = QPushButton(
            "GUARDAR TEMAS Y ASISTENCIA"
        )

        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #003B73;
                color: white;
            }

            QPushButton:hover {
                background-color: #1677C8;
            }
        """)

        self.btn_cancelar.clicked.connect(
            self.reject
        )

        self.btn_guardar.clicked.connect(
            self.guardar
        )

        botones.addWidget(self.btn_cancelar)

        botones.addWidget(self.btn_guardar, 2)

        principal.addLayout(botones)

    # ======================================================
    # GUARDAR
    # ======================================================

    def guardar(self):

        temas = self.txt_temas.toPlainText().strip()

        if not temas:

            QMessageBox.warning(
                self,
                "Temas pendientes",
                "Debes escribir los temas de la clase."
            )

            return

        self.btn_guardar.setEnabled(False)

        try:

            registrar_clase_impartida(
                maestro=self.maestro,
                horario=self.horario,
                fecha_hora_reconocimiento=(
                    self.fecha_hora_reconocimiento
                ),
                temas=temas
            )

            self.registro_guardado = True

            QMessageBox.information(
                self,
                "Registro completado",
                "Los temas y la asistencia se guardaron "
                "correctamente en Firebase."
            )

            self.accept()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al guardar",
                str(error)
            )

            self.btn_guardar.setEnabled(True)
