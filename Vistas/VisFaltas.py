# ==========================================================
# ARKOS CHECADOR
# Archivo: Vistas/VisFaltas.py
# Diseño visual de la sección de faltas
# ==========================================================

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QScrollArea,
)


class VisFaltas(QWidget):

    def __init__(self):
        super().__init__()
        self.setObjectName("paginaFaltas")
        self.crear_estilos()
        self.crear_interfaz()

    def crear_estilos(self):
        self.setStyleSheet("""
            QWidget#paginaFaltas { background: #FFFFFF; color: #1B2E43; font-family: "Segoe UI"; }
            QScrollArea#scrollFaltas { background: #FFFFFF; border: none; }
            QWidget#contenidoFaltas { background: #FFFFFF; }
            QFrame#hero { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #092746,stop:1 #14598C); border: none; border-radius: 18px; }
            QLabel#eyebrow { color: #F7B267; font-size: 9pt; font-weight: 800; letter-spacing: 1px; }
            QLabel#tituloHero { color: #FFFFFF; font-size: 23pt; font-weight: 800; }
            QLabel#textoHero { color: #C7D8E8; font-size: 10pt; }
            QLabel#iconoHero { color: #FFFFFF; background: #214E73; border: 1px solid #3A6485; border-radius: 15px; font-size: 20pt; font-weight: 800; }
            QLabel#tituloSeccion { color: #0B2D4B; font-size: 16pt; font-weight: 800; }
            QLabel#textoSecundario { color: #718096; font-size: 9pt; }
            QFrame#tarjetaDato { background: #FFFFFF; border: 1px solid #E1E8F0; border-radius: 14px; }
            QLabel#valorDato { color: #18334D; font-size: 24pt; font-weight: 800; }
            QLabel#nombreDato { color: #36536D; font-size: 9pt; font-weight: 700; }
            QLabel#estadoDato { color: #8998A7; font-size: 8pt; }
            QFrame#panelDetalle { background: #FFFFFF; border: 1px solid #E1E8F0; border-radius: 15px; }
            QFrame#encabezados { background: #F1F5F9; border-radius: 9px; }
            QLabel#tituloColumna { color: #64788C; font-size: 8pt; font-weight: 800; }
            QFrame#vacio { background: #FAFCFE; border: 1px dashed #CCD8E3; border-radius: 12px; }
            QLabel#iconoVacio { color: #A95D1D; background: #FFF1E2; border-radius: 24px; font-size: 14pt; font-weight: 800; }
            QLabel#tituloVacio { color: #29465F; font-size: 11pt; font-weight: 800; }
            QLabel#textoVacio { color: #7A8B9B; font-size: 9pt; }
        """)

    def crear_interfaz(self):
        base = QVBoxLayout(self)
        base.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("scrollFaltas")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        contenido = QWidget()
        contenido.setObjectName("contenidoFaltas")
        layout = QVBoxLayout(contenido)
        layout.setContentsMargins(26, 24, 26, 26)
        layout.setSpacing(19)
        layout.addWidget(self.crear_hero())
        layout.addWidget(self.crear_resumen())
        layout.addWidget(self.crear_detalle())
        layout.addStretch(1)

        scroll.setWidget(contenido)
        base.addWidget(scroll)

    def crear_hero(self):
        panel = QFrame()
        panel.setObjectName("hero")
        panel.setMinimumHeight(150)
        fila = QHBoxLayout(panel)
        fila.setContentsMargins(25, 22, 25, 22)
        fila.setSpacing(18)

        textos = QVBoxLayout()
        textos.setSpacing(6)
        eyebrow = QLabel("ARKOS  /  CONTROL DE ASISTENCIA")
        eyebrow.setObjectName("eyebrow")
        titulo = QLabel("Faltas")
        titulo.setObjectName("tituloHero")
        descripcion = QLabel("Vista de seguimiento de ausencias del personal docente.")
        descripcion.setObjectName("textoHero")
        descripcion.setWordWrap(True)
        textos.addWidget(eyebrow)
        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        icono = QLabel("F")
        icono.setObjectName("iconoHero")
        icono.setAlignment(Qt.AlignCenter)
        icono.setFixedSize(66, 66)
        fila.addLayout(textos, 1)
        fila.addWidget(icono, 0, Qt.AlignVCenter)
        return panel

    def crear_resumen(self):
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        titulo = QLabel("Resumen")
        titulo.setObjectName("tituloSeccion")
        descripcion = QLabel("Indicadores de ausencias")
        descripcion.setObjectName("textoSecundario")
        layout.addWidget(titulo)
        layout.addWidget(descripcion)

        tarjetas = QGridLayout()
        tarjetas.setContentsMargins(0, 2, 0, 0)
        tarjetas.setHorizontalSpacing(12)
        tarjetas.setVerticalSpacing(12)
        for columna, nombre in enumerate((
            "Faltas en el periodo", "Docentes con falta", "Materias afectadas"
        )):
            tarjeta = QFrame()
            tarjeta.setObjectName("tarjetaDato")
            tarjeta_layout = QVBoxLayout(tarjeta)
            tarjeta_layout.setContentsMargins(17, 15, 17, 15)
            tarjeta_layout.setSpacing(5)
            valor = QLabel("—")
            valor.setObjectName("valorDato")
            etiqueta = QLabel(nombre)
            etiqueta.setObjectName("nombreDato")
            estado = QLabel("Sin datos")
            estado.setObjectName("estadoDato")
            tarjeta_layout.addWidget(valor)
            tarjeta_layout.addWidget(etiqueta)
            tarjeta_layout.addWidget(estado)
            tarjetas.addWidget(tarjeta, 0, columna)
            tarjetas.setColumnStretch(columna, 1)
        layout.addLayout(tarjetas)
        return contenedor

    def crear_detalle(self):
        panel = QFrame()
        panel.setObjectName("panelDetalle")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(14)

        encabezado = QHBoxLayout()
        textos = QVBoxLayout()
        textos.setSpacing(4)
        titulo = QLabel("Detalle de faltas")
        titulo.setObjectName("tituloSeccion")
        descripcion = QLabel("Registros de ausencias")
        descripcion.setObjectName("textoSecundario")
        textos.addWidget(titulo)
        textos.addWidget(descripcion)
        encabezado.addLayout(textos)
        encabezado.addStretch(1)
        layout.addLayout(encabezado)

        columnas = QFrame()
        columnas.setObjectName("encabezados")
        fila = QHBoxLayout(columnas)
        fila.setContentsMargins(12, 10, 12, 10)
        fila.setSpacing(8)
        for texto in ("DOCENTE", "FECHA", "MATERIA", "OBSERVACIONES"):
            etiqueta = QLabel(texto)
            etiqueta.setObjectName("tituloColumna")
            fila.addWidget(etiqueta, 1)
        layout.addWidget(columnas)

        vacio = QFrame()
        vacio.setObjectName("vacio")
        vacio.setMinimumHeight(165)
        vacio_layout = QVBoxLayout(vacio)
        vacio_layout.setContentsMargins(18, 18, 18, 18)
        vacio_layout.setSpacing(7)
        vacio_layout.setAlignment(Qt.AlignCenter)
        icono = QLabel("F")
        icono.setObjectName("iconoVacio")
        icono.setAlignment(Qt.AlignCenter)
        icono.setFixedSize(48, 48)
        titulo_vacio = QLabel("Sin registros para mostrar")
        titulo_vacio.setObjectName("tituloVacio")
        titulo_vacio.setAlignment(Qt.AlignCenter)
        texto = QLabel("Las ausencias aparecerán aquí cuando se conecten los datos.")
        texto.setObjectName("textoVacio")
        texto.setAlignment(Qt.AlignCenter)
        texto.setWordWrap(True)
        vacio_layout.addWidget(icono, 0, Qt.AlignCenter)
        vacio_layout.addWidget(titulo_vacio)
        vacio_layout.addWidget(texto)
        layout.addWidget(vacio)
        return panel
