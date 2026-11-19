# ==========================================================
# ARKOS CHECADOR
# Archivo: Vistas/VisConfiguracion.py
# Panel de configuracion general del sistema
# ==========================================================

import json
import cv2

from pathlib import Path
from datetime import datetime, date, time
from decimal import Decimal

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QTabWidget,
    QListWidget,
    QStackedWidget,
    QSpinBox,
    QComboBox,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QSizePolicy,
    QScrollArea,
    QFileDialog,
    QProgressBar,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox
)

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices

from Configuracion.ConexionMySQL import obtener_conexion
from Servicios.ServicioUsuarios import (
    ROLES,
    listar_usuarios,
    guardar_usuario,
    establecer_estado_usuario,
)


class VisConfiguracion(QWidget):

    volver_solicitado = Signal()

    RUTA_PROYECTO = Path(__file__).resolve().parent.parent
    RUTA_DATOS = RUTA_PROYECTO / "DatosLocales"
    RUTA_RESPALDOS = RUTA_DATOS / "Respaldos"
    RUTA_CONFIGURACION = RUTA_DATOS / "configuracion.json"

    VERSION = "1.0"

    RESOLUCIONES = {
        "640x480": (640, 480),
        "800x600": (800, 600),
        "1280x720": (1280, 720),
        "1920x1080": (1920, 1080)
    }

    def __init__(self):
        super().__init__()

        self.RUTA_DATOS.mkdir(parents=True, exist_ok=True)
        self.RUTA_RESPALDOS.mkdir(parents=True, exist_ok=True)

        self.configuracion = self.cargar_configuracion()

        self.crear_estilos()
        self.crear_interfaz()
        self.cargar_valores()
        self.actualizar_historial_respaldos()

    # ======================================================
    # ESTILOS
    # ======================================================

    def crear_estilos(self):

        self.setStyleSheet("""
            QWidget {
                background: #F4F7FB;
                color: #1B2E43;
                font-family: "Segoe UI";
                font-size: 10pt;
            }

            QLabel { background: transparent; }

            QFrame#barraSuperior {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #092746, stop:1 #14598C);
                border: none;
                border-radius: 16px;
            }

            QLabel#tituloPrincipal {
                color: #FFFFFF;
                font-size: 22pt;
                font-weight: 800;
            }

            QLabel#subtitulo {
                color: #C5D7E8;
                font-size: 9pt;
            }

            QFrame#panelNavegacion {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0A2A49, stop:1 #103B61);
                border: 1px solid #173D60;
                border-radius: 16px;
            }

            QLabel#marca {
                color: #FFFFFF;
                font-size: 19pt;
                font-weight: 900;
                letter-spacing: 1px;
            }

            QLabel#marcaDetalle {
                color: #AFC2D7;
                font-size: 8pt;
            }

            QLabel#navTitulo {
                color: #8FA9C4;
                font-size: 8pt;
                font-weight: 800;
                letter-spacing: 1px;
                padding: 10px 12px 4px 12px;
            }

            QListWidget#navegacion {
                background: transparent;
                border: none;
                outline: none;
                color: #D8E4F0;
                padding: 4px;
            }

            QListWidget#navegacion::item {
                min-height: 46px;
                padding: 0 12px;
                margin: 3px 0;
                border-radius: 9px;
                border-left: 3px solid transparent;
                color: #D8E4F0;
                font-weight: 600;
            }

            QListWidget#navegacion::item:hover {
                background: #173D60;
                color: #FFFFFF;
            }

            QListWidget#navegacion::item:selected {
                background: #194B72;
                border-left: 3px solid #F28C28;
                color: #FFFFFF;
                font-weight: 800;
            }

            QLabel#pieNavegacion {
                color: #91A9C1;
                font-size: 8pt;
            }

            QFrame#contenedorContenido {
                background: transparent;
                border: none;
            }

            QFrame#tarjeta {
                background: #FFFFFF;
                border: 1px solid #E2EAF2;
                border-radius: 15px;
            }

            QLabel#tituloSeccion {
                color: #0A2F50;
                font-size: 19pt;
                font-weight: 800;
            }

            QLabel#tituloTarjeta {
                color: #12395E;
                font-size: 11pt;
                font-weight: 800;
            }

            QLabel#descripcion {
                color: #687C91;
                font-size: 9pt;
            }

            QLabel#estado {
                color: #52677D;
                font-size: 9pt;
            }

            QLabel#estadoExito {
                color: #16804A;
                font-weight: 800;
            }

            QLabel#estadoError {
                color: #B42318;
                font-weight: 800;
            }

            QSpinBox, QComboBox, QLineEdit {
                background: #F8FAFC;
                border: 1px solid #D3DFEA;
                border-radius: 9px;
                padding: 9px 11px;
                min-height: 25px;
                color: #18334D;
                selection-background-color: #D5E8F7;
            }

            QSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border: 1px solid #2877B7;
                background: #FFFFFF;
            }

            QPushButton {
                border: none;
                border-radius: 9px;
                padding: 10px 16px;
                min-height: 22px;
                font-weight: 800;
            }

            QPushButton#principal {
                background: #07558C;
                color: #FFFFFF;
            }

            QPushButton#volverPanel {
                background: #173D60;
                color: #E7F0F8;
                border: 1px solid #315978;
                text-align: left;
            }

            QPushButton#volverPanel:hover {
                background: #21547B;
                border-color: #6E91AD;
            }

            QPushButton#principal:hover { background: #0B6EAD; }

            QPushButton#secundario {
                background: #EDF3F8;
                color: #17466D;
                border: 1px solid #D7E2EC;
            }

            QPushButton#secundario:hover {
                background: #DFEBF5;
                border-color: #B9CCDD;
            }

            QPushButton#exito {
                background: #16804A;
                color: #FFFFFF;
            }

            QPushButton#exito:hover { background: #11683C; }

            QPushButton#peligro {
                background: #A51D1D;
                color: #FFFFFF;
            }

            QPushButton#peligro:hover { background: #861717; }

            QPushButton:disabled {
                background: #E2E8F0;
                color: #94A3B8;
            }

            QTableWidget {
                background: #FFFFFF;
                alternate-background-color: #F7FAFC;
                border: 1px solid #E1E8F0;
                border-radius: 10px;
                gridline-color: #EDF1F5;
                selection-background-color: #DCEBFA;
                selection-color: #092746;
                outline: none;
            }

            QTableWidget::item { padding: 7px; }
            QTableWidget::item:hover { background: #EEF6FC; }

            QHeaderView::section {
                background: #EDF3F8;
                color: #17466D;
                padding: 11px 9px;
                border: none;
                border-bottom: 1px solid #DDE6EF;
                font-weight: 800;
            }

            QProgressBar {
                border: 1px solid #DCE4EE;
                border-radius: 7px;
                background: #EDF2F7;
                text-align: center;
                min-height: 16px;
            }

            QProgressBar::chunk {
                background: #16804A;
                border-radius: 5px;
            }

            QScrollArea { border: none; background: transparent; }

            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #B9C9D8;
                min-height: 28px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover { background: #8FA9C0; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

    # ======================================================
    # CONFIGURACION LOCAL
    # ======================================================

    def configuracion_predeterminada(self):

        return {
            "tolerancia_retardo": 10,
            "camara": 0,
            "resolucion": "1280x720"
        }

    def cargar_configuracion(self):

        predeterminada = self.configuracion_predeterminada()

        try:

            if self.RUTA_CONFIGURACION.exists():

                with open(
                    self.RUTA_CONFIGURACION,
                    "r",
                    encoding="utf-8"
                ) as archivo:

                    datos = json.load(archivo)

                    if isinstance(datos, dict):
                        predeterminada.update(datos)

        except Exception as error:

            print("[CONFIGURACION] Error al cargar:", error)

        return predeterminada

    def guardar_configuracion(self):

        try:

            datos = {
                "tolerancia_retardo": self.spin_tolerancia.value(),
                "camara": self.spin_camara.value(),
                "resolucion": self.combo_resolucion.currentText()
            }

            archivo_temporal = self.RUTA_CONFIGURACION.with_suffix(".tmp")

            with open(
                archivo_temporal,
                "w",
                encoding="utf-8"
            ) as archivo:

                json.dump(
                    datos,
                    archivo,
                    indent=4,
                    ensure_ascii=False
                )

            archivo_temporal.replace(self.RUTA_CONFIGURACION)

            self.configuracion = datos

            QMessageBox.information(
                self,
                "Configuración guardada",
                "Los ajustes se guardaron correctamente."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar la configuración:\n{error}"
            )

    def restablecer_configuracion(self):

        respuesta = QMessageBox.question(
            self,
            "Restablecer configuración",
            "¿Deseas regresar todos los ajustes a sus valores "
            "predeterminados?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        predeterminada = self.configuracion_predeterminada()

        self.spin_tolerancia.setValue(
            predeterminada["tolerancia_retardo"]
        )

        self.spin_camara.setValue(
            predeterminada["camara"]
        )

        self.combo_resolucion.setCurrentText(
            predeterminada["resolucion"]
        )

        self.guardar_configuracion()

    # ======================================================
    # COMPONENTES DE INTERFAZ
    # ======================================================

    def crear_tarjeta(self, titulo, descripcion=""):

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(11)

        etiqueta_titulo = QLabel(titulo)
        etiqueta_titulo.setObjectName("tituloTarjeta")

        layout.addWidget(etiqueta_titulo)

        if descripcion:

            etiqueta_descripcion = QLabel(descripcion)
            etiqueta_descripcion.setObjectName("descripcion")
            etiqueta_descripcion.setWordWrap(True)

            layout.addWidget(etiqueta_descripcion)

        return tarjeta, layout

    def crear_pagina_scroll(self):

        contenido = QWidget()

        layout = QVBoxLayout(contenido)
        layout.setContentsMargins(24, 22, 24, 24)
        layout.setSpacing(18)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(contenido)

        return scroll, layout

    # ======================================================
    # INTERFAZ PRINCIPAL
    # ======================================================

    def crear_interfaz(self):

        principal = QVBoxLayout(self)
        principal.setContentsMargins(22, 20, 22, 22)
        principal.setSpacing(16)

        encabezado = QFrame()
        encabezado.setObjectName("barraSuperior")
        encabezado.setFixedHeight(102)

        h = QHBoxLayout(encabezado)
        h.setContentsMargins(26, 16, 26, 16)

        bloque_titulo = QVBoxLayout()
        bloque_titulo.setSpacing(3)

        titulo = QLabel("Configuración del sistema")
        titulo.setObjectName("tituloPrincipal")

        subtitulo = QLabel(
            "Administra los parámetros y el mantenimiento de ARKOS CHECADOR"
        )
        subtitulo.setObjectName("subtitulo")

        bloque_titulo.addWidget(titulo)
        bloque_titulo.addWidget(subtitulo)

        h.addLayout(bloque_titulo)
        h.addStretch()

        indicador = QLabel("●  SISTEMA ARKOS")

        indicador.setStyleSheet(
            "color:#16804A; font-weight:800; "
            "background:#EAF7EF; padding:9px 14px; border-radius:8px;"
        )

        h.addWidget(indicador)

        principal.addWidget(encabezado)

        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(18)

        panel = QFrame()
        panel.setObjectName("panelNavegacion")
        panel.setFixedWidth(238)

        nav_layout = QVBoxLayout(panel)
        nav_layout.setContentsMargins(14, 20, 14, 16)
        nav_layout.setSpacing(9)

        marca = QLabel("ARKOS")
        marca.setObjectName("marca")

        detalle = QLabel("CHECADOR  ·  PANEL DE CONTROL")
        detalle.setObjectName("marcaDetalle")

        nav_layout.addWidget(marca)
        nav_layout.addWidget(detalle)

        btn_volver = QPushButton("←  Volver al panel principal")
        btn_volver.setObjectName("volverPanel")
        btn_volver.clicked.connect(self.volver_solicitado.emit)
        nav_layout.addWidget(btn_volver)
        nav_layout.addSpacing(12)

        etiqueta_nav = QLabel("CONFIGURACIÓN")
        etiqueta_nav.setObjectName("navTitulo")

        nav_layout.addWidget(etiqueta_nav)

        self.navegacion = QListWidget()
        self.navegacion.setObjectName("navegacion")
        self.navegacion.setSpacing(2)

        opciones = [
            "◈   General",
            "▣   Cámara",
            "▤   Base de datos",
            "⚙   Administración",
            "♙   Usuarios",
            "▣   Respaldos"
        ]

        self.navegacion.addItems(opciones)

        nav_layout.addWidget(self.navegacion, 1)

        pie = QLabel("ARKOS CHECADOR\nVersión " + self.VERSION)
        pie.setObjectName("pieNavegacion")
        pie.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        nav_layout.addWidget(pie)

        cuerpo.addWidget(panel)

        contenedor = QFrame()
        contenedor.setObjectName("contenedorContenido")

        contenido_layout = QVBoxLayout(contenedor)
        contenido_layout.setContentsMargins(0, 0, 0, 0)

        self.paginas = QStackedWidget()

        self.paginas.addWidget(self.crear_pestana_general())
        self.paginas.addWidget(self.crear_pestana_camara())
        self.paginas.addWidget(self.crear_pestana_base_datos())
        self.paginas.addWidget(self.crear_pestana_administracion())
        self.paginas.addWidget(self.crear_pestana_usuarios())
        self.paginas.addWidget(self.crear_pestana_respaldos())

        contenido_layout.addWidget(self.paginas)

        cuerpo.addWidget(contenedor, 1)

        principal.addLayout(cuerpo, 1)

        self.navegacion.currentRowChanged.connect(
            self.paginas.setCurrentIndex
        )

        self.navegacion.setCurrentRow(0)

    # ======================================================
    # PESTAÑA GENERAL
    # ======================================================

    def crear_pestana_general(self):

        pagina, layout = self.crear_pagina_scroll()

        titulo = QLabel("Preferencias generales")
        titulo.setObjectName("tituloSeccion")

        descripcion = QLabel(
            "Configura los parámetros que utiliza ARKOS CHECADOR "
            "durante el registro de asistencia."
        )

        descripcion.setObjectName("descripcion")
        descripcion.setWordWrap(True)

        layout.addWidget(titulo)
        layout.addWidget(descripcion)

        tarjeta, tarjeta_layout = self.crear_tarjeta(
            "Control de puntualidad",
            "Define el tiempo de tolerancia para clasificar "
            "los registros de asistencia."
        )

        fila = QHBoxLayout()

        etiqueta = QLabel("Tolerancia de retardo")

        self.spin_tolerancia = QSpinBox()
        self.spin_tolerancia.setRange(0, 60)
        self.spin_tolerancia.setSuffix(" minutos")
        self.spin_tolerancia.setFixedWidth(190)

        fila.addWidget(etiqueta)
        fila.addStretch()
        fila.addWidget(self.spin_tolerancia)

        tarjeta_layout.addLayout(fila)

        nota = QLabel(
            "Nota: este valor se guarda en la configuración local. "
            "El servicio que determina los retardos deberá leer este "
            "ajuste para aplicarlo al registro de clases."
        )

        nota.setObjectName("descripcion")
        nota.setWordWrap(True)

        tarjeta_layout.addWidget(nota)

        layout.addWidget(tarjeta)

        tarjeta_info, info_layout = self.crear_tarjeta(
            "Información de la instalación",
            "Datos generales de esta instalación de ARKOS."
        )

        self.lbl_nombre_sistema = QLabel("ARKOS CHECADOR")
        self.lbl_version = QLabel(f"Versión: {self.VERSION}")
        self.lbl_motor = QLabel("Motor de datos: MySQL")

        for etiqueta in (
            self.lbl_nombre_sistema,
            self.lbl_version,
            self.lbl_motor
        ):

            etiqueta.setObjectName("estado")
            info_layout.addWidget(etiqueta)

        layout.addWidget(tarjeta_info)

        tarjeta_archivos, archivos_layout = self.crear_tarjeta(
            "Archivos locales",
            "Ubicación de los archivos de configuración y respaldos."
        )

        self.lbl_ruta_configuracion = QLabel(
            str(self.RUTA_CONFIGURACION)
        )

        self.lbl_ruta_configuracion.setWordWrap(True)
        self.lbl_ruta_configuracion.setObjectName("estado")

        self.lbl_ruta_datos = QLabel(
            str(self.RUTA_DATOS)
        )

        self.lbl_ruta_datos.setWordWrap(True)
        self.lbl_ruta_datos.setObjectName("estado")

        archivos_layout.addWidget(
            QLabel("Archivo de configuración:")
        )

        archivos_layout.addWidget(self.lbl_ruta_configuracion)

        archivos_layout.addWidget(
            QLabel("Carpeta de datos:")
        )

        archivos_layout.addWidget(self.lbl_ruta_datos)

        layout.addWidget(tarjeta_archivos)

        botones = QHBoxLayout()
        botones.addStretch()

        btn_restaurar = QPushButton("RESTABLECER")
        btn_restaurar.setObjectName("secundario")

        btn_restaurar.clicked.connect(
            self.restablecer_configuracion
        )

        btn_guardar = QPushButton("GUARDAR CAMBIOS")
        btn_guardar.setObjectName("principal")

        btn_guardar.clicked.connect(
            self.guardar_configuracion
        )

        botones.addWidget(btn_restaurar)
        botones.addWidget(btn_guardar)

        layout.addLayout(botones)
        layout.addStretch()

        return pagina

    # ======================================================
    # PESTAÑA CAMARA
    # ======================================================

    def crear_pestana_camara(self):

        pagina, layout = self.crear_pagina_scroll()

        titulo = QLabel("Dispositivo de reconocimiento facial")
        titulo.setObjectName("tituloSeccion")

        descripcion = QLabel(
            "Selecciona la cámara que utilizará este equipo "
            "para el reconocimiento facial."
        )

        descripcion.setObjectName("descripcion")
        descripcion.setWordWrap(True)

        layout.addWidget(titulo)
        layout.addWidget(descripcion)

        tarjeta, tarjeta_layout = self.crear_tarjeta(
            "Configuración del dispositivo",
            "Los cambios se guardan localmente en este equipo."
        )

        fila_camara = QHBoxLayout()

        fila_camara.addWidget(QLabel("Número de cámara"))

        self.spin_camara = QSpinBox()
        self.spin_camara.setRange(0, 10)
        self.spin_camara.setFixedWidth(190)

        fila_camara.addStretch()
        fila_camara.addWidget(self.spin_camara)

        tarjeta_layout.addLayout(fila_camara)

        fila_resolucion = QHBoxLayout()

        fila_resolucion.addWidget(QLabel("Resolución"))

        self.combo_resolucion = QComboBox()

        self.combo_resolucion.addItems(
            list(self.RESOLUCIONES.keys())
        )

        self.combo_resolucion.setFixedWidth(190)

        fila_resolucion.addStretch()
        fila_resolucion.addWidget(self.combo_resolucion)

        tarjeta_layout.addLayout(fila_resolucion)

        layout.addWidget(tarjeta)

        tarjeta_prueba, prueba_layout = self.crear_tarjeta(
            "Diagnóstico de cámara",
            "Comprueba que el dispositivo seleccionado pueda abrirse "
            "y entregar imágenes."
        )

        self.lbl_estado_camara = QLabel("Sin comprobar")
        self.lbl_estado_camara.setObjectName("estado")

        self.lbl_detalle_camara = QLabel(
            "Selecciona una cámara y ejecuta la prueba."
        )

        self.lbl_detalle_camara.setObjectName("descripcion")
        self.lbl_detalle_camara.setWordWrap(True)

        self.btn_probar_camara = QPushButton("PROBAR CÁMARA")
        self.btn_probar_camara.setObjectName("secundario")

        self.btn_probar_camara.clicked.connect(
            self.probar_camara
        )

        prueba_layout.addWidget(self.lbl_estado_camara)
        prueba_layout.addWidget(self.lbl_detalle_camara)
        prueba_layout.addWidget(self.btn_probar_camara)

        layout.addWidget(tarjeta_prueba)

        botones = QHBoxLayout()
        botones.addStretch()

        btn_guardar = QPushButton("GUARDAR CONFIGURACIÓN")
        btn_guardar.setObjectName("principal")

        btn_guardar.clicked.connect(
            self.guardar_configuracion
        )

        botones.addWidget(btn_guardar)

        layout.addLayout(botones)
        layout.addStretch()

        return pagina

    # ======================================================
    # PESTAÑA BASE DE DATOS
    # ======================================================

    def crear_pestana_base_datos(self):

        pagina, layout = self.crear_pagina_scroll()

        titulo = QLabel("Conexión con MySQL")
        titulo.setObjectName("tituloSeccion")

        descripcion = QLabel(
            "Consulta el estado real de la conexión utilizada "
            "por ARKOS CHECADOR."
        )

        descripcion.setObjectName("descripcion")
        descripcion.setWordWrap(True)

        layout.addWidget(titulo)
        layout.addWidget(descripcion)

        tarjeta, tarjeta_layout = self.crear_tarjeta(
            "Estado del servidor",
            "La conexión utiliza los parámetros configurados "
            "en Configuracion/ConexionMySQL.py."
        )

        self.lbl_estado_mysql = QLabel("Sin comprobar")
        self.lbl_estado_mysql.setObjectName("estado")

        self.lbl_servidor_mysql = QLabel("Servidor: no consultado")
        self.lbl_servidor_mysql.setObjectName("estado")

        self.lbl_base_mysql = QLabel("Base de datos: no consultada")
        self.lbl_base_mysql.setObjectName("estado")

        self.lbl_version_mysql = QLabel("Versión: no consultada")
        self.lbl_version_mysql.setObjectName("estado")

        tarjeta_layout.addWidget(self.lbl_estado_mysql)
        tarjeta_layout.addWidget(self.lbl_servidor_mysql)
        tarjeta_layout.addWidget(self.lbl_base_mysql)
        tarjeta_layout.addWidget(self.lbl_version_mysql)

        self.btn_probar_mysql = QPushButton("COMPROBAR CONEXIÓN")
        self.btn_probar_mysql.setObjectName("principal")

        self.btn_probar_mysql.clicked.connect(
            self.probar_conexion_mysql
        )

        tarjeta_layout.addWidget(self.btn_probar_mysql)

        layout.addWidget(tarjeta)

        tarjeta_tablas, tablas_layout = self.crear_tarjeta(
            "Tablas de la base de datos",
            "Consulta las tablas disponibles y la cantidad de registros "
            "almacenados en cada una."
        )

        self.tabla_bd = QTableWidget()
        self.tabla_bd.setColumnCount(2)

        self.tabla_bd.setHorizontalHeaderLabels([
            "Tabla",
            "Registros"
        ])

        self.tabla_bd.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabla_bd.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabla_bd.setAlternatingRowColors(True)
        self.tabla_bd.verticalHeader().setVisible(False)

        self.tabla_bd.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )

        self.tabla_bd.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )

        self.tabla_bd.setMinimumHeight(220)

        self.btn_actualizar_tablas = QPushButton(
            "ACTUALIZAR TABLAS"
        )

        self.btn_actualizar_tablas.setObjectName("secundario")

        self.btn_actualizar_tablas.clicked.connect(
            self.consultar_tablas_bd
        )

        tablas_layout.addWidget(self.tabla_bd)
        tablas_layout.addWidget(self.btn_actualizar_tablas)

        layout.addWidget(tarjeta_tablas)
        layout.addStretch()

        return pagina

    # ======================================================
    # PESTAÑA ADMINISTRACION
    # ======================================================

    def crear_pestana_administracion(self):

        pagina, layout = self.crear_pagina_scroll()

        titulo = QLabel("Administración del sistema")
        titulo.setObjectName("tituloSeccion")

        descripcion = QLabel(
            "Herramientas de diagnóstico y mantenimiento "
            "de la instalación actual."
        )

        descripcion.setObjectName("descripcion")
        descripcion.setWordWrap(True)

        layout.addWidget(titulo)
        layout.addWidget(descripcion)

        tarjeta_bd, bd_layout = self.crear_tarjeta(
            "Diagnóstico de la base de datos",
            "Revisa la disponibilidad de las tablas principales "
            "del sistema."
        )

        self.lbl_diagnostico = QLabel(
            "Ejecuta el diagnóstico para consultar el estado."
        )

        self.lbl_diagnostico.setObjectName("estado")
        self.lbl_diagnostico.setWordWrap(True)

        btn_diagnostico = QPushButton("EJECUTAR DIAGNÓSTICO")
        btn_diagnostico.setObjectName("principal")

        btn_diagnostico.clicked.connect(
            self.ejecutar_diagnostico
        )

        bd_layout.addWidget(self.lbl_diagnostico)
        bd_layout.addWidget(btn_diagnostico)

        layout.addWidget(tarjeta_bd)

        tarjeta_archivos, archivos_layout = self.crear_tarjeta(
            "Carpetas del sistema",
            "Abre las ubicaciones donde ARKOS almacena "
            "sus archivos locales."
        )

        btn_abrir_datos = QPushButton("ABRIR CARPETA DE DATOS")
        btn_abrir_datos.setObjectName("secundario")

        btn_abrir_datos.clicked.connect(
            lambda: self.abrir_carpeta(self.RUTA_DATOS)
        )

        btn_abrir_respaldos = QPushButton(
            "ABRIR CARPETA DE RESPALDOS"
        )

        btn_abrir_respaldos.setObjectName("secundario")

        btn_abrir_respaldos.clicked.connect(
            lambda: self.abrir_carpeta(self.RUTA_RESPALDOS)
        )

        archivos_layout.addWidget(btn_abrir_datos)
        archivos_layout.addWidget(btn_abrir_respaldos)

        layout.addWidget(tarjeta_archivos)

        layout.addStretch()

        return pagina

    def crear_pestana_usuarios(self):
        pagina, layout = self.crear_pagina_scroll()

        titulo = QLabel("Usuarios y permisos")
        titulo.setObjectName("tituloSeccion")
        descripcion = QLabel(
            "Crea cuentas con usuario, contraseña y rol. También puedes "
            "editar cuentas o activar y desactivar el acceso."
        )
        descripcion.setObjectName("descripcion")
        descripcion.setWordWrap(True)
        layout.addWidget(titulo)
        layout.addWidget(descripcion)

        tarjeta, usuarios_layout = self.crear_tarjeta(
            "Administrar usuarios",
            "Las contraseñas se guardan con hash seguro y no se muestran en la tabla."
        )
        self.tabla_usuarios = QTableWidget(0, 5)
        self.tabla_usuarios.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Usuario", "Rol", "Estado"]
        )
        self.tabla_usuarios.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_usuarios.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_usuarios.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_usuarios.setAlternatingRowColors(True)
        self.tabla_usuarios.verticalHeader().setVisible(False)
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        for columna in (1, 2, 3, 4):
            self.tabla_usuarios.horizontalHeader().setSectionResizeMode(
                columna, QHeaderView.Stretch
            )
        self.tabla_usuarios.setMinimumHeight(260)
        self.tabla_usuarios.verticalHeader().setDefaultSectionSize(40)
        usuarios_layout.addWidget(self.tabla_usuarios)

        acciones_usuarios = QHBoxLayout()
        self.btn_crear_usuario = QPushButton("CREAR USUARIO")
        self.btn_crear_usuario.setObjectName("principal")
        self.btn_editar_usuario = QPushButton("EDITAR / CONTRASEÑA")
        self.btn_editar_usuario.setObjectName("secundario")
        self.btn_estado_usuario = QPushButton("ACTIVAR / DESACTIVAR")
        self.btn_estado_usuario.setObjectName("secundario")
        self.btn_actualizar_usuarios = QPushButton("ACTUALIZAR")
        self.btn_actualizar_usuarios.setObjectName("secundario")
        self.btn_crear_usuario.clicked.connect(self.crear_usuario)
        self.btn_editar_usuario.clicked.connect(self.editar_usuario)
        self.btn_estado_usuario.clicked.connect(self.cambiar_estado_usuario)
        self.btn_actualizar_usuarios.clicked.connect(self.cargar_usuarios)
        acciones_usuarios.addWidget(self.btn_crear_usuario)
        acciones_usuarios.addWidget(self.btn_editar_usuario)
        acciones_usuarios.addWidget(self.btn_estado_usuario)
        acciones_usuarios.addWidget(self.btn_actualizar_usuarios)
        usuarios_layout.addLayout(acciones_usuarios)

        self.lbl_estado_usuarios = QLabel("Cargando usuarios...")
        self.lbl_estado_usuarios.setObjectName("estado")
        usuarios_layout.addWidget(self.lbl_estado_usuarios)

        tarjeta_seguridad, seguridad_layout = self.crear_tarjeta(
            "Acceso y seguridad",
            "El inicio de sesión valida estas cuentas y rechaza las desactivadas."
        )
        estado_seguridad = QLabel(
            "Las contraseñas se protegen con PBKDF2-HMAC-SHA256."
        )
        estado_seguridad.setObjectName("estado")
        seguridad_layout.addWidget(estado_seguridad)

        layout.addWidget(tarjeta)
        layout.addWidget(tarjeta_seguridad)
        layout.addStretch()
        self.cargar_usuarios()
        return pagina

    def cargar_usuarios(self):
        if not hasattr(self, "tabla_usuarios"):
            return
        try:
            usuarios = listar_usuarios()
            self.tabla_usuarios.setRowCount(len(usuarios))
            for fila, usuario in enumerate(usuarios):
                id_usuario, nombre, login, rol, activo = usuario
                valores = (id_usuario, nombre, login, rol,
                           "Activo" if activo else "Inactivo")
                for columna, valor in enumerate(valores):
                    item = QTableWidgetItem(str(valor))
                    if columna == 0:
                        item.setData(Qt.UserRole, id_usuario)
                    self.tabla_usuarios.setItem(fila, columna, item)
            self.lbl_estado_usuarios.setText(
                f"{len(usuarios)} cuenta(s) registrada(s)."
            )
        except Exception as error:
            self.tabla_usuarios.setRowCount(0)
            self.lbl_estado_usuarios.setText(
                f"No se pudieron cargar los usuarios: {error}"
            )

    def dialogo_usuario(self, titulo, nombre="", usuario="", rol="Consulta",
                        es_nuevo=True):
        dialogo = QDialog(self)
        dialogo.setWindowTitle(titulo)
        dialogo.setObjectName("dialogoUsuario")
        dialogo.setFixedSize(360, 275)
        formulario = QFormLayout(dialogo)
        campo_nombre = QLineEdit(nombre)
        campo_usuario = QLineEdit(usuario)
        combo_rol = QComboBox()
        combo_rol.addItems(ROLES)
        combo_rol.setCurrentText(rol)
        campo_password = QLineEdit()
        campo_password.setEchoMode(QLineEdit.Password)
        campo_password.setPlaceholderText(
            "Obligatoria, mínimo 8 caracteres" if es_nuevo
            else "Déjala vacía para conservarla"
        )
        formulario.addRow("Nombre:", campo_nombre)
        formulario.addRow("Usuario:", campo_usuario)
        formulario.addRow("Rol:", combo_rol)
        formulario.addRow("Contraseña:", campo_password)
        botones = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        botones.accepted.connect(dialogo.accept)
        botones.rejected.connect(dialogo.reject)
        formulario.addRow(botones)
        if dialogo.exec() != QDialog.Accepted:
            return None
        return (campo_nombre.text(), campo_usuario.text(), combo_rol.currentText(),
                campo_password.text())

    def crear_usuario(self):
        datos = self.dialogo_usuario("Crear usuario", es_nuevo=True)
        if datos is None:
            return
        try:
            guardar_usuario(*datos[:3], password=datos[3])
            self.cargar_usuarios()
            QMessageBox.information(self, "Usuario creado", "La cuenta se creó correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "No se pudo crear", str(error))

    def fila_usuario_seleccionada(self):
        fila = self.tabla_usuarios.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Selecciona un usuario", "Elige una fila de la tabla.")
            return None
        return fila, self.tabla_usuarios.item(fila, 0).data(Qt.UserRole)

    def editar_usuario(self):
        seleccion = self.fila_usuario_seleccionada()
        if seleccion is None:
            return
        fila, id_usuario = seleccion
        datos = self.dialogo_usuario(
            "Editar usuario",
            self.tabla_usuarios.item(fila, 1).text(),
            self.tabla_usuarios.item(fila, 2).text(),
            self.tabla_usuarios.item(fila, 3).text(),
            es_nuevo=False
        )
        if datos is None:
            return
        try:
            guardar_usuario(*datos[:3], password=datos[3] or None,
                            id_usuario=id_usuario)
            self.cargar_usuarios()
            QMessageBox.information(self, "Usuario actualizado", "Los datos se guardaron correctamente.")
        except Exception as error:
            QMessageBox.critical(self, "No se pudo actualizar", str(error))

    def cambiar_estado_usuario(self):
        seleccion = self.fila_usuario_seleccionada()
        if seleccion is None:
            return
        fila, id_usuario = seleccion
        actualmente_activo = self.tabla_usuarios.item(fila, 4).text() == "Activo"
        try:
            establecer_estado_usuario(id_usuario, not actualmente_activo)
            self.cargar_usuarios()
        except Exception as error:
            QMessageBox.warning(self, "No se pudo cambiar el estado", str(error))

    # ======================================================
    # PESTAÑA RESPALDOS
    # ======================================================

    def crear_pestana_respaldos(self):

        pagina, layout = self.crear_pagina_scroll()

        titulo = QLabel("Respaldos de información")
        titulo.setObjectName("tituloSeccion")

        descripcion = QLabel(
            "Genera copias de seguridad de las tablas y registros "
            "almacenados en la base de datos MySQL."
        )

        descripcion.setObjectName("descripcion")
        descripcion.setWordWrap(True)

        layout.addWidget(titulo)
        layout.addWidget(descripcion)

        tarjeta, tarjeta_layout = self.crear_tarjeta(
            "Crear respaldo",
            "Se generará un archivo SQL con la estructura y los datos "
            "de las tablas de la base de datos seleccionada."
        )

        self.lbl_estado_respaldo = QLabel(
            "Listo para generar un respaldo."
        )

        self.lbl_estado_respaldo.setObjectName("estado")
        self.lbl_estado_respaldo.setWordWrap(True)

        self.barra_respaldo = QProgressBar()
        self.barra_respaldo.setRange(0, 100)
        self.barra_respaldo.setValue(0)
        self.barra_respaldo.setTextVisible(True)

        btn_crear = QPushButton("CREAR RESPALDO AHORA")
        btn_crear.setObjectName("exito")

        btn_crear.clicked.connect(
            self.crear_respaldo
        )

        btn_abrir = QPushButton("ABRIR CARPETA DE RESPALDOS")
        btn_abrir.setObjectName("secundario")

        btn_abrir.clicked.connect(
            lambda: self.abrir_carpeta(self.RUTA_RESPALDOS)
        )

        tarjeta_layout.addWidget(self.lbl_estado_respaldo)
        tarjeta_layout.addWidget(self.barra_respaldo)
        tarjeta_layout.addWidget(btn_crear)
        tarjeta_layout.addWidget(btn_abrir)

        layout.addWidget(tarjeta)

        tarjeta_historial, historial_layout = self.crear_tarjeta(
            "Historial de respaldos",
            "Selecciona un respaldo para restaurarlo o eliminarlo."
        )

        self.tabla_respaldos = QTableWidget()
        self.tabla_respaldos.setColumnCount(3)

        self.tabla_respaldos.setHorizontalHeaderLabels([
            "Fecha",
            "Archivo",
            "Tamaño"
        ])

        self.tabla_respaldos.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabla_respaldos.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabla_respaldos.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.tabla_respaldos.setAlternatingRowColors(True)
        self.tabla_respaldos.verticalHeader().setVisible(False)

        self.tabla_respaldos.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )

        self.tabla_respaldos.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )

        self.tabla_respaldos.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )

        self.tabla_respaldos.setMinimumHeight(230)

        fila_botones = QHBoxLayout()

        btn_actualizar = QPushButton("ACTUALIZAR LISTA")
        btn_actualizar.setObjectName("secundario")

        btn_actualizar.clicked.connect(
            self.actualizar_historial_respaldos
        )

        btn_restaurar = QPushButton("RESTAURAR RESPALDO")
        btn_restaurar.setObjectName("principal")

        btn_restaurar.clicked.connect(
            self.restaurar_respaldo
        )

        btn_eliminar = QPushButton("ELIMINAR RESPALDO")
        btn_eliminar.setObjectName("peligro")

        btn_eliminar.clicked.connect(
            self.eliminar_respaldo
        )

        fila_botones.addWidget(btn_actualizar)
        fila_botones.addWidget(btn_restaurar)
        fila_botones.addWidget(btn_eliminar)

        historial_layout.addWidget(self.tabla_respaldos)
        historial_layout.addLayout(fila_botones)

        layout.addWidget(tarjeta_historial)
        layout.addStretch()

        return pagina

    # ======================================================
    # CARGAR VALORES
    # ======================================================

    def cargar_valores(self):

        self.spin_tolerancia.setValue(
            int(self.configuracion.get("tolerancia_retardo", 10))
        )

        self.spin_camara.setValue(
            int(self.configuracion.get("camara", 0))
        )

        resolucion = self.configuracion.get(
            "resolucion",
            "1280x720"
        )

        if resolucion not in self.RESOLUCIONES:
            resolucion = "1280x720"

        self.combo_resolucion.setCurrentText(resolucion)

    # ======================================================
    # PRUEBA DE CAMARA
    # ======================================================

    def probar_camara(self):

        numero = self.spin_camara.value()
        resolucion = self.combo_resolucion.currentText()

        ancho, alto = self.RESOLUCIONES[resolucion]

        camara = None

        self.btn_probar_camara.setEnabled(False)

        self.lbl_estado_camara.setText("Comprobando cámara...")

        self.lbl_detalle_camara.setText(
            "Intentando abrir el dispositivo seleccionado."
        )

        try:

            camara = cv2.VideoCapture(
                numero,
                cv2.CAP_DSHOW
            )

            if not camara.isOpened():

                self.lbl_estado_camara.setText(
                    "No se pudo abrir la cámara."
                )

                self.lbl_estado_camara.setObjectName("estadoError")

                self.lbl_estado_camara.style().unpolish(
                    self.lbl_estado_camara
                )

                self.lbl_estado_camara.style().polish(
                    self.lbl_estado_camara
                )

                QMessageBox.warning(
                    self,
                    "Cámara",
                    "No se pudo acceder a la cámara seleccionada.\n\n"
                    "Comprueba que esté conectada y que ninguna otra "
                    "aplicación la esté utilizando."
                )

                return

            camara.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
            camara.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)

            correcto, frame = camara.read()

            if not correcto or frame is None:

                self.lbl_estado_camara.setText(
                    "La cámara abrió, pero no entregó imagen."
                )

                QMessageBox.warning(
                    self,
                    "Cámara",
                    "El dispositivo abrió correctamente, pero no "
                    "se pudo obtener una imagen."
                )

                return

            ancho_real = frame.shape[1]
            alto_real = frame.shape[0]

            self.lbl_estado_camara.setText(
                "Cámara funcionando correctamente."
            )

            self.lbl_detalle_camara.setText(
                f"Dispositivo: {numero} | "
                f"Resolución solicitada: {resolucion} | "
                f"Resolución obtenida: {ancho_real}x{alto_real}"
            )

            self.lbl_estado_camara.setObjectName("estadoExito")

            self.lbl_estado_camara.style().unpolish(
                self.lbl_estado_camara
            )

            self.lbl_estado_camara.style().polish(
                self.lbl_estado_camara
            )

            QMessageBox.information(
                self,
                "Prueba de cámara",
                "La cámara funciona correctamente.\n\n"
                f"Resolución obtenida: {ancho_real}x{alto_real}"
            )

        except Exception as error:

            self.lbl_estado_camara.setText(
                "Error al comprobar la cámara."
            )

            QMessageBox.critical(
                self,
                "Error de cámara",
                str(error)
            )

        finally:

            if camara is not None:
                camara.release()

            self.btn_probar_camara.setEnabled(True)

    # ======================================================
    # CONEXION MYSQL
    # ======================================================

    def obtener_conexion_segura(self):

        conexion = obtener_conexion()

        if conexion is None:

            raise ConnectionError(
                "No se pudo establecer la conexión con MySQL."
            )

        return conexion

    def probar_conexion_mysql(self):

        conexion = None
        cursor = None

        self.btn_probar_mysql.setEnabled(False)

        self.lbl_estado_mysql.setText("Comprobando conexión...")

        try:

            conexion = self.obtener_conexion_segura()
            cursor = conexion.cursor()

            cursor.execute(
                "SELECT DATABASE(), @@hostname, VERSION()"
            )

            resultado = cursor.fetchone()

            if not resultado:

                raise RuntimeError(
                    "MySQL no devolvió información del servidor."
                )

            base_datos, servidor, version = resultado

            self.lbl_estado_mysql.setText(
                "Conexión establecida correctamente."
            )

            self.lbl_estado_mysql.setObjectName("estadoExito")

            self.lbl_servidor_mysql.setText(
                f"Servidor: {servidor}"
            )

            self.lbl_base_mysql.setText(
                f"Base de datos: {base_datos}"
            )

            self.lbl_version_mysql.setText(
                f"MySQL: {version}"
            )

            self.lbl_estado_mysql.style().unpolish(
                self.lbl_estado_mysql
            )

            self.lbl_estado_mysql.style().polish(
                self.lbl_estado_mysql
            )

            QMessageBox.information(
                self,
                "Conexión MySQL",
                "La conexión con la base de datos funciona correctamente."
            )

            self.consultar_tablas_bd()

        except Exception as error:

            self.lbl_estado_mysql.setText(
                "No se pudo conectar con MySQL."
            )

            self.lbl_estado_mysql.setObjectName("estadoError")

            self.lbl_estado_mysql.style().unpolish(
                self.lbl_estado_mysql
            )

            self.lbl_estado_mysql.style().polish(
                self.lbl_estado_mysql
            )

            QMessageBox.critical(
                self,
                "Error de conexión",
                str(error)
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexion is not None:
                conexion.close()

            self.btn_probar_mysql.setEnabled(True)

    def consultar_tablas_bd(self):

        conexion = None
        cursor = None

        try:

            conexion = self.obtener_conexion_segura()
            cursor = conexion.cursor()

            cursor.execute("SHOW TABLES")

            tablas = cursor.fetchall()

            self.tabla_bd.setRowCount(0)

            for fila, registro in enumerate(tablas):

                nombre_tabla = registro[0]

                cursor.execute(
                    f"SELECT COUNT(*) FROM `{nombre_tabla}`"
                )

                cantidad = cursor.fetchone()[0]

                self.tabla_bd.insertRow(fila)

                self.tabla_bd.setItem(
                    fila,
                    0,
                    QTableWidgetItem(str(nombre_tabla))
                )

                self.tabla_bd.setItem(
                    fila,
                    1,
                    QTableWidgetItem(str(cantidad))
                )

            if not tablas:

                self.tabla_bd.setRowCount(1)

                self.tabla_bd.setItem(
                    0,
                    0,
                    QTableWidgetItem("No se encontraron tablas.")
                )

                self.tabla_bd.setItem(
                    0,
                    1,
                    QTableWidgetItem("-")
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron consultar las tablas:\n{error}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexion is not None:
                conexion.close()

    # ======================================================
    # DIAGNOSTICO DEL SISTEMA
    # ======================================================

    def ejecutar_diagnostico(self):

        conexion = None
        cursor = None

        tablas_principales = [
            "tblMaestros",
            "tblMaterias",
            "tblHorarios",
            "tblClasesImpartidas",
            "tblFaltas"
        ]

        try:

            conexion = self.obtener_conexion_segura()
            cursor = conexion.cursor()

            cursor.execute("SHOW TABLES")

            existentes = {
                registro[0]
                for registro in cursor.fetchall()
            }

            lineas = []

            for tabla in tablas_principales:

                if tabla in existentes:

                    cursor.execute(
                        f"SELECT COUNT(*) FROM `{tabla}`"
                    )

                    cantidad = cursor.fetchone()[0]

                    lineas.append(
                        f"Correcto: {tabla} ({cantidad} registros)"
                    )

                else:

                    lineas.append(
                        f"No encontrada: {tabla}"
                    )

            self.lbl_diagnostico.setText(
                "\n".join(lineas)
            )

            QMessageBox.information(
                self,
                "Diagnóstico",
                "El diagnóstico de la base de datos terminó."
            )

        except Exception as error:

            self.lbl_diagnostico.setText(
                f"No se pudo completar el diagnóstico:\n{error}"
            )

            QMessageBox.critical(
                self,
                "Diagnóstico",
                str(error)
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexion is not None:
                conexion.close()

    # ======================================================
    # ABRIR CARPETAS
    # ======================================================

    def abrir_carpeta(self, ruta):

        try:

            ruta.mkdir(parents=True, exist_ok=True)

            correcto = QDesktopServices.openUrl(
                QUrl.fromLocalFile(str(ruta.resolve()))
            )

            if not correcto:

                QMessageBox.warning(
                    self,
                    "Carpeta",
                    "No se pudo abrir la ubicación solicitada."
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                str(error)
            )

    # ======================================================
    # CONVERSION DE VALORES SQL
    # ======================================================

    def valor_sql(self, valor):

        if valor is None:
            return "NULL"

        if isinstance(valor, bool):
            return "1" if valor else "0"

        if isinstance(valor, (int, float, Decimal)):
            return str(valor)

        if isinstance(valor, (datetime, date, time)):

            valor = valor.isoformat(sep=" ") if isinstance(
                valor, datetime
            ) else valor.isoformat()

        if isinstance(valor, bytes):
            return "0x" + valor.hex()

        texto = str(valor)

        hexadecimal = texto.encode(
            "utf-8"
        ).hex()

        return f"CONVERT(0x{hexadecimal} USING utf8mb4)"

    # ======================================================
    # CREAR RESPALDO
    # ======================================================

    def crear_respaldo(self):

        conexion = None
        cursor = None
        ruta_archivo = None

        self.barra_respaldo.setValue(0)

        self.lbl_estado_respaldo.setText(
            "Conectando con MySQL..."
        )

        try:

            conexion = self.obtener_conexion_segura()
            cursor = conexion.cursor()

            cursor.execute("SELECT DATABASE()")

            resultado = cursor.fetchone()

            if not resultado or not resultado[0]:

                raise RuntimeError(
                    "No se pudo identificar la base de datos."
                )

            nombre_bd = resultado[0]

            cursor.execute("SHOW TABLES")

            tablas = [
                registro[0]
                for registro in cursor.fetchall()
            ]

            if not tablas:

                raise RuntimeError(
                    "La base de datos no contiene tablas."
                )

            marca_tiempo = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            nombre_archivo = (
                f"ARKOS_RESPALDO_{marca_tiempo}.sql"
            )

            ruta_archivo = (
                self.RUTA_RESPALDOS / nombre_archivo
            )

            total = len(tablas)

            self.lbl_estado_respaldo.setText(
                f"Generando respaldo de {total} tablas..."
            )

            with open(
                ruta_archivo,
                "w",
                encoding="utf-8"
            ) as archivo:

                archivo.write(
                    "-- ==================================================\n"
                    "-- ARKOS CHECADOR - RESPALDO DE BASE DE DATOS\n"
                    f"-- Fecha: {datetime.now().isoformat(sep=' ')}\n"
                    f"-- Base de datos: {nombre_bd}\n"
                    "-- ==================================================\n\n"
                )

                archivo.write(
                    "SET FOREIGN_KEY_CHECKS=0;\n\n"
                )

                for indice, tabla in enumerate(tablas, start=1):

                    self.lbl_estado_respaldo.setText(
                        f"Respaldando tabla {indice} de {total}: {tabla}"
                    )

                    cursor.execute(
                        f"SHOW CREATE TABLE `{tabla}`"
                    )

                    estructura = cursor.fetchone()[1]

                    archivo.write(
                        f"\n-- Tabla: {tabla}\n"
                    )

                    archivo.write(
                        f"DROP TABLE IF EXISTS `{tabla}`;\n"
                    )

                    archivo.write(
                        estructura + ";\n\n"
                    )

                    cursor.execute(
                        f"SELECT * FROM `{tabla}`"
                    )

                    columnas = [
                        descripcion[0]
                        for descripcion in cursor.description
                    ]

                    nombres_columnas = ", ".join(
                        f"`{columna}`"
                        for columna in columnas
                    )

                    while True:

                        registros = cursor.fetchmany(500)

                        if not registros:
                            break

                        for registro in registros:

                            valores = ", ".join(
                                self.valor_sql(valor)
                                for valor in registro
                            )

                            archivo.write(
                                f"INSERT INTO `{tabla}` "
                                f"({nombres_columnas}) "
                                f"VALUES ({valores});\n"
                            )

                    archivo.write("\n")

                    progreso = int(
                        (indice / total) * 100
                    )

                    self.barra_respaldo.setValue(progreso)

                archivo.write(
                    "\nSET FOREIGN_KEY_CHECKS=1;\n"
                )

            self.lbl_estado_respaldo.setText(
                f"Respaldo creado correctamente: {nombre_archivo}"
            )

            self.barra_respaldo.setValue(100)

            self.actualizar_historial_respaldos()

            QMessageBox.information(
                self,
                "Respaldo completado",
                "El respaldo se creó correctamente.\n\n"
                f"Archivo: {nombre_archivo}\n\n"
                f"Ubicación:\n{ruta_archivo}"
            )

        except Exception as error:

            self.lbl_estado_respaldo.setText(
                f"No se pudo crear el respaldo: {error}"
            )

            self.barra_respaldo.setValue(0)

            if ruta_archivo is not None:

                try:

                    if ruta_archivo.exists():
                        ruta_archivo.unlink()

                except Exception:
                    pass

            QMessageBox.critical(
                self,
                "Error al crear respaldo",
                str(error)
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexion is not None:
                conexion.close()

    # ======================================================
    # HISTORIAL DE RESPALDOS
    # ======================================================

    def actualizar_historial_respaldos(self):

        self.RUTA_RESPALDOS.mkdir(
            parents=True,
            exist_ok=True
        )

        archivos = sorted(
            self.RUTA_RESPALDOS.glob("*.sql"),
            key=lambda archivo: archivo.stat().st_mtime,
            reverse=True
        )

        self.tabla_respaldos.setRowCount(0)

        for fila, archivo in enumerate(archivos):

            fecha = datetime.fromtimestamp(
                archivo.stat().st_mtime
            ).strftime("%d/%m/%Y %H:%M:%S")

            tamano = archivo.stat().st_size

            if tamano >= 1024 * 1024:

                tamano_texto = f"{tamano / (1024 * 1024):.2f} MB"

            elif tamano >= 1024:

                tamano_texto = f"{tamano / 1024:.2f} KB"

            else:

                tamano_texto = f"{tamano} bytes"

            self.tabla_respaldos.insertRow(fila)

            item_fecha = QTableWidgetItem(fecha)
            item_archivo = QTableWidgetItem(archivo.name)
            item_tamano = QTableWidgetItem(tamano_texto)

            item_archivo.setData(
                Qt.UserRole,
                str(archivo.resolve())
            )

            self.tabla_respaldos.setItem(
                fila, 0, item_fecha
            )

            self.tabla_respaldos.setItem(
                fila, 1, item_archivo
            )

            self.tabla_respaldos.setItem(
                fila, 2, item_tamano
            )

        if not archivos:

            self.tabla_respaldos.setRowCount(1)

            self.tabla_respaldos.setItem(
                0,
                0,
                QTableWidgetItem("Sin respaldos")
            )

            self.tabla_respaldos.setItem(
                0,
                1,
                QTableWidgetItem("Todavía no hay archivos SQL")
            )

            self.tabla_respaldos.setItem(
                0,
                2,
                QTableWidgetItem("-")
            )

    # ======================================================
    # OBTENER RESPALDO SELECCIONADO
    # ======================================================

    def obtener_respaldo_seleccionado(self):

        fila = self.tabla_respaldos.currentRow()

        if fila < 0:
            return None

        item = self.tabla_respaldos.item(fila, 1)

        if item is None:
            return None

        ruta = item.data(Qt.UserRole)

        if not ruta:
            return None

        archivo = Path(ruta)

        if not archivo.exists() or archivo.suffix.lower() != ".sql":
            return None

        return archivo

    # ======================================================
    # DIVIDIR SCRIPT SQL
    # ======================================================

    def dividir_script_sql(self, contenido):

        sentencias = []
        actual = []

        dentro_comilla = False
        dentro_comilla_doble = False
        dentro_backtick = False

        escape = False

        for caracter in contenido:

            if escape:

                actual.append(caracter)
                escape = False

                continue

            if caracter == "\\\\" and (
                dentro_comilla or dentro_comilla_doble
            ):

                actual.append(caracter)
                escape = True

                continue

            if caracter == "'" and not dentro_comilla_doble and not dentro_backtick:

                dentro_comilla = not dentro_comilla

            elif caracter == '"' and not dentro_comilla and not dentro_backtick:

                dentro_comilla_doble = not dentro_comilla_doble

            elif caracter == "`" and not dentro_comilla and not dentro_comilla_doble:

                dentro_backtick = not dentro_backtick

            if caracter == ";" and not (
                dentro_comilla
                or dentro_comilla_doble
                or dentro_backtick
            ):

                sentencia = "".join(actual).strip()

                if sentencia:
                    sentencias.append(sentencia)

                actual = []

            else:

                actual.append(caracter)

        ultima = "".join(actual).strip()

        if ultima:
            sentencias.append(ultima)

        return sentencias

    # ======================================================
    # RESTAURAR RESPALDO
    # ======================================================

    def restaurar_respaldo(self):

        archivo = self.obtener_respaldo_seleccionado()

        if archivo is None:

            QMessageBox.warning(
                self,
                "Restaurar respaldo",
                "Selecciona un archivo SQL válido de la lista."
            )

            return

        respuesta = QMessageBox.warning(
            self,
            "Confirmar restauración",
            "ATENCIÓN:\n\n"
            "Restaurar este respaldo reemplazará las tablas "
            "incluidas en el archivo y sus datos actuales.\n\n"
            "Esta operación puede provocar pérdida de información "
            "registrada después de la fecha del respaldo.\n\n"
            "Se recomienda crear un respaldo nuevo antes de continuar.\n\n"
            "¿Deseas continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        conexion = None
        cursor = None

        try:

            self.lbl_estado_respaldo.setText(
                "Leyendo archivo de respaldo..."
            )

            contenido = archivo.read_text(
                encoding="utf-8"
            )

            sentencias = self.dividir_script_sql(
                contenido
            )

            if not sentencias:

                raise RuntimeError(
                    "El archivo de respaldo está vacío."
                )

            conexion = self.obtener_conexion_segura()
            cursor = conexion.cursor()

            total = len(sentencias)

            cursor.execute("SET FOREIGN_KEY_CHECKS=0")

            for indice, sentencia in enumerate(
                sentencias,
                start=1
            ):

                cursor.execute(sentencia)

                if indice % 20 == 0 or indice == total:

                    self.barra_respaldo.setValue(
                        int((indice / total) * 100)
                    )

            cursor.execute("SET FOREIGN_KEY_CHECKS=1")

            conexion.commit()

            self.lbl_estado_respaldo.setText(
                f"Respaldo restaurado: {archivo.name}"
            )

            self.barra_respaldo.setValue(100)

            self.consultar_tablas_bd()

            QMessageBox.information(
                self,
                "Restauración completada",
                "El respaldo se restauró correctamente."
            )

        except Exception as error:

            if conexion is not None:

                try:

                    conexion.rollback()
                    cursor.execute("SET FOREIGN_KEY_CHECKS=1")

                except Exception:
                    pass

            self.lbl_estado_respaldo.setText(
                f"Error al restaurar: {error}"
            )

            QMessageBox.critical(
                self,
                "Error de restauración",
                "No se pudo completar la restauración.\n\n"
                f"Detalle:\n{error}\n\n"
                "Comprueba la conexión y el archivo de respaldo."
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexion is not None:
                conexion.close()

            self.barra_respaldo.setValue(0)

    # ======================================================
    # ELIMINAR RESPALDO
    # ======================================================

    def eliminar_respaldo(self):

        archivo = self.obtener_respaldo_seleccionado()

        if archivo is None:

            QMessageBox.warning(
                self,
                "Eliminar respaldo",
                "Selecciona un respaldo válido."
            )

            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar respaldo",
            f"¿Deseas eliminar este archivo?\n\n{archivo.name}\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        try:

            archivo.unlink()

            self.actualizar_historial_respaldos()

            QMessageBox.information(
                self,
                "Respaldo eliminado",
                "El archivo se eliminó correctamente."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo eliminar el respaldo:\n{error}"
            )
