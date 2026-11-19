# ==========================================================
# ARKOS CHECADOR
# Archivo: Vistas/VisReportes.py
# Diseño visual de la sección de reportes
# ==========================================================

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QScrollArea,
)
from PySide6.QtGui import QPalette
from PySide6.QtCore import Qt


class VisReportes(QWidget):

    def __init__(self):
        super().__init__()
        self.crear_estilos()
        self.crear_interfaz()

    def crear_estilos(self):
        self.setStyleSheet("""
            QWidget#paginaReportes {
                background: #FFFFFF;
                color: #1B2E43;
                font-family: "Segoe UI";
            }

            QScrollArea#scrollReportes {
                background: transparent;
                border: none;
            }

            QFrame#heroReportes {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #092746, stop:1 #14598C);
                border: none;
                border-radius: 18px;
            }

            QLabel#etiquetaHero {
                color: #F7B267;
                font-size: 9pt;
                font-weight: 800;
                letter-spacing: 1px;
            }

            QLabel#tituloHero {
                color: #FFFFFF;
                font-size: 23pt;
                font-weight: 800;
            }

            QLabel#textoHero {
                color: #C7D8E8;
                font-size: 10pt;
            }

            QLabel#insigniaHero {
                color: #EAF4FD;
                background: #214E73;
                border: 1px solid #3A6485;
                border-radius: 10px;
                padding: 9px 13px;
                font-size: 8pt;
                font-weight: 800;
            }

            QLabel#tituloSeccionReportes {
                color: #0B2D4B;
                font-size: 17pt;
                font-weight: 800;
            }

            QLabel#descripcionSeccion {
                color: #718096;
                font-size: 9pt;
            }

            QFrame#tarjetaReporte {
                background: #FFFFFF;
                border: 1px solid #E1E8F0;
                border-radius: 15px;
            }

            QLabel#iconoReporte {
                border-radius: 11px;
                font-size: 13pt;
                font-weight: 900;
            }

            QLabel#tituloTarjetaReporte {
                color: #143858;
                font-size: 12pt;
                font-weight: 800;
            }

            QLabel#textoTarjetaReporte {
                color: #718096;
                font-size: 9pt;
            }

            QLabel#etiquetaEstadoReporte {
                color: #718096;
                background: #F1F5F9;
                border-radius: 8px;
                padding: 6px 9px;
                font-size: 8pt;
                font-weight: 700;
            }

            QFrame#panelResumen {
                background: #FFFFFF;
                border: 1px solid #E1E8F0;
                border-radius: 14px;
            }

            QLabel#tituloResumen {
                color: #143858;
                font-size: 10pt;
                font-weight: 800;
            }

            QLabel#textoResumen {
                color: #718096;
                font-size: 9pt;
            }
        """)

    def crear_interfaz(self):
        self.setObjectName("paginaReportes")
        paleta_blanca = self.palette()
        paleta_blanca.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
        self.setPalette(paleta_blanca)
        self.setAutoFillBackground(True)

        principal = QVBoxLayout(self)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("scrollReportes")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        paleta_scroll = scroll.viewport().palette()
        paleta_scroll.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
        scroll.viewport().setPalette(paleta_scroll)
        scroll.viewport().setAutoFillBackground(True)

        contenido = QWidget()
        paleta_contenido = contenido.palette()
        paleta_contenido.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
        contenido.setPalette(paleta_contenido)
        contenido.setAutoFillBackground(True)
        layout = QVBoxLayout(contenido)
        layout.setContentsMargins(28, 26, 28, 28)
        layout.setSpacing(22)

        layout.addWidget(self.crear_encabezado())
        layout.addWidget(self.crear_seccion_reportes())
        layout.addWidget(self.crear_resumen())
        layout.addStretch(1)

        scroll.setWidget(contenido)
        principal.addWidget(scroll)

    def crear_encabezado(self):
        hero = QFrame()
        hero.setObjectName("heroReportes")
        hero.setMinimumHeight(172)

        fila = QHBoxLayout(hero)
        fila.setContentsMargins(28, 23, 28, 23)
        fila.setSpacing(18)

        textos = QVBoxLayout()
        textos.setSpacing(7)

        etiqueta = QLabel("ARKOS  /  CENTRO DE INFORMES")
        etiqueta.setObjectName("etiquetaHero")

        titulo = QLabel("Reportes académicos")
        titulo.setObjectName("tituloHero")

        descripcion = QLabel(
            "Consulta visual de asistencia y actividad docente."
        )
        descripcion.setObjectName("textoHero")
        descripcion.setWordWrap(True)

        textos.addWidget(etiqueta)
        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        insignia = QLabel("PANEL DE REPORTES")
        insignia.setObjectName("insigniaHero")
        insignia.setAlignment(Qt.AlignCenter)
        insignia.setFixedWidth(150)

        fila.addLayout(textos, 1)
        fila.addWidget(insignia, 0, Qt.AlignVCenter)
        return hero

    def crear_tarjeta_reporte(self, iniciales, titulo, descripcion,
                              fondo_icono, color_icono):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaReporte")
        tarjeta.setMinimumHeight(172)

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(19, 17, 19, 17)
        layout.setSpacing(10)

        fila = QHBoxLayout()
        icono = QLabel(iniciales)
        icono.setObjectName("iconoReporte")
        icono.setAlignment(Qt.AlignCenter)
        icono.setFixedSize(42, 42)
        icono.setStyleSheet(
            f"background:{fondo_icono}; color:{color_icono};"
        )
        fila.addWidget(icono)
        fila.addStretch(1)

        estado = QLabel("SIN DATOS")
        estado.setObjectName("etiquetaEstadoReporte")
        fila.addWidget(estado, 0, Qt.AlignVCenter)

        titulo_label = QLabel(titulo)
        titulo_label.setObjectName("tituloTarjetaReporte")

        descripcion_label = QLabel(descripcion)
        descripcion_label.setObjectName("textoTarjetaReporte")
        descripcion_label.setWordWrap(True)

        layout.addLayout(fila)
        layout.addWidget(titulo_label)
        layout.addWidget(descripcion_label)
        layout.addStretch(1)
        return tarjeta

    def crear_seccion_reportes(self):
        seccion = QWidget()
        layout = QVBoxLayout(seccion)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(13)

        titulo = QLabel("Categorías de reporte")
        titulo.setObjectName("tituloSeccionReportes")
        descripcion = QLabel(
            "La información de cada categoría se mostrará en este espacio."
        )
        descripcion.setObjectName("descripcionSeccion")

        layout.addWidget(titulo)
        layout.addWidget(descripcion)

        tarjetas = QGridLayout()
        tarjetas.setContentsMargins(0, 3, 0, 0)
        tarjetas.setHorizontalSpacing(14)
        tarjetas.setVerticalSpacing(14)
        tarjetas.setColumnStretch(0, 1)
        tarjetas.setColumnStretch(1, 1)

        elementos = [
            ("AS", "Asistencia", "Resumen de registros de asistencia.",
             "#E5F1FB", "#17618F"),
            ("RE", "Retardos", "Vista de puntualidad y llegadas tardías.",
             "#FFF1E2", "#B96815"),
            ("FA", "Faltas", "Resumen de incidencias y ausencias.",
             "#FDEBEC", "#B6424B"),
            ("DO", "Personal docente", "Información general del personal.",
             "#E9F5EE", "#28734C"),
        ]

        for indice, datos in enumerate(elementos):
            fila, columna = divmod(indice, 2)
            tarjetas.addWidget(
                self.crear_tarjeta_reporte(*datos), fila, columna
            )

        layout.addLayout(tarjetas)
        return seccion

    def crear_resumen(self):
        panel = QFrame()
        panel.setObjectName("panelResumen")

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(19, 15, 19, 15)
        layout.setSpacing(12)

        marca = QLabel("i")
        marca.setAlignment(Qt.AlignCenter)
        marca.setFixedSize(28, 28)
        marca.setStyleSheet(
            "background:#EAF1F7; color:#17466D; border-radius:14px; "
            "font-weight:800;"
        )

        textos = QVBoxLayout()
        textos.setSpacing(3)
        titulo = QLabel("Vista de reportes")
        titulo.setObjectName("tituloResumen")
        descripcion = QLabel(
            "Esta pantalla presenta el diseño de la sección; los datos se integrarán después."
        )
        descripcion.setObjectName("textoResumen")
        descripcion.setWordWrap(True)
        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        layout.addWidget(marca, 0, Qt.AlignTop)
        layout.addLayout(textos, 1)
        return panel
