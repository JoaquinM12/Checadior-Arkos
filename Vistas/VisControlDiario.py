# ==========================================================
# ARKOS CHECADOR
# Archivo: Vistas/VisControlDiario.py
# Seguimiento diario de clases y asistencias
# ==========================================================

from datetime import datetime

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QDateEdit,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QAbstractItemView,
    QDialog,
    QFormLayout,
)

from Servicios.ServicioAsistencias import (
    cargar_control_diario,
    registrar_asistencia_manual as guardar_asistencia_manual,
    registrar_falta_manual as guardar_falta_manual,
)


CUATRIMESTRES_ROMANOS = {
    "PRIMERO": "I",
    "SEGUNDO": "II",
    "TERCERO": "III",
    "CUARTO": "IV",
    "QUINTO": "V",
    "SEXTO": "VI",
    "SÉPTIMO": "VII",
    "SEPTIMO": "VII",
    "OCTAVO": "VIII",
    "NOVENO": "IX",
}

DIAS = (
    "lunes", "martes", "miércoles", "jueves",
    "viernes", "sábado", "domingo"
)

MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre",
    "diciembre",
)


class VisControlDiario(QWidget):

    def __init__(self):
        super().__init__()
        self.registros = []
        self.crear_interfaz()

    def crear_interfaz(self):
        self.setStyleSheet("""
            QWidget {
                background: #F3F6FA;
                color: #243447;
                font-family: "Segoe UI";
            }
            QLabel { background: transparent; }
            QFrame#hero {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #092746, stop:1 #14598C);
                border-radius: 16px;
            }
            QLabel#heroEyebrow {
                color: #F7B267;
                font-size: 9pt;
                font-weight: 800;
                letter-spacing: 1px;
            }
            QLabel#heroTitle {
                color: #FFFFFF;
                font-size: 22pt;
                font-weight: 800;
            }
            QLabel#heroSubtitle {
                color: #C7D8E8;
                font-size: 10pt;
            }
            QLabel#heroBadge {
                color: #EAF4FD;
                background: #214E73;
                border: 1px solid #3A6485;
                border-radius: 9px;
                padding: 9px 13px;
                font-size: 8pt;
                font-weight: 800;
            }
            QFrame#panel {
                background: #FFFFFF;
                border: 1px solid #DFE7F0;
                border-radius: 13px;
            }
            QFrame#tarjetaResumen {
                background: #FFFFFF;
                border: 1px solid #DFE7F0;
                border-radius: 11px;
            }
            QLabel#valorResumen {
                color: #092746;
                font-size: 21pt;
                font-weight: 800;
            }
            QLabel#nombreResumen {
                color: #64788C;
                font-size: 9pt;
                font-weight: 700;
            }
            QLabel#fecha {
                color: #52677D;
                font-size: 9pt;
            }
            QDateEdit {
                min-height: 36px;
                padding: 0 10px;
                color: #243447;
                background: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
            }
            QSpinBox, QLineEdit {
                min-height: 32px;
                padding: 0 8px;
                color: #243447;
                background: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
            }
            QPushButton#actualizar, QPushButton#registrarManual {
                min-height: 38px;
                padding: 0 16px;
                color: #FFFFFF;
                background: #003B73;
                border: none;
                border-radius: 7px;
                font-weight: 700;
            }
            QPushButton#actualizar:hover { background: #07569B; }
            QPushButton#registrarManual { background: #C66A18; }
            QPushButton#registrarManual:hover { background: #A95510; }
            QPushButton#registrarManual:disabled {
                background: #E5EAF0;
                color: #9AA8B7;
            }
            QTableWidget {
                background: #FFFFFF;
                alternate-background-color: #F8FAFC;
                border: 1px solid #DFE7F0;
                border-radius: 9px;
                gridline-color: #EDF1F5;
                selection-background-color: #DBEAFE;
                selection-color: #001F3F;
            }
            QTableWidget::item { padding: 8px 9px; }
            QTableWidget::item:selected {
                background: #CFE4F7;
                color: #092746;
            }
            QHeaderView::section {
                color: #FFFFFF;
                background: #092746;
                padding: 11px 8px;
                border: none;
                font-weight: 800;
            }
        """)

        principal = QVBoxLayout(self)
        principal.setContentsMargins(25, 22, 25, 22)
        principal.setSpacing(16)

        hero = QFrame()
        hero.setObjectName("hero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(25, 20, 25, 20)
        hero_layout.setSpacing(16)

        textos_hero = QVBoxLayout()
        textos_hero.setSpacing(5)
        eyebrow = QLabel("ARKOS  /  SEGUIMIENTO DE ASISTENCIA")
        eyebrow.setObjectName("heroEyebrow")
        titulo = QLabel("Control diario")
        titulo.setObjectName("heroTitle")
        subtitulo = QLabel(
            "Consulta las clases programadas y registra asistencias manuales."
        )
        subtitulo.setObjectName("heroSubtitle")
        subtitulo.setWordWrap(True)
        textos_hero.addWidget(eyebrow)
        textos_hero.addWidget(titulo)
        textos_hero.addWidget(subtitulo)
        hero_layout.addLayout(textos_hero, 1)

        insignia = QLabel("CONTROL ACADÉMICO")
        insignia.setObjectName("heroBadge")
        insignia.setAlignment(Qt.AlignCenter)
        hero_layout.addWidget(insignia, 0, Qt.AlignVCenter)
        principal.addWidget(hero)

        resumen = QHBoxLayout()
        resumen.setSpacing(12)
        self.valor_clases = self.crear_tarjeta_resumen(
            resumen, "CLASES PROGRAMADAS"
        )
        self.valor_registradas = self.crear_tarjeta_resumen(
            resumen, "CON ASISTENCIA"
        )
        self.valor_incidencias = self.crear_tarjeta_resumen(
            resumen, "FALTAS"
        )
        self.valor_pendientes = self.crear_tarjeta_resumen(
            resumen, "PENDIENTES"
        )
        principal.addLayout(resumen)

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 15, 16, 16)
        panel_layout.setSpacing(12)

        controles = QHBoxLayout()
        etiqueta_fecha = QLabel("Fecha:")
        self.fecha = QDateEdit(QDate.currentDate())
        self.fecha.setCalendarPopup(True)
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        self.fecha.setFixedWidth(150)

        self.lbl_fecha = QLabel("")
        self.lbl_fecha.setObjectName("fecha")

        self.btn_actualizar = QPushButton("Actualizar lista")
        self.btn_actualizar.setObjectName("actualizar")
        self.btn_actualizar.setCursor(Qt.PointingHandCursor)
        self.btn_actualizar.clicked.connect(self.cargar_datos)
        self.fecha.dateChanged.connect(self.cargar_datos)

        controles.addWidget(etiqueta_fecha)
        controles.addWidget(self.fecha)
        controles.addWidget(self.lbl_fecha, 1)
        controles.addWidget(self.btn_actualizar)
        panel_layout.addLayout(controles)

        self.tabla = QTableWidget(0, 8)
        self.tabla.setHorizontalHeaderLabels((
            "Maestro", "Materia", "Carrera", "Cuatrimestre",
            "Horario", "Estado", "Hora de asistencia", "Motivo / suplente"
        ))
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(42)
        self.tabla.itemSelectionChanged.connect(
            self.actualizar_estado_boton_manual
        )
        encabezado = self.tabla.horizontalHeader()
        encabezado.setSectionResizeMode(QHeaderView.ResizeToContents)
        encabezado.setSectionResizeMode(0, QHeaderView.Stretch)
        encabezado.setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setMinimumHeight(300)
        panel_layout.addWidget(self.tabla, 1)

        pie_tabla = QHBoxLayout()
        self.lbl_resultados = QLabel("Selecciona una fecha para consultar.")
        self.lbl_resultados.setObjectName("fecha")
        pie_tabla.addWidget(self.lbl_resultados, 1)

        self.btn_registrar_manual = QPushButton(
            "Registrar asistencia manual"
        )
        self.btn_registrar_manual.setObjectName("registrarManual")
        self.btn_registrar_manual.setCursor(Qt.PointingHandCursor)
        self.btn_registrar_manual.setEnabled(False)
        self.btn_registrar_manual.clicked.connect(
            self.registrar_asistencia_seleccionada
        )
        pie_tabla.addWidget(self.btn_registrar_manual)
        panel_layout.addLayout(pie_tabla)

        principal.addWidget(panel, 1)

    @staticmethod
    def crear_tarjeta_resumen(layout, nombre):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaResumen")
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(16, 12, 16, 12)
        tarjeta_layout.setSpacing(3)

        valor = QLabel("0")
        valor.setObjectName("valorResumen")
        etiqueta = QLabel(nombre)
        etiqueta.setObjectName("nombreResumen")
        tarjeta_layout.addWidget(valor)
        tarjeta_layout.addWidget(etiqueta)
        layout.addWidget(tarjeta, 1)
        return valor

    @staticmethod
    def formatear_hora(valor):
        if valor is None:
            return "—"
        if hasattr(valor, "strftime"):
            return valor.strftime("%H:%M")
        return str(valor).split(" ")[-1][:5]

    @staticmethod
    def convertir_hora(valor):
        if isinstance(valor, datetime):
            return valor.time()
        if hasattr(valor, "hour") and hasattr(valor, "minute"):
            return valor

        texto = str(valor).strip().split(" ")[-1]
        for formato in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(texto, formato).time()
            except ValueError:
                continue
        raise ValueError("No se pudo leer la hora de inicio de la clase.")

    @staticmethod
    def convertir_cuatrimestre(valor):
        texto = str(valor or "").strip().upper()
        return CUATRIMESTRES_ROMANOS.get(texto, texto or "—")

    @staticmethod
    def extraer_minutos_retardo(observaciones):
        marcador = "Retardo manual: "
        texto = str(observaciones or "")
        if marcador not in texto:
            return None
        valor = texto.split(marcador, 1)[1].split(" ", 1)[0]
        try:
            return int(valor)
        except ValueError:
            return None

    def cargar_datos(self, *_):
        fecha = datetime.strptime(
            self.fecha.date().toString("yyyy-MM-dd"),
            "%Y-%m-%d"
        ).date()

        try:
            registros = cargar_control_diario(fecha)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Error al cargar el control diario",
                f"No fue posible consultar las clases del día:\n{error}"
            )
            return

        texto_fecha = (
            f"{DIAS[fecha.weekday()].capitalize()}, {fecha.day} de "
            f"{MESES[fecha.month - 1]} de {fecha.year}"
        )
        self.lbl_fecha.setText(texto_fecha)
        self.registros = registros
        self.tabla.clearSpans()
        self.tabla.clearSelection()
        self.tabla.setCurrentCell(-1, -1)
        self.tabla.setRowCount(len(registros) if registros else 1)

        if not registros:
            self.valor_clases.setText("0")
            self.valor_registradas.setText("0")
            self.valor_incidencias.setText("0")
            self.valor_pendientes.setText("0")
            elemento = QTableWidgetItem(
                "No hay clases programadas para esta fecha."
            )
            elemento.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(0, 0, elemento)
            self.tabla.setSpan(0, 0, 1, self.tabla.columnCount())
            self.lbl_resultados.setText("0 clases programadas")
            self.btn_registrar_manual.setEnabled(False)
            return

        con_asistencia = 0
        con_falta = 0

        for fila, registro in enumerate(registros):
            registrada = registro.get("asistencia_id") is not None
            hay_falta = registro.get("id_falta") is not None
            if registrada:
                con_asistencia += 1
            elif hay_falta:
                con_falta += 1

            if registrada:
                estado = registro.get("estado_asistencia") or "REGISTRADA"
                if estado == "RETARDO":
                    minutos = self.extraer_minutos_retardo(
                        registro.get("observaciones_asistencia")
                    )
                    if minutos is not None:
                        estado = f"RETARDO · {minutos} min"
                detalle = ""
            elif hay_falta:
                estado = registro.get("estado_falta") or "FALTA"
                detalle = registro.get("observaciones_falta") or ""
                suplente = registro.get("maestro_cubrio")
                if suplente:
                    detalle = f"{detalle} · Suplente: {suplente}"
            else:
                estado = "PENDIENTE"
                detalle = ""
            hora_asistencia = (
                self.formatear_hora(registro.get("hora_asistencia"))
                if registrada else "—"
            )
            valores = (
                registro.get("maestro", ""),
                registro.get("materia", ""),
                registro.get("carrera", ""),
                self.convertir_cuatrimestre(registro.get("cuatrimestre")),
                f"{self.formatear_hora(registro.get('hora_inicio'))} - "
                f"{self.formatear_hora(registro.get('hora_fin'))}",
                estado,
                hora_asistencia,
                detalle,
            )

            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor or "—"))
                if columna in (2, 3, 4, 5, 6):
                    item.setTextAlignment(Qt.AlignCenter)
                if columna == 5:
                    item.setForeground(QColor(
                        "#15803D" if registrada
                        else "#B42318" if hay_falta
                        else "#B45309"
                    ))
                if columna == 0:
                    item.setData(Qt.ItemDataRole.UserRole, fila)
                self.tabla.setItem(fila, columna, item)

        self.lbl_resultados.setText(
            f"{len(registros)} clases programadas · "
            f"{con_asistencia} con asistencia · "
            f"{con_falta} faltas · "
            f"{len(registros) - con_asistencia - con_falta} pendientes"
        )
        self.valor_clases.setText(str(len(registros)))
        self.valor_registradas.setText(str(con_asistencia))
        self.valor_incidencias.setText(str(con_falta))
        self.valor_pendientes.setText(
            str(len(registros) - con_asistencia - con_falta)
        )
        self.actualizar_estado_boton_manual()

    def actualizar_estado_boton_manual(self):
        fila = self.tabla.currentRow()
        item = self.tabla.item(fila, 0) if fila >= 0 else None
        indice = (
            item.data(Qt.ItemDataRole.UserRole)
            if item is not None else None
        )
        pendiente = (
            isinstance(indice, int)
            and 0 <= indice < len(self.registros)
            and self.registros[indice].get("asistencia_id") is None
            and self.registros[indice].get("id_falta") is None
        )
        self.btn_registrar_manual.setEnabled(pendiente)

    def registrar_asistencia_seleccionada(self):
        fila = self.tabla.currentRow()
        item = self.tabla.item(fila, 0) if fila >= 0 else None
        indice = (
            item.data(Qt.ItemDataRole.UserRole)
            if item is not None else None
        )

        if not isinstance(indice, int) or not 0 <= indice < len(self.registros):
            return

        registro = self.registros[indice]
        if (
            registro.get("asistencia_id") is not None
            or registro.get("id_falta") is not None
        ):
            QMessageBox.information(
                self,
                "Registro existente",
                "Esta clase ya tiene una asistencia o falta registrada."
            )
            return

        try:
            hora_inicio = self.convertir_hora(registro.get("hora_inicio"))
        except ValueError as error:
            QMessageBox.critical(self, "Horario no válido", str(error))
            return

        dialogo = QDialog(self)
        dialogo.setWindowTitle("Registrar asistencia manual")
        dialogo.setMinimumWidth(390)
        formulario = QFormLayout(dialogo)
        formulario.setContentsMargins(22, 20, 22, 18)
        formulario.setSpacing(12)

        detalle = QLabel(
            f"{registro.get('maestro', '')}\n"
            f"{registro.get('materia', '')} · "
            f"{registro.get('carrera', '')} · "
            f"{self.convertir_cuatrimestre(registro.get('cuatrimestre'))}"
        )
        detalle.setWordWrap(True)
        formulario.addRow(detalle)

        fecha_seleccionada = datetime.strptime(
            self.fecha.date().toString("yyyy-MM-dd"),
            "%Y-%m-%d"
        ).date()
        etiqueta_hora = QLabel(
            f"{hora_inicio.strftime('%H:%M')}  ·  hora de inicio de la clase"
        )
        formulario.addRow("Hora que se registrará:", etiqueta_hora)

        estado = QComboBox()
        estado.addItems(("ASISTENCIA", "RETARDO", "FALTA", "JUSTIFICADA"))
        formulario.addRow("Tipo de registro:", estado)

        fila_retardo = QWidget()
        layout_retardo = QHBoxLayout(fila_retardo)
        layout_retardo.setContentsMargins(0, 0, 0, 0)
        layout_retardo.addWidget(QLabel("Minutos de retardo:"))
        minutos_retardo = QSpinBox()
        minutos_retardo.setRange(1, 600)
        minutos_retardo.setSuffix(" min")
        layout_retardo.addWidget(minutos_retardo)
        fila_retardo.hide()
        formulario.addRow(fila_retardo)

        fila_falta = QWidget()
        layout_falta = QVBoxLayout(fila_falta)
        layout_falta.setContentsMargins(0, 0, 0, 0)
        layout_falta.setSpacing(7)

        motivo = QLineEdit()
        motivo.setMaxLength(500)
        motivo.setPlaceholderText("Escribe por qué faltó el maestro")
        layout_falta.addWidget(QLabel("Motivo de la falta:"))
        layout_falta.addWidget(motivo)

        hay_suplente = QCheckBox("La clase tuvo un maestro suplente")
        layout_falta.addWidget(hay_suplente)
        maestro_suplente = QLineEdit()
        maestro_suplente.setMaxLength(150)
        maestro_suplente.setPlaceholderText("Nombre del maestro suplente")
        maestro_suplente.hide()
        layout_falta.addWidget(maestro_suplente)
        hay_suplente.toggled.connect(maestro_suplente.setVisible)
        fila_falta.hide()
        formulario.addRow(fila_falta)

        def actualizar_campos(tipo):
            fila_retardo.setVisible(tipo == "RETARDO")
            fila_falta.setVisible(tipo in ("FALTA", "JUSTIFICADA"))

        estado.currentTextChanged.connect(actualizar_campos)

        botones = QHBoxLayout()
        botones.addStretch(1)
        cancelar = QPushButton("Cancelar")
        guardar = QPushButton("Registrar")
        guardar.setObjectName("actualizar")
        cancelar.clicked.connect(dialogo.reject)

        def validar_y_aceptar():
            if estado.currentText() in ("FALTA", "JUSTIFICADA"):
                if not motivo.text().strip():
                    QMessageBox.warning(
                        dialogo,
                        "Motivo requerido",
                        "Escribe la razón de la falta."
                    )
                    return
                if hay_suplente.isChecked() and not maestro_suplente.text().strip():
                    QMessageBox.warning(
                        dialogo,
                        "Suplente requerido",
                        "Escribe el nombre del maestro suplente."
                    )
                    return
            dialogo.accept()

        guardar.clicked.connect(validar_y_aceptar)
        botones.addWidget(cancelar)
        botones.addWidget(guardar)
        formulario.addRow(botones)

        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return

        fecha_hora = datetime.combine(fecha_seleccionada, hora_inicio)

        try:
            if estado.currentText() in ("ASISTENCIA", "RETARDO"):
                observaciones = "Asistencia registrada manualmente."
                if estado.currentText() == "RETARDO":
                    observaciones += (
                        f" Retardo manual: {minutos_retardo.value()} minutos."
                    )
                guardar_asistencia_manual(
                    registro["id_maestro"],
                    registro["id_horario"],
                    fecha_hora,
                    estado.currentText(),
                    observaciones
                )
            else:
                guardar_falta_manual(
                    registro["id_maestro"],
                    registro["id_horario"],
                    fecha_hora,
                    estado.currentText(),
                    motivo.text(),
                    maestro_suplente.text() if hay_suplente.isChecked() else None
                )
        except Exception as error:
            QMessageBox.critical(
                self,
                "No se pudo registrar el movimiento",
                str(error)
            )
            return

        QMessageBox.information(
            self,
            "Registro guardado",
            "La información de la clase se guardó correctamente."
        )
        self.cargar_datos()
