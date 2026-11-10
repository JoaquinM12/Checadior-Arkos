
# ==========================================================
# ARKOS CHECADOR
# Archivo: Vistas/VisInicio.py
# Panel adaptable a diferentes resoluciones
# ==========================================================

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QGridLayout,
    QStackedWidget,
    QMessageBox,
    QScrollArea,
    QSizePolicy
)

from PySide6.QtCore import Qt, Signal, QTimer

from Configuracion.Firebase import db

from Servicios.ServicioAlmacenamiento import cargar_maestros
from Servicios.ServicioMaterias import cargar_materias

from Vistas.VisChecador import VisChecador
from Vistas.VisMaestros import VisMaestros
from Vistas.VisNuevoMaestro import VisNuevoMaestro
from Vistas.VisEditarMaestro import VisEditarMaestro
from Vistas.VisHorarios import VisHorarios
from Vistas.VisMaterias import VisMaterias


# ==========================================================
# COLORES
# ==========================================================

AZUL_MARINO = "#001F3F"
AZUL = "#003B73"
NARANJA = "#FF851B"

FONDO = "#F1F5F9"
BLANCO = "#FFFFFF"

TEXTO = "#1E293B"
TEXTO_SECUNDARIO = "#64748B"

BORDE = "#E2E8F0"


# ==========================================================
# CLASE PRINCIPAL
# ==========================================================

class VisInicio(QWidget):

    cerrar_sesion_solicitado = Signal()

    def __init__(self):

        super().__init__()

        self.setObjectName("VisInicio")

        self.setStyleSheet("""
            QWidget#VisInicio {
                background-color: #F1F5F9;
            }
        """)

        self.indices = {}
        self.paginas_provisionales = {}

        self.pagina_registro_rostro = None
        self.pagina_editar_maestro = None

        self.indicadores = {}
        self.tarjetas_indicadores = []

        self.crear_interfaz()

        self.actualizar_fecha_hora_inicio()
        self.actualizar_supervision()

        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(
            self.actualizar_fecha_hora_inicio
        )
        self.timer_reloj.start(1000)

    # ======================================================
    # ADAPTACIÓN AL CAMBIO DE TAMAÑO
    # ======================================================

    def resizeEvent(self, event):

        super().resizeEvent(event)

        ancho = self.width()

        # Menú lateral adaptable
        if ancho < 850:
            self.menu_lateral.setFixedWidth(180)
        elif ancho < 1100:
            self.menu_lateral.setFixedWidth(205)
        else:
            self.menu_lateral.setFixedWidth(245)

        # Ajustar indicadores
        self.actualizar_distribucion_indicadores()

        # Ajustar encabezado y banner
        self.ajustar_elementos_responsivos(ancho)

    # ======================================================
    # DISTRIBUCIÓN RESPONSIVA DE INDICADORES
    # ======================================================

    def actualizar_distribucion_indicadores(self):

        if not hasattr(self, "grid_indicadores"):
            return

        ancho = self.scroll.viewport().width()

        if ancho < 650:
            columnas = 1
        else:
            columnas = 2

        # Eliminar posiciones anteriores
        while self.grid_indicadores.count():

            elemento = self.grid_indicadores.takeAt(0)

            if elemento.widget():
                elemento.widget().setParent(None)

        # Distribuir tarjetas
        for indice, tarjeta in enumerate(
            self.tarjetas_indicadores
        ):

            fila = indice // columnas
            columna = indice % columnas

            self.grid_indicadores.addWidget(
                tarjeta,
                fila,
                columna
            )

        for columna in range(2):
            self.grid_indicadores.setColumnStretch(
                columna,
                1 if columna < columnas else 0
            )

    # ======================================================
    # AJUSTES RESPONSIVOS DE ELEMENTOS
    # ======================================================

    def ajustar_elementos_responsivos(self, ancho):

        if not hasattr(self, "layout_encabezado"):
            return

        if ancho < 750:

            self.tarjeta_reloj.setMinimumWidth(180)
            self.tarjeta_reloj.setMaximumWidth(210)

            self.lbl_hora.setStyleSheet("""
                color: #003B73;
                font-size: 19px;
                font-weight: bold;
                background: transparent;
                border: none;
            """)

            self.boton_checador.setMinimumWidth(145)

        else:

            self.tarjeta_reloj.setMinimumWidth(235)
            self.tarjeta_reloj.setMaximumWidth(270)

            self.lbl_hora.setStyleSheet("""
                color: #003B73;
                font-size: 23px;
                font-weight: bold;
                background: transparent;
                border: none;
            """)

            self.boton_checador.setMinimumWidth(175)

        # En pantallas pequeñas, el contenido se compacta
        if ancho < 650:

            self.layout_contenido.setContentsMargins(
                12, 15, 12, 15
            )

            self.layout_contenido.setSpacing(14)

            self.banner.setMinimumHeight(165)
            self.banner.setMaximumHeight(190)

        elif ancho < 1000:

            self.layout_contenido.setContentsMargins(
                20, 20, 20, 18
            )

            self.layout_contenido.setSpacing(16)

            self.banner.setMinimumHeight(140)
            self.banner.setMaximumHeight(160)

        else:

            self.layout_contenido.setContentsMargins(
                30, 25, 30, 20
            )

            self.layout_contenido.setSpacing(20)

            self.banner.setMinimumHeight(135)
            self.banner.setMaximumHeight(155)

    # ======================================================
    # INTERFAZ PRINCIPAL
    # ======================================================

    def crear_interfaz(self):

        principal = QHBoxLayout(self)

        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        # ==================================================
        # MENÚ LATERAL
        # ==================================================

        self.menu_lateral = QFrame()
        self.menu_lateral.setFixedWidth(245)

        self.menu_lateral.setStyleSheet("""
            QFrame {
                background-color: #001F3F;
                border: none;
            }
        """)

        layout_menu = QVBoxLayout(self.menu_lateral)

        layout_menu.setContentsMargins(12, 22, 12, 18)
        layout_menu.setSpacing(7)

        logo = QLabel("ARKOS")
        logo.setAlignment(Qt.AlignCenter)

        logo.setStyleSheet("""
            color: #FFFFFF;
            font-size: 27px;
            font-weight: bold;
            letter-spacing: 3px;
            background: transparent;
            padding: 12px;
        """)

        subtitulo = QLabel("CHECADOR DOCENTE")
        subtitulo.setAlignment(Qt.AlignCenter)

        subtitulo.setStyleSheet("""
            color: #93C5FD;
            font-size: 10px;
            font-weight: bold;
            background: transparent;
            padding-bottom: 22px;
        """)

        layout_menu.addWidget(logo)
        layout_menu.addWidget(subtitulo)

        # ==================================================
        # CONTENEDOR DE PÁGINAS
        # ==================================================

        self.paginas = QStackedWidget()

        self.paginas.setStyleSheet("""
            QStackedWidget {
                background-color: #F1F5F9;
                border: none;
            }
        """)

        # ==================================================
        # INICIO
        # ==================================================

        self.pagina_inicio = self.crear_pagina_inicio()

        self.indices["Inicio"] = self.paginas.addWidget(
            self.pagina_inicio
        )

        # ==================================================
        # CHECADOR FACIAL
        # ==================================================

        self.pagina_checador = VisChecador()

        self.indices["Checador facial"] = (
            self.paginas.addWidget(self.pagina_checador)
        )

        # ==================================================
        # MAESTROS
        # ==================================================

        self.pagina_maestros = VisMaestros()

        self.indices["Maestros"] = self.paginas.addWidget(
            self.pagina_maestros
        )

        # ==================================================
        # NUEVO MAESTRO
        # ==================================================

        self.pagina_nuevo_maestro = VisNuevoMaestro()

        self.indices["Nuevo maestro"] = (
            self.paginas.addWidget(self.pagina_nuevo_maestro)
        )

        # ==================================================
        # MATERIAS
        # ==================================================

        self.pagina_materias = VisMaterias()

        self.indices["Materias"] = self.paginas.addWidget(
            self.pagina_materias
        )

        # ==================================================
        # HORARIOS
        # ==================================================

        self.pagina_horarios = VisHorarios()

        self.indices["Horarios"] = self.paginas.addWidget(
            self.pagina_horarios
        )

        # ==================================================
        # CONEXIONES
        # ==================================================

        self.pagina_maestros.nuevo_maestro_solicitado.connect(
            self.mostrar_nuevo_maestro
        )

        self.pagina_maestros.editar_maestro_solicitado.connect(
            self.mostrar_editar_maestro
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

        # ==================================================
        # BOTONES DEL MENÚ
        # ==================================================

        opciones = [
            "Inicio",
            "Checador facial",
            "Maestros",
            "Materias",
            "Horarios",
            "Asistencias",
            "Retardos",
            "Faltas",
            "Reportes",
            "Configuración"
        ]

        self.botones_menu = {}

        for opcion in opciones:

            boton = QPushButton(opcion)

            boton.setCursor(Qt.PointingHandCursor)
            boton.setMinimumHeight(42)
            boton.setCheckable(True)

            boton.setStyleSheet("""
                QPushButton {
                    color: #CBD5E1;
                    background-color: transparent;
                    border: none;
                    border-radius: 7px;
                    text-align: left;
                    padding-left: 13px;
                    font-size: 12px;
                }

                QPushButton:hover {
                    background-color: #003B73;
                    color: #FFFFFF;
                }

                QPushButton:checked {
                    background-color: #003B73;
                    color: #FFFFFF;
                    font-weight: bold;
                    border-left: 4px solid #FF851B;
                    padding-left: 9px;
                }
            """)

            boton.clicked.connect(
                lambda checked=False, nombre=opcion:
                self.cambiar_seccion(nombre)
            )

            layout_menu.addWidget(boton)

            self.botones_menu[opcion] = boton

        layout_menu.addStretch()

        # ==================================================
        # CERRAR SESIÓN
        # ==================================================

        cerrar = QPushButton("Cerrar sesión")

        cerrar.setMinimumHeight(42)
        cerrar.setCursor(Qt.PointingHandCursor)

        cerrar.setStyleSheet("""
            QPushButton {
                background-color: #991B1B;
                color: #FFFFFF;
                border: none;
                border-radius: 7px;
                font-weight: bold;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #DC2626;
            }
        """)

        cerrar.clicked.connect(
            self.cerrar_sesion_solicitado.emit
        )

        layout_menu.addWidget(cerrar)

        principal.addWidget(self.menu_lateral)
        principal.addWidget(self.paginas, 1)

        self.paginas.setCurrentIndex(
            self.indices["Inicio"]
        )

        self.botones_menu["Inicio"].setChecked(True)

    # ======================================================
    # CREAR PÁGINA DE INICIO
    # ======================================================

    def crear_pagina_inicio(self):

        pagina = QWidget()
        pagina.setObjectName("PaginaInicio")

        pagina.setStyleSheet("""
            QWidget#PaginaInicio {
                background-color: #F1F5F9;
            }
        """)

        layout_principal = QVBoxLayout(pagina)

        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # ==================================================
        # SCROLL
        # ==================================================

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(True)

        self.scroll.setFrameShape(QFrame.NoFrame)

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll.setStyleSheet("""
            QScrollArea {
                background-color: #F1F5F9;
                border: none;
            }

            QScrollBar:vertical {
                background: #E2E8F0;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #94A3B8;
                border-radius: 4px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #64748B;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        contenido = QWidget()

        contenido.setStyleSheet("""
            QWidget {
                background-color: #F1F5F9;
            }
        """)

        self.layout_contenido = QVBoxLayout(contenido)

        self.layout_contenido.setContentsMargins(
            30, 25, 30, 20
        )

        self.layout_contenido.setSpacing(20)

        # ==================================================
        # ENCABEZADO
        # ==================================================

        self.layout_encabezado = QHBoxLayout()
        self.layout_encabezado.setSpacing(15)

        bloque_titulo = QVBoxLayout()
        bloque_titulo.setSpacing(5)

        titulo = QLabel("Panel de supervisión")

        titulo.setWordWrap(True)

        titulo.setStyleSheet("""
            color: #001F3F;
            font-size: 27px;
            font-weight: bold;
            background: transparent;
        """)

        descripcion = QLabel(
            "Resumen general de la actividad académica."
        )

        descripcion.setWordWrap(True)

        descripcion.setStyleSheet("""
            color: #475569;
            font-size: 13px;
            background: transparent;
        """)

        bloque_titulo.addWidget(titulo)
        bloque_titulo.addWidget(descripcion)

        self.layout_encabezado.addLayout(
            bloque_titulo,
            1
        )

        # ==================================================
        # RELOJ
        # ==================================================

        self.tarjeta_reloj = QFrame()

        self.tarjeta_reloj.setMinimumHeight(75)

        self.tarjeta_reloj.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Fixed
        )

        self.tarjeta_reloj.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
        """)

        layout_reloj = QVBoxLayout(
            self.tarjeta_reloj
        )

        layout_reloj.setContentsMargins(
            12, 9, 12, 9
        )

        layout_reloj.setSpacing(4)

        self.lbl_fecha = QLabel()
        self.lbl_hora = QLabel()

        self.lbl_fecha.setAlignment(Qt.AlignRight)
        self.lbl_fecha.setWordWrap(True)

        self.lbl_hora.setAlignment(Qt.AlignRight)

        self.lbl_fecha.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)

        self.lbl_hora.setStyleSheet("""
            color: #003B73;
            font-size: 23px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)

        layout_reloj.addWidget(self.lbl_fecha)
        layout_reloj.addWidget(self.lbl_hora)

        self.layout_encabezado.addWidget(
            self.tarjeta_reloj
        )

        self.layout_contenido.addLayout(
            self.layout_encabezado
        )

        # ==================================================
        # BANNER
        # ==================================================

        self.banner = QFrame()

        self.banner.setMinimumHeight(135)
        self.banner.setMaximumHeight(170)

        self.banner.setStyleSheet("""
            QFrame {
                background-color: #001F3F;
                border: none;
                border-radius: 12px;
            }
        """)

        layout_banner = QHBoxLayout(self.banner)

        layout_banner.setContentsMargins(
            22, 18, 22, 18
        )

        layout_banner.setSpacing(15)

        texto_banner = QVBoxLayout()
        texto_banner.setSpacing(8)

        titulo_banner = QLabel("ARKOS CHECADOR")

        titulo_banner.setStyleSheet("""
            color: #FFFFFF;
            font-size: 23px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)

        descripcion_banner = QLabel(
            "Control de asistencia y supervisión de la actividad docente."
        )

        descripcion_banner.setWordWrap(True)

        descripcion_banner.setStyleSheet("""
            color: #E2E8F0;
            font-size: 13px;
            background: transparent;
            border: none;
        """)

        texto_banner.addWidget(titulo_banner)
        texto_banner.addWidget(descripcion_banner)
        texto_banner.addStretch()

        layout_banner.addLayout(texto_banner, 1)

        self.boton_checador = QPushButton(
            "Abrir checador facial"
        )

        self.boton_checador.setMinimumHeight(43)
        self.boton_checador.setCursor(Qt.PointingHandCursor)

        self.boton_checador.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Fixed
        )

        self.boton_checador.setStyleSheet("""
            QPushButton {
                background-color: #FF851B;
                color: #FFFFFF;
                border: none;
                border-radius: 7px;
                padding: 0 15px;
                font-size: 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #E66F0B;
            }

            QPushButton:pressed {
                background-color: #C75A00;
            }
        """)

        self.boton_checador.clicked.connect(
            lambda: self.cambiar_seccion("Checador facial")
        )

        layout_banner.addWidget(
            self.boton_checador
        )

        self.layout_contenido.addWidget(
            self.banner
        )

        # ==================================================
        # INDICADORES
        # ==================================================

        titulo_indicadores = QLabel(
            "Indicadores generales"
        )

        titulo_indicadores.setStyleSheet("""
            color: #001F3F;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)

        self.layout_contenido.addWidget(
            titulo_indicadores
        )

        self.grid_indicadores = QGridLayout()

        self.grid_indicadores.setSpacing(14)

        tarjetas = [
            (
                "maestros",
                "MAESTROS REGISTRADOS",
                "Total de docentes",
                "#003B73"
            ),
            (
                "materias",
                "MATERIAS REGISTRADAS",
                "Materias activas",
                "#0F766E"
            ),
            (
                "clases",
                "CLASES IMPARTIDAS",
                "Total histórico",
                "#7C3AED"
            ),
            (
                "asistencias",
                "ASISTENCIAS DE HOY",
                "Clases registradas hoy",
                "#EA580C"
            )
        ]

        for clave, titulo, detalle, color in tarjetas:

            tarjeta = QFrame()

            tarjeta.setMinimumHeight(125)

            tarjeta.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed
            )

            tarjeta.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 10px;
                }

                QFrame:hover {
                    border: 1px solid #94A3B8;
                }
            """)

            layout_tarjeta = QVBoxLayout(tarjeta)

            layout_tarjeta.setContentsMargins(
                17, 13, 17, 13
            )

            layout_tarjeta.setSpacing(5)

            lbl_titulo = QLabel(titulo)

            lbl_titulo.setWordWrap(True)

            lbl_titulo.setStyleSheet("""
                color: #475569;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                border: none;
            """)

            lbl_valor = QLabel("...")

            lbl_valor.setStyleSheet(f"""
                color: {color};
                font-size: 30px;
                font-weight: bold;
                background: transparent;
                border: none;
            """)

            lbl_detalle = QLabel(detalle)

            lbl_detalle.setWordWrap(True)

            lbl_detalle.setStyleSheet("""
                color: #64748B;
                font-size: 11px;
                background: transparent;
                border: none;
            """)

            layout_tarjeta.addWidget(lbl_titulo)
            layout_tarjeta.addWidget(lbl_valor)
            layout_tarjeta.addWidget(lbl_detalle)
            layout_tarjeta.addStretch()

            self.indicadores[clave] = lbl_valor

            self.tarjetas_indicadores.append(
                tarjeta
            )

        self.layout_contenido.addLayout(
            self.grid_indicadores
        )

        # ==================================================
        # ACTIVIDAD RECIENTE
        # ==================================================

        titulo_actividad = QLabel(
            "Actividad reciente"
        )

        titulo_actividad.setStyleSheet("""
            color: #001F3F;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)

        self.layout_contenido.addWidget(
            titulo_actividad
        )

        tarjeta_actividad = QFrame()

        tarjeta_actividad.setMinimumHeight(160)

        tarjeta_actividad.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )

        tarjeta_actividad.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
        """)

        layout_actividad = QVBoxLayout(
            tarjeta_actividad
        )

        layout_actividad.setContentsMargins(
            18, 15, 18, 15
        )

        self.lbl_actividad = QLabel(
            "Consultando actividad..."
        )

        self.lbl_actividad.setWordWrap(True)

        self.lbl_actividad.setMinimumHeight(110)

        self.lbl_actividad.setStyleSheet("""
            color: #334155;
            font-size: 12px;
            background: transparent;
            border: none;
        """)

        layout_actividad.addWidget(
            self.lbl_actividad
        )

        self.layout_contenido.addWidget(
            tarjeta_actividad
        )

        # ==================================================
        # PIE DE PÁGINA
        # ==================================================

        pie = QLabel(
            "ARKOS CHECADOR  |  Sistema de supervisión docente"
        )

        pie.setAlignment(Qt.AlignCenter)

        pie.setStyleSheet("""
            color: #64748B;
            font-size: 10px;
            background: transparent;
            padding: 8px;
        """)

        self.layout_contenido.addWidget(pie)

        self.layout_contenido.addStretch()

        self.scroll.setWidget(contenido) if hasattr(
            self, "scroll"
        ) else None

        self.scroll = self.scroll if hasattr(
            self, "scroll"
        ) else None

        # El scroll se asigna al layout al final
        self.scroll.setWidget(contenido)

        layout_principal.addWidget(self.scroll)

        return pagina

    # ======================================================
    # FECHA Y HORA
    # ======================================================

    def actualizar_fecha_hora_inicio(self):

        ahora = datetime.now()

        dias = [
            "lunes", "martes", "miércoles",
            "jueves", "viernes", "sábado", "domingo"
        ]

        meses = [
            "enero", "febrero", "marzo",
            "abril", "mayo", "junio",
            "julio", "agosto", "septiembre",
            "octubre", "noviembre", "diciembre"
        ]

        fecha = (
            f"{dias[ahora.weekday()]}, "
            f"{ahora.day} de "
            f"{meses[ahora.month - 1]} de "
            f"{ahora.year}"
        )

        hora = ahora.strftime("%I:%M:%S %p")

        self.lbl_fecha.setText(fecha)
        self.lbl_hora.setText(hora)

    # ======================================================
    # ACTUALIZAR INDICADORES
    # ======================================================

    def actualizar_supervision(self):

        # MAESTROS
        try:

            maestros = cargar_maestros()

            self.indicadores["maestros"].setText(
                str(len(maestros))
            )

        except Exception as error:

            print("ERROR AL CONTAR MAESTROS:", error)

            self.indicadores["maestros"].setText("--")

        # MATERIAS
        try:

            materias = cargar_materias(
                solo_activas=True
            )

            self.indicadores["materias"].setText(
                str(len(materias))
            )

        except Exception as error:

            print("ERROR AL CONTAR MATERIAS:", error)

            self.indicadores["materias"].setText("--")

        # CLASES IMPARTIDAS
        try:

            documentos = db.collection(
                "tblClasesImpartidas"
            ).stream()

            clases = []

            for documento in documentos:

                datos = documento.to_dict() or {}
                datos["id"] = documento.id

                clases.append(datos)

            self.indicadores["clases"].setText(
                str(len(clases))
            )

            fecha_hoy = datetime.now().strftime(
                "%Y-%m-%d"
            )

            asistencias_hoy = [
                clase
                for clase in clases
                if clase.get("fecha") == fecha_hoy
            ]

            self.indicadores["asistencias"].setText(
                str(len(asistencias_hoy))
            )

            clases.sort(
                key=lambda clase: (
                    clase.get("fecha", ""),
                    clase.get("hora_asistencia", "")
                ),
                reverse=True
            )

            recientes = clases[:5]

            if recientes:

                lineas = []

                for clase in recientes:

                    maestro = clase.get(
                        "maestro",
                        "Maestro no identificado"
                    )

                    materia = clase.get(
                        "materia",
                        "Materia no identificada"
                    )

                    fecha = clase.get(
                        "fecha",
                        "Sin fecha"
                    )

                    hora = clase.get(
                        "hora_asistencia",
                        "Sin hora"
                    )

                    carrera = clase.get("carrera", "")
                    cuatrimestre = clase.get("cuatrimestre", "")

                    contexto = " | ".join(
                        dato
                        for dato in [carrera, cuatrimestre]
                        if dato
                    )

                    linea = (
                        f"•  {maestro}\n"
                        f"    {materia}\n"
                        f"    {fecha}  |  {hora}"
                    )

                    if contexto:
                        linea += f"\n    {contexto}"

                    lineas.append(linea)

                self.lbl_actividad.setText(
                    "\n\n".join(lineas)
                )

                self.lbl_actividad.setAlignment(
                    Qt.AlignLeft | Qt.AlignVCenter
                )

            else:

                self.lbl_actividad.setText(
                    "Todavía no hay clases impartidas registradas."
                )

                self.lbl_actividad.setAlignment(
                    Qt.AlignCenter
                )

        except Exception as error:

            print(
                "ERROR AL CARGAR CLASES IMPARTIDAS:",
                error
            )

            self.indicadores["clases"].setText("--")
            self.indicadores["asistencias"].setText("--")

            self.lbl_actividad.setText(
                "No fue posible consultar la actividad reciente."
            )

    # ======================================================
    # NAVEGACIÓN
    # ======================================================

    def cambiar_seccion(self, nombre):

        if nombre == "Inicio":

            self.actualizar_supervision()

            self.paginas.setCurrentIndex(
                self.indices["Inicio"]
            )

        elif nombre == "Maestros":

            self.mostrar_maestros()
            return

        elif nombre == "Materias":

            self.pagina_materias.cargar_lista_materias()

            self.paginas.setCurrentIndex(
                self.indices["Materias"]
            )

        elif nombre == "Horarios":

            self.pagina_horarios.cargar_datos()
            self.pagina_horarios.cargar_horarios()

            self.paginas.setCurrentIndex(
                self.indices["Horarios"]
            )

        elif nombre in self.indices:

            self.paginas.setCurrentIndex(
                self.indices[nombre]
            )

        else:

            self.mostrar_pagina_provisional(nombre)
            return

        self.actualizar_boton_seleccionado(nombre)

    # ======================================================
    # BOTÓN SELECCIONADO
    # ======================================================

    def actualizar_boton_seleccionado(self, nombre):

        for nombre_boton, boton in self.botones_menu.items():

            boton.setChecked(
                nombre_boton == nombre
            )

    # ======================================================
    # MAESTROS
    # ======================================================

    def mostrar_maestros(self):

        self.pagina_maestros.actualizar_lista()

        self.paginas.setCurrentIndex(
            self.indices["Maestros"]
        )

        self.actualizar_boton_seleccionado(
            "Maestros"
        )

    # ======================================================
    # NUEVO MAESTRO
    # ======================================================

    def mostrar_nuevo_maestro(self):

        self.paginas.setCurrentIndex(
            self.indices["Nuevo maestro"]
        )

    def maestro_registrado(self, maestro):

        self.pagina_maestros.actualizar_lista()

        self.actualizar_supervision()

        self.paginas.setCurrentIndex(
            self.indices["Maestros"]
        )

        self.actualizar_boton_seleccionado(
            "Maestros"
        )

    # ======================================================
    # EDITAR MAESTRO
    # ======================================================

    def mostrar_editar_maestro(self, maestro):

        if self.pagina_editar_maestro is not None:

            self.paginas.removeWidget(
                self.pagina_editar_maestro
            )

            self.pagina_editar_maestro.deleteLater()

            self.pagina_editar_maestro = None

        self.pagina_editar_maestro = VisEditarMaestro(
            maestro
        )

        self.pagina_editar_maestro.cancelar_solicitado.connect(
            self.mostrar_maestros
        )

        self.pagina_editar_maestro.maestro_actualizado.connect(
            self.maestro_actualizado
        )

        indice = self.paginas.addWidget(
            self.pagina_editar_maestro
        )

        self.paginas.setCurrentIndex(indice)

    def maestro_actualizado(self, maestro):

        self.pagina_maestros.actualizar_lista()

        self.actualizar_supervision()

        self.paginas.setCurrentIndex(
            self.indices["Maestros"]
        )

        self.actualizar_boton_seleccionado(
            "Maestros"
        )

    # ======================================================
    # REGISTRO FACIAL
    # ======================================================

    def mostrar_registro_rostro(self, maestro):

        try:

            from Vistas.VisRostros import VisRostros

        except ImportError as error:

            QMessageBox.information(
                self,
                "Módulo pendiente",
                "El módulo de registro facial todavía no está "
                "disponible.\n\n"
                f"Detalle: {error}"
            )

            return

        if self.pagina_registro_rostro is not None:

            self.paginas.removeWidget(
                self.pagina_registro_rostro
            )

            self.pagina_registro_rostro.deleteLater()

            self.pagina_registro_rostro = None

        self.pagina_registro_rostro = VisRostros(
            maestro
        )

        self.pagina_registro_rostro.volver_solicitado.connect(
            self.mostrar_maestros
        )

        indice = self.paginas.addWidget(
            self.pagina_registro_rostro
        )

        self.paginas.setCurrentIndex(indice)

    # ======================================================
    # PÁGINAS PROVISIONALES
    # ======================================================

    def mostrar_pagina_provisional(self, nombre):

        if nombre in self.paginas_provisionales:

            self.paginas.setCurrentIndex(
                self.indices[nombre]
            )

            self.actualizar_boton_seleccionado(nombre)

            return

        pagina = QWidget()

        pagina.setStyleSheet("""
            QWidget {
                background-color: #F1F5F9;
            }
        """)

        layout = QVBoxLayout(pagina)

        layout.setContentsMargins(
            30, 25, 30, 25
        )

        titulo = QLabel(nombre)

        titulo.setStyleSheet("""
            color: #001F3F;
            font-size: 27px;
            font-weight: bold;
            background: transparent;
        """)

        mensaje = QLabel(
            "Esta sección todavía está pendiente de desarrollo."
        )

        mensaje.setStyleSheet("""
            color: #475569;
            font-size: 14px;
            background: transparent;
        """)

        layout.addWidget(titulo)
        layout.addWidget(mensaje)
        layout.addStretch()

        indice = self.paginas.addWidget(pagina)

        self.indices[nombre] = indice
        self.paginas_provisionales[nombre] = pagina

        self.paginas.setCurrentIndex(indice)

        self.actualizar_boton_seleccionado(nombre)
