
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QGridLayout,
    QStackedWidget
)

from PySide6.QtCore import Qt, Signal

from Vistas.VisChecador import VisChecador
from Vistas.VisMaestros import VisMaestros
from Vistas.VisNuevoMaestro import VisNuevoMaestro


class VisInicio(QWidget):

    cerrar_sesion_solicitado = Signal()

    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                font-family: Segoe UI;
            }
        """)

        self.indices = {}
        self.pagina_registro_rostro = None

        self.crear_interfaz()

    def crear_interfaz(self):

        principal = QHBoxLayout(self)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        # =====================================
        # MENÚ LATERAL
        # =====================================

        menu = QFrame()
        menu.setFixedWidth(245)

        menu.setStyleSheet("""
            QFrame {
                background-color: #001F3F;
            }
        """)

        layout_menu = QVBoxLayout(menu)
        layout_menu.setContentsMargins(15, 25, 15, 20)
        layout_menu.setSpacing(8)

        logo = QLabel("ARKOS")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            color: white;
            font-size: 29px;
            font-weight: bold;
            letter-spacing: 3px;
            padding: 15px;
        """)

        subtitulo = QLabel("CHECADOR DOCENTE")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("""
            color: #FF851B;
            font-size: 11px;
            font-weight: bold;
            padding-bottom: 25px;
        """)

        layout_menu.addWidget(logo)
        layout_menu.addWidget(subtitulo)

        # =====================================
        # CONTENEDOR DE PANTALLAS
        # =====================================

        self.paginas = QStackedWidget()

        self.paginas.setStyleSheet("""
            QStackedWidget {
                background-color: #F4F6F9;
            }
        """)

        # Inicio
        self.pagina_inicio = self.crear_pagina_inicio()

        self.indices["Inicio"] = self.paginas.addWidget(
            self.pagina_inicio
        )

        # Checador
        self.pagina_checador = VisChecador()

        self.indices["Checador facial"] = self.paginas.addWidget(
            self.pagina_checador
        )

        # Maestros
        self.pagina_maestros = VisMaestros()

        self.indices["Maestros"] = self.paginas.addWidget(
            self.pagina_maestros
        )

        # Nuevo maestro
        self.pagina_nuevo_maestro = VisNuevoMaestro()

        self.indices["Nuevo maestro"] = self.paginas.addWidget(
            self.pagina_nuevo_maestro
        )

        # =====================================
        # CONEXIONES DE MAESTROS
        # =====================================

        self.pagina_maestros.nuevo_maestro_solicitado.connect(
            self.mostrar_nuevo_maestro
        )

        self.pagina_maestros.registro_rostro_solicitado.connect(
            self.mostrar_registro_rostro
        )

        self.pagina_nuevo_maestro.cancelar_solicitado.connect(
            self.mostrar_maestros
        )

        self.pagina_nuevo_maestro.maestro_guardado.connect(
            self.maestro_registrado
        )

        # =====================================
        # BOTONES DEL MENÚ
        # =====================================

        opciones = [
            "Inicio",
            "Checador facial",
            "Maestros",
            "Horarios",
            "Asistencias",
            "Retardos",
            "Faltas",
            "Reportes",
            "Configuración"
        ]

        for opcion in opciones:

            boton = QPushButton(opcion)
            boton.setCursor(Qt.PointingHandCursor)
            boton.setMinimumHeight(43)

            boton.setStyleSheet("""
                QPushButton {
                    color: #E2E8F0;
                    background-color: transparent;
                    border: none;
                    border-radius: 7px;
                    text-align: left;
                    padding-left: 15px;
                    font-size: 13px;
                }

                QPushButton:hover {
                    background-color: #003B73;
                    color: white;
                }
            """)

            boton.clicked.connect(
                lambda checked=False, nombre=opcion:
                self.cambiar_seccion(nombre)
            )

            layout_menu.addWidget(boton)

        layout_menu.addStretch()

        # =====================================
        # CERRAR SESIÓN
        # =====================================

        cerrar = QPushButton("Cerrar sesión")
        cerrar.setMinimumHeight(43)
        cerrar.setCursor(Qt.PointingHandCursor)

        cerrar.setStyleSheet("""
            QPushButton {
                background-color: #9F2929;
                color: white;
                border: none;
                border-radius: 7px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #DC2626;
            }
        """)

        cerrar.clicked.connect(
            self.cerrar_sesion_solicitado.emit
        )

        layout_menu.addWidget(cerrar)

        # =====================================
        # AGREGAR ELEMENTOS
        # =====================================

        principal.addWidget(menu)
        principal.addWidget(self.paginas)

    # =====================================
    # PANTALLA DE INICIO
    # =====================================

    def crear_pagina_inicio(self):

        pagina = QWidget()

        layout_contenido = QVBoxLayout(pagina)
        layout_contenido.setContentsMargins(35, 30, 35, 30)

        titulo = QLabel("Panel principal")

        titulo.setStyleSheet("""
            color: #001F3F;
            font-size: 27px;
            font-weight: bold;
        """)

        descripcion = QLabel(
            "Bienvenido al sistema ARKOS CHECADOR."
        )

        descripcion.setStyleSheet("""
            color: #64748B;
            font-size: 14px;
        """)

        layout_contenido.addWidget(titulo)
        layout_contenido.addWidget(descripcion)
        layout_contenido.addSpacing(25)

        tarjetas = QGridLayout()
        tarjetas.setSpacing(18)

        datos = [
            ("MAESTROS", "Administración docente"),
            ("HORARIOS", "Consulta de horarios"),
            ("ASISTENCIAS", "Control de asistencia"),
            ("REPORTES", "Reportes del sistema")
        ]

        for i, (nombre, detalle) in enumerate(datos):

            tarjeta = QFrame()
            tarjeta.setMinimumHeight(145)

            tarjeta.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 12px;
                    border: 1px solid #E2E8F0;
                }
            """)

            layout_tarjeta = QVBoxLayout(tarjeta)

            lbl_nombre = QLabel(nombre)

            lbl_nombre.setStyleSheet("""
                color: #003B73;
                font-size: 17px;
                font-weight: bold;
                border: none;
            """)

            lbl_detalle = QLabel(detalle)

            lbl_detalle.setStyleSheet("""
                color: #64748B;
                font-size: 12px;
                border: none;
            """)

            layout_tarjeta.addWidget(lbl_nombre)
            layout_tarjeta.addWidget(lbl_detalle)
            layout_tarjeta.addStretch()

            tarjetas.addWidget(
                tarjeta,
                i // 2,
                i % 2
            )

        layout_contenido.addLayout(tarjetas)
        layout_contenido.addStretch()

        return pagina

    # =====================================
    # NAVEGACIÓN
    # =====================================

    def cambiar_seccion(self, nombre):

        if nombre == "Maestros":
            self.mostrar_maestros()
            return

        if nombre in self.indices:

            self.paginas.setCurrentIndex(
                self.indices[nombre]
            )

            return

        self.mostrar_pagina_provisional(nombre)

    # =====================================
    # MAESTROS
    # =====================================

    def mostrar_maestros(self):

        self.pagina_maestros.actualizar_lista()

        self.paginas.setCurrentIndex(
            self.indices["Maestros"]
        )

    def mostrar_nuevo_maestro(self):

        self.paginas.setCurrentIndex(
            self.indices["Nuevo maestro"]
        )

    def maestro_registrado(self, maestro):

        self.pagina_maestros.actualizar_lista()

        self.paginas.setCurrentIndex(
            self.indices["Maestros"]
        )

    # =====================================
    # REGISTRO FACIAL
    # =====================================

    def mostrar_registro_rostro(self, maestro):

        # La pantalla se cargará cuando creemos VisRostros.py.
        from Vistas.VisRostros import VisRostros

        if self.pagina_registro_rostro is not None:

            self.paginas.removeWidget(
                self.pagina_registro_rostro
            )

            self.pagina_registro_rostro.deleteLater()

        self.pagina_registro_rostro = VisRostros(maestro)

        self.pagina_registro_rostro.volver_solicitado.connect(
            self.mostrar_maestros
        )

        indice = self.paginas.addWidget(
            self.pagina_registro_rostro
        )

        self.paginas.setCurrentIndex(indice)

    # =====================================
    # PÁGINAS PROVISIONALES
    # =====================================

    def mostrar_pagina_provisional(self, nombre):

        pagina = QWidget()
        layout = QVBoxLayout(pagina)

        titulo = QLabel(nombre)

        titulo.setStyleSheet("""
            color: #001F3F;
            font-size: 27px;
            font-weight: bold;
        """)

        mensaje = QLabel(
            "Esta sección todavía está pendiente de desarrollo."
        )

        mensaje.setStyleSheet("""
            color: #64748B;
            font-size: 14px;
        """)

        layout.addWidget(titulo)
        layout.addWidget(mensaje)
        layout.addStretch()

        indice = self.paginas.addWidget(pagina)

        self.indices[nombre] = indice

        self.paginas.setCurrentIndex(indice)
