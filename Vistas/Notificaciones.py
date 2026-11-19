
# ==========================================================
# ARKOS CHECADOR
# SISTEMA PERSONALIZADO DE NOTIFICACIONES
# Archivo: Vistas/Componentes/Notificaciones.py
# ==========================================================

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy
)

from PySide6.QtCore import (
    Qt,
    QTimer,
    QPoint
)

from PySide6.QtGui import QFont


class Notificaciones:

    # ======================================================
    # COLORES INSTITUCIONALES
    # ======================================================

    AZUL_MARINO = "#001F3F"
    AZUL = "#003B73"
    NARANJA = "#FF851B"

    VERDE = "#16A34A"
    ROJO = "#DC2626"
    AMARILLO = "#D97706"
    AZUL_INFO = "#2563EB"

    # ======================================================
    # NOTIFICACIONES TEMPORALES
    # ======================================================

    @staticmethod
    def exito(parent, mensaje, titulo="Operación exitosa"):

        Notificaciones._mostrar_toast(
            parent,
            titulo,
            mensaje,
            "✓",
            Notificaciones.VERDE
        )

    @staticmethod
    def informacion(parent, mensaje, titulo="Información"):

        Notificaciones._mostrar_toast(
            parent,
            titulo,
            mensaje,
            "i",
            Notificaciones.AZUL_INFO
        )

    # ======================================================
    # VENTANAS QUE REQUIEREN INTERACCIÓN
    # ======================================================

    @staticmethod
    def error(parent, mensaje, titulo="Ha ocurrido un error"):

        return Notificaciones._mostrar_dialogo(
            parent,
            titulo,
            mensaje,
            "✕",
            Notificaciones.ROJO,
            [("Aceptar", True)]
        )

    @staticmethod
    def advertencia(parent, mensaje, titulo="Advertencia"):

        return Notificaciones._mostrar_dialogo(
            parent,
            titulo,
            mensaje,
            "!",
            Notificaciones.AMARILLO,
            [("Entendido", True)]
        )

    @staticmethod
    def confirmar(
        parent,
        mensaje,
        titulo="Confirmar operación",
        texto_aceptar="Aceptar",
        texto_cancelar="Cancelar"
    ):

        resultado = Notificaciones._mostrar_dialogo(
            parent,
            titulo,
            mensaje,
            "?",
            Notificaciones.AZUL,
            [
                (texto_cancelar, False),
                (texto_aceptar, True)
            ]
        )

        return resultado is True

    # ======================================================
    # CREAR NOTIFICACIÓN TEMPORAL
    # ======================================================

    @staticmethod
    def _mostrar_toast(parent, titulo, mensaje, simbolo, color):

        toast = QWidget(
            parent,
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint
        )

        toast.setAttribute(
            Qt.WidgetAttribute.WA_DeleteOnClose
        )

        toast.setFixedWidth(370)

        toast.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: none;
                border-radius: 12px;
            }

            QLabel {
                border: none;
                background: transparent;
            }
        """)

        layout = QHBoxLayout(toast)
        layout.setContentsMargins(16, 15, 16, 15)
        layout.setSpacing(13)

        icono = QLabel(simbolo)
        icono.setFixedSize(43, 43)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icono.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 21px;
                font-size: 23px;
                font-weight: bold;
            }}
        """)

        textos = QVBoxLayout()
        textos.setSpacing(4)

        etiqueta_titulo = QLabel(titulo)
        etiqueta_titulo.setStyleSheet("""
            color: #001F3F;
            font-size: 14px;
            font-weight: bold;
        """)

        etiqueta_mensaje = QLabel(mensaje)
        etiqueta_mensaje.setWordWrap(True)
        etiqueta_mensaje.setStyleSheet("""
            color: #64748B;
            font-size: 12px;
        """)

        textos.addWidget(etiqueta_titulo)
        textos.addWidget(etiqueta_mensaje)

        layout.addWidget(icono)
        layout.addLayout(textos, 1)

        toast.adjustSize()

        # Posicionar en la esquina superior derecha
        if parent is not None:

            posicion = parent.mapToGlobal(
                QPoint(
                    parent.width() - toast.width() - 25,
                    25
                )
            )

            toast.move(posicion)

        else:

            pantalla = QApplication.primaryScreen()

            if pantalla:
                area = pantalla.availableGeometry()

                toast.move(
                    area.right() - toast.width() - 25,
                    area.top() + 25
                )

        toast.show()
        toast.raise_()

        # Desaparecer automáticamente
        QTimer.singleShot(
            3500,
            toast.close
        )

    # ======================================================
    # CREAR DIÁLOGO PERSONALIZADO
    # ======================================================

    @staticmethod
    def _mostrar_dialogo(
        parent,
        titulo,
        mensaje,
        simbolo,
        color,
        botones
    ):

        dialogo = QDialog(parent)

        dialogo.setWindowTitle(titulo)
        dialogo.setModal(True)
        dialogo.setFixedWidth(440)

        dialogo.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )

        dialogo.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 15px;
            }

            QLabel {
                border: none;
                background: transparent;
            }
        """)

        principal = QVBoxLayout(dialogo)
        principal.setContentsMargins(28, 28, 28, 25)
        principal.setSpacing(15)

        # --------------------------------------------------
        # ICONO
        # --------------------------------------------------

        contenedor_icono = QHBoxLayout()
        contenedor_icono.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        icono = QLabel(simbolo)
        icono.setFixedSize(65, 65)

        icono.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        icono.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 32px;
                font-size: 30px;
                font-weight: bold;
            }}
        """)

        contenedor_icono.addWidget(icono)
        principal.addLayout(contenedor_icono)

        # --------------------------------------------------
        # TITULO
        # --------------------------------------------------

        etiqueta_titulo = QLabel(titulo)

        etiqueta_titulo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        etiqueta_titulo.setWordWrap(True)

        etiqueta_titulo.setStyleSheet("""
            color: #001F3F;
            font-size: 19px;
            font-weight: bold;
        """)

        principal.addWidget(etiqueta_titulo)

        # --------------------------------------------------
        # MENSAJE
        # --------------------------------------------------

        etiqueta_mensaje = QLabel(mensaje)

        etiqueta_mensaje.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        etiqueta_mensaje.setWordWrap(True)

        etiqueta_mensaje.setStyleSheet("""
            color: #64748B;
            font-size: 13px;
        """)

        principal.addWidget(etiqueta_mensaje)

        # --------------------------------------------------
        # SEPARADOR
        # --------------------------------------------------

        separador = QFrame()
        separador.setFrameShape(
            QFrame.Shape.HLine
        )

        separador.setStyleSheet("""
            background-color: #E2E8F0;
            border: none;
            max-height: 1px;
        """)

        principal.addWidget(separador)

        # --------------------------------------------------
        # BOTONES
        # --------------------------------------------------

        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(10)

        resultado = {"valor": False}

        for texto, valor in botones:

            boton = QPushButton(texto)
            boton.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            boton.setFixedHeight(43)
            boton.setMinimumWidth(115)

            if valor:

                boton.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Notificaciones.AZUL};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: bold;
                        padding: 0 18px;
                    }}

                    QPushButton:hover {{
                        background-color: {Notificaciones.AZUL_MARINO};
                    }}

                    QPushButton:pressed {{
                        background-color: {Notificaciones.NARANJA};
                    }}
                """)

            else:

                boton.setStyleSheet("""
                    QPushButton {
                        background-color: #F1F5F9;
                        color: #334155;
                        border: 1px solid #E2E8F0;
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: bold;
                        padding: 0 18px;
                    }

                    QPushButton:hover {
                        background-color: #E2E8F0;
                    }
                """)

            def accion(checked=False, v=valor):
                resultado["valor"] = v
                dialogo.accept()

            boton.clicked.connect(accion)

            layout_botones.addWidget(boton)

        principal.addLayout(layout_botones)

        # --------------------------------------------------
        # CENTRAR EN LA VENTANA PADRE
        # --------------------------------------------------

        dialogo.adjustSize()

        if parent is not None:

            posicion = parent.mapToGlobal(
                QPoint(
                    (parent.width() - dialogo.width()) // 2,
                    (parent.height() - dialogo.height()) // 2
                )
            )

            dialogo.move(posicion)

        else:

            pantalla = QApplication.primaryScreen()

            if pantalla:
                area = pantalla.availableGeometry()

                dialogo.move(
                    area.center() - dialogo.rect().center()
                )

        dialogo.exec()

        return resultado["valor"]
