# ==========================================================
# ARKOS CHECADOR
# Archivo: Vistas/VisAsistencias.py
# Control y administración de asistencias
# ==========================================================

from datetime import date, datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFrame,
    QComboBox,
    QDateEdit,
    QLineEdit,
    QAbstractItemView,
    QDialog,
    QFormLayout
)

from PySide6.QtCore import Qt, QDate

from Servicios.ServicioAsistencias import (
    cargar_asistencias,
    actualizar_asistencia,
    eliminar_asistencia
)


class VisAsistencias(QWidget):

    def __init__(self):
        super().__init__()

        self.id_asistencia_seleccionada = None
        self.registros = []

        self.setWindowTitle("ARKOS - Asistencias")
        self.setMinimumSize(1050, 680)

        self.crear_interfaz()
        self.aplicar_estilos()
        self.cargar_datos()

    # ======================================================
    # INTERFAZ PRINCIPAL
    # ======================================================

    def crear_interfaz(self):

        principal = QVBoxLayout(self)
        principal.setContentsMargins(22, 18, 22, 20)
        principal.setSpacing(15)

        # ENCABEZADO

        encabezado = QVBoxLayout()
        encabezado.setSpacing(4)

        titulo = QLabel("Control de asistencias")
        titulo.setObjectName("titulo")

        subtitulo = QLabel(
            "Consulta, filtra y administra las asistencias "
            "y retardos de los maestros."
        )

        subtitulo.setObjectName("subtitulo")

        encabezado.addWidget(titulo)
        encabezado.addWidget(subtitulo)

        principal.addLayout(encabezado)

        # ==================================================
        # TARJETAS DE RESUMEN
        # ==================================================

        tarjetas = QHBoxLayout()
        tarjetas.setSpacing(14)

        self.tarjeta_asistencias = self.crear_tarjeta(
            "ASISTENCIAS",
            "0",
            "tarjetaAzul"
        )

        self.tarjeta_retardos = self.crear_tarjeta(
            "RETARDOS",
            "0",
            "tarjetaNaranja"
        )

        self.tarjeta_total = self.crear_tarjeta(
            "TOTAL DE REGISTROS",
            "0",
            "tarjetaOscura"
        )

        tarjetas.addWidget(self.tarjeta_asistencias)
        tarjetas.addWidget(self.tarjeta_retardos)
        tarjetas.addWidget(self.tarjeta_total)

        principal.addLayout(tarjetas)

        # ==================================================
        # FILTROS DE BÚSQUEDA
        # ==================================================

        marco_filtros = QFrame()
        marco_filtros.setObjectName("marco")

        filtros = QVBoxLayout(marco_filtros)
        filtros.setContentsMargins(18, 15, 18, 16)
        filtros.setSpacing(12)

        fila_titulo_filtros = QHBoxLayout()

        titulo_filtros = QLabel("Filtros de búsqueda")
        titulo_filtros.setObjectName("tituloSeccion")

        ayuda_filtros = QLabel(
            "Define el periodo y los criterios de consulta"
        )

        ayuda_filtros.setObjectName("ayuda")

        fila_titulo_filtros.addWidget(titulo_filtros)
        fila_titulo_filtros.addStretch()
        fila_titulo_filtros.addWidget(ayuda_filtros)

        filtros.addLayout(fila_titulo_filtros)

        rejilla = QGridLayout()
        rejilla.setHorizontalSpacing(12)
        rejilla.setVerticalSpacing(6)

        lbl_desde = QLabel("FECHA INICIAL")
        lbl_hasta = QLabel("FECHA FINAL")
        lbl_estado = QLabel("ESTADO")
        lbl_buscar = QLabel("BUSCAR MAESTRO O MATERIA")

        for etiqueta in (
            lbl_desde,
            lbl_hasta,
            lbl_estado,
            lbl_buscar
        ):

            etiqueta.setObjectName("etiquetaFiltro")

        # FECHA INICIAL

        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDisplayFormat("dd/MM/yyyy")

        self.fecha_inicio.setDate(
            QDate.currentDate().addMonths(-1)
        )

        self.fecha_inicio.setMinimumWidth(135)
        self.fecha_inicio.setFixedHeight(40)

        # FECHA FINAL

        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDisplayFormat("dd/MM/yyyy")

        self.fecha_fin.setDate(
            QDate.currentDate()
        )

        self.fecha_fin.setMinimumWidth(135)
        self.fecha_fin.setFixedHeight(40)

        # ESTADO

        self.combo_estado = QComboBox()

        self.combo_estado.addItems([
            "TODOS",
            "ASISTENCIA",
            "RETARDO"
        ])

        self.combo_estado.setMinimumWidth(145)
        self.combo_estado.setFixedHeight(40)

        # BUSCADOR

        self.buscar_texto = QLineEdit()

        self.buscar_texto.setPlaceholderText(
            "Nombre del maestro, materia o carrera..."
        )

        self.buscar_texto.setClearButtonEnabled(True)
        self.buscar_texto.setMinimumWidth(190)
        self.buscar_texto.setFixedHeight(40)

        self.buscar_texto.returnPressed.connect(
            self.aplicar_filtros
        )

        # DISTRIBUCIÓN

        rejilla.addWidget(lbl_desde, 0, 0)
        rejilla.addWidget(lbl_hasta, 0, 1)
        rejilla.addWidget(lbl_estado, 0, 2)
        rejilla.addWidget(lbl_buscar, 0, 3)

        rejilla.addWidget(self.fecha_inicio, 1, 0)
        rejilla.addWidget(self.fecha_fin, 1, 1)
        rejilla.addWidget(self.combo_estado, 1, 2)
        rejilla.addWidget(self.buscar_texto, 1, 3)

        rejilla.setColumnStretch(0, 1)
        rejilla.setColumnStretch(1, 1)
        rejilla.setColumnStretch(2, 1)
        rejilla.setColumnStretch(3, 2)

        filtros.addLayout(rejilla)

        # BOTONES DE FILTROS

        botones_filtro = QHBoxLayout()
        botones_filtro.addStretch()

        self.btn_limpiar = QPushButton("Limpiar filtros")
        self.btn_limpiar.setObjectName("btnSecundario")

        self.btn_limpiar.clicked.connect(
            self.limpiar_filtros
        )

        self.btn_filtrar = QPushButton("APLICAR FILTROS")
        self.btn_filtrar.setObjectName("btnPrimario")

        self.btn_filtrar.clicked.connect(
            self.aplicar_filtros
        )

        botones_filtro.addWidget(self.btn_limpiar)
        botones_filtro.addWidget(self.btn_filtrar)

        filtros.addLayout(botones_filtro)

        principal.addWidget(marco_filtros)

        # ==================================================
        # TABLA DE ASISTENCIAS
        # ==================================================

        marco_tabla = QFrame()
        marco_tabla.setObjectName("marco")

        layout_tabla = QVBoxLayout(marco_tabla)
        layout_tabla.setContentsMargins(18, 15, 18, 15)
        layout_tabla.setSpacing(12)

        fila_titulo = QHBoxLayout()

        titulo_tabla = QLabel("Registros de asistencia")
        titulo_tabla.setObjectName("tituloSeccion")

        self.lbl_resultados = QLabel("0 registros")
        self.lbl_resultados.setObjectName("contador")

        fila_titulo.addWidget(titulo_tabla)
        fila_titulo.addStretch()
        fila_titulo.addWidget(self.lbl_resultados)

        layout_tabla.addLayout(fila_titulo)

        # TABLA

        self.tabla = QTableWidget()
        self.tabla.setObjectName("tablaAsistencias")

        self.tabla.setColumnCount(9)

        self.tabla.setHorizontalHeaderLabels([
            "ID",
            "Maestro",
            "Materia",
            "Carrera",
            "Fecha",
            "Horario",
            "Hora de asistencia",
            "Estado",
            "Observaciones"
        ])

        # CONFIGURACIÓN DE SELECCIÓN

        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tabla.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.tabla.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.tabla.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus
        )

        self.tabla.setShowGrid(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setWordWrap(False)
        self.tabla.setSortingEnabled(False)
        self.tabla.setMouseTracking(False)

        self.tabla.verticalHeader().setVisible(False)

        self.tabla.verticalHeader().setDefaultSectionSize(42)

        self.tabla.horizontalHeader().setMinimumHeight(42)

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            8,
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla.setMinimumHeight(250)

        # EVENTOS DE SELECCIÓN

        self.tabla.cellClicked.connect(
            self.seleccionar_fila
        )

        self.tabla.itemSelectionChanged.connect(
            self.seleccionar_registro
        )

        self.tabla.currentCellChanged.connect(
            lambda fila, columna, fila_anterior, columna_anterior:
            self.seleccionar_fila(fila, columna)
            if fila >= 0 else None
        )

        layout_tabla.addWidget(self.tabla, 1)

        # ==================================================
        # BOTONES DE ACCIONES
        # ==================================================

        botones = QHBoxLayout()

        self.btn_actualizar = QPushButton(
            "Modificar registro"
        )

        self.btn_actualizar.setObjectName("btnPrimario")
        self.btn_actualizar.setEnabled(False)

        self.btn_actualizar.clicked.connect(
            self.modificar_asistencia
        )

        self.btn_eliminar = QPushButton(
            "Eliminar registro"
        )

        self.btn_eliminar.setObjectName("btnPeligro")
        self.btn_eliminar.setEnabled(False)

        self.btn_eliminar.clicked.connect(
            self.eliminar_registro
        )

        self.btn_recargar = QPushButton(
            "Actualizar lista"
        )

        self.btn_recargar.setObjectName("btnSecundario")

        self.btn_recargar.clicked.connect(
            self.cargar_datos
        )

        botones.addWidget(self.btn_actualizar)
        botones.addWidget(self.btn_eliminar)
        botones.addStretch()
        botones.addWidget(self.btn_recargar)

        layout_tabla.addLayout(botones)

        principal.addWidget(marco_tabla, 1)

    # ======================================================
    # TARJETAS DE RESUMEN
    # ======================================================

    def crear_tarjeta(self, titulo, valor, estilo):

        tarjeta = QFrame()
        tarjeta.setObjectName(estilo)

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(5)

        etiqueta = QLabel(titulo)
        etiqueta.setObjectName("tarjetaTitulo")

        numero = QLabel(valor)
        numero.setObjectName("tarjetaNumero")

        layout.addWidget(etiqueta)
        layout.addWidget(numero)

        tarjeta.valor = numero

        return tarjeta

    # ======================================================
    # CARGAR DATOS
    # ======================================================

    def cargar_datos(self):

        try:

            inicio = self.fecha_inicio.date().toString(
                "yyyy-MM-dd"
            )

            fin = self.fecha_fin.date().toString(
                "yyyy-MM-dd"
            )

            if inicio > fin:

                QMessageBox.warning(
                    self,
                    "Fechas incorrectas",
                    "La fecha inicial no puede ser posterior "
                    "a la fecha final."
                )

                return

            self.registros = cargar_asistencias(
                inicio,
                fin
            ) or []

            self.mostrar_registros(self.registros)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No fue posible cargar las asistencias:\n{error}"
            )

    # ======================================================
    # MOSTRAR REGISTROS
    # ======================================================

    def mostrar_registros(self, registros):

        self.tabla.setSortingEnabled(False)
        self.tabla.clearSelection()
        self.tabla.setCurrentCell(-1, -1)
        self.tabla.setRowCount(0)

        asistencias = 0
        retardos = 0

        for registro in registros:

            estado = str(
                registro.get("estado", "") or ""
            ).upper()

            if estado == "ASISTENCIA":
                asistencias += 1

            elif estado == "RETARDO":
                retardos += 1

            fila = self.tabla.rowCount()

            self.tabla.insertRow(fila)

            nombre = (
                f"{registro.get('nombre', '')} "
                f"{registro.get('apellido', '')}"
            ).strip()

            fecha = self.formatear_fecha(
                registro.get("fecha")
            )

            hora_inicio = self.formatear_hora(
                registro.get("hora_inicio")
            )

            hora_fin = self.formatear_hora(
                registro.get("hora_fin")
            )

            hora_asistencia = self.formatear_fecha_hora(
                registro.get("hora_asistencia")
            )

            horario = f"{hora_inicio} - {hora_fin}"

            valores = [
                registro.get("id_clase", ""),
                nombre,
                registro.get("materia", ""),
                registro.get("carrera", ""),
                fecha,
                horario,
                hora_asistencia,
                estado,
                registro.get("observaciones") or ""
            ]

            for columna, valor in enumerate(valores):

                item = QTableWidgetItem(str(valor))

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter
                )

                if columna in (0, 3, 4, 5, 6, 7):

                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                # Todas las celdas son seleccionables.

                item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled |
                    Qt.ItemFlag.ItemIsSelectable
                )

                if columna == 0:

                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        registro.get("id_clase")
                    )

                if columna == 7:

                    if estado == "ASISTENCIA":

                        item.setForeground(
                            Qt.GlobalColor.darkGreen
                        )

                    elif estado == "RETARDO":

                        item.setForeground(
                            Qt.GlobalColor.darkYellow
                        )

                self.tabla.setItem(
                    fila,
                    columna,
                    item
                )

        self.tarjeta_asistencias.valor.setText(
            str(asistencias)
        )

        self.tarjeta_retardos.valor.setText(
            str(retardos)
        )

        self.tarjeta_total.valor.setText(
            str(len(registros))
        )

        self.lbl_resultados.setText(
            f"{len(registros)} registros"
        )

        self.id_asistencia_seleccionada = None

        self.btn_actualizar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        self.tabla.clearSelection()

    # ======================================================
    # APLICAR FILTROS
    # ======================================================

    def aplicar_filtros(self):

        inicio = self.fecha_inicio.date().toString(
            "yyyy-MM-dd"
        )

        fin = self.fecha_fin.date().toString(
            "yyyy-MM-dd"
        )

        if inicio > fin:

            QMessageBox.warning(
                self,
                "Fechas incorrectas",
                "La fecha inicial no puede ser posterior "
                "a la fecha final."
            )

            return

        try:

            registros = cargar_asistencias(
                inicio,
                fin
            ) or []

            estado = self.combo_estado.currentText().strip().upper()

            texto = self.buscar_texto.text().strip().casefold()

            # FILTRAR POR ESTADO

            if estado != "TODOS":

                registros = [
                    registro
                    for registro in registros
                    if str(
                        registro.get("estado", "")
                    ).upper() == estado
                ]

            # FILTRAR POR TEXTO

            if texto:

                filtrados = []

                for registro in registros:

                    contenido = " ".join([
                        str(registro.get("nombre", "") or ""),
                        str(registro.get("apellido", "") or ""),
                        str(registro.get("materia", "") or ""),
                        str(registro.get("carrera", "") or ""),
                        str(registro.get("id_clase", "") or "")
                    ]).casefold()

                    if texto in contenido:

                        filtrados.append(registro)

                registros = filtrados

            self.registros = registros

            self.mostrar_registros(registros)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error en la búsqueda",
                f"No fue posible aplicar los filtros:\n{error}"
            )

    # ======================================================
    # LIMPIAR FILTROS
    # ======================================================

    def limpiar_filtros(self):

        self.fecha_inicio.setDate(
            QDate.currentDate().addMonths(-1)
        )

        self.fecha_fin.setDate(
            QDate.currentDate()
        )

        self.combo_estado.setCurrentIndex(0)

        self.buscar_texto.clear()

        self.cargar_datos()

    # ======================================================
    # SELECCIONAR FILA
    # ======================================================

    def seleccionar_fila(self, fila, columna=0):

        if fila < 0 or fila >= self.tabla.rowCount():

            self.id_asistencia_seleccionada = None

            self.btn_actualizar.setEnabled(False)
            self.btn_eliminar.setEnabled(False)

            return

        self.tabla.selectRow(fila)

        self.seleccionar_registro()

    # ======================================================
    # OBTENER REGISTRO SELECCIONADO
    # ======================================================

    def seleccionar_registro(self):

        fila = self.tabla.currentRow()

        if fila < 0:

            filas = self.tabla.selectionModel().selectedRows()

            if filas:

                fila = filas[0].row()

        if fila < 0:

            self.id_asistencia_seleccionada = None

            self.btn_actualizar.setEnabled(False)
            self.btn_eliminar.setEnabled(False)

            return

        item = self.tabla.item(fila, 0)

        if item is None:

            self.id_asistencia_seleccionada = None

        else:

            self.id_asistencia_seleccionada = item.data(
                Qt.ItemDataRole.UserRole
            )

            if self.id_asistencia_seleccionada is None:

                self.id_asistencia_seleccionada = item.text()

        seleccionado = (
            self.id_asistencia_seleccionada is not None
        )

        self.btn_actualizar.setEnabled(seleccionado)
        self.btn_eliminar.setEnabled(seleccionado)

    # ======================================================
    # MODIFICAR ASISTENCIA
    # ======================================================

    def modificar_asistencia(self):

        if self.id_asistencia_seleccionada is None:

            QMessageBox.warning(
                self,
                "Selecciona un registro",
                "Selecciona una asistencia de la tabla."
            )

            return

        registro = next(
            (
                r for r in self.registros
                if str(r.get("id_clase")) ==
                str(self.id_asistencia_seleccionada)
            ),
            None
        )

        if not registro:

            QMessageBox.warning(
                self,
                "Registro no encontrado",
                "No fue posible encontrar el registro seleccionado."
            )

            return

        dialogo = QDialog(self)

        dialogo.setWindowTitle("Modificar asistencia")
        dialogo.setMinimumWidth(440)

        layout = QVBoxLayout(dialogo)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(15)

        titulo = QLabel("Modificar registro de asistencia")
        titulo.setObjectName("tituloDialogo")

        descripcion = QLabel(
            "Actualiza el estado, la hora y las observaciones."
        )

        descripcion.setObjectName("subtitulo")
        descripcion.setWordWrap(True)

        layout.addWidget(titulo)
        layout.addWidget(descripcion)

        formulario = QFormLayout()
        formulario.setSpacing(12)

        combo_estado = QComboBox()

        combo_estado.addItems([
            "ASISTENCIA",
            "RETARDO"
        ])

        combo_estado.setCurrentText(
            registro.get("estado", "ASISTENCIA")
        )

        hora = QLineEdit()
        hora.setPlaceholderText("HH:MM:SS")

        valor_hora = registro.get("hora_asistencia")

        if valor_hora:

            hora.setText(
                valor_hora.strftime("%H:%M:%S")
                if hasattr(valor_hora, "strftime")
                else str(valor_hora).split(" ")[-1]
            )

        observaciones = QLineEdit()

        observaciones.setPlaceholderText(
            "Observaciones del registro"
        )

        observaciones.setText(
            registro.get("observaciones") or ""
        )

        formulario.addRow(
            "Estado:",
            combo_estado
        )

        formulario.addRow(
            "Hora de asistencia:",
            hora
        )

        formulario.addRow(
            "Observaciones:",
            observaciones
        )

        layout.addLayout(formulario)

        botones = QHBoxLayout()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btnSecundario")

        btn_guardar = QPushButton("Guardar cambios")
        btn_guardar.setObjectName("btnPrimario")

        btn_guardar.clicked.connect(dialogo.accept)
        btn_cancelar.clicked.connect(dialogo.reject)

        botones.addWidget(btn_cancelar)
        botones.addWidget(btn_guardar)

        layout.addLayout(botones)

        if dialogo.exec() != QDialog.DialogCode.Accepted:

            return

        # VALIDAR HORA

        hora_texto = hora.text().strip()

        if hora_texto:

            try:

                hora_valida = datetime.strptime(
                    hora_texto,
                    "%H:%M:%S"
                ).time()

            except ValueError:

                QMessageBox.warning(
                    self,
                    "Hora incorrecta",
                    "Utiliza el formato HH:MM:SS."
                )

                return

        else:

            hora_valida = None

        # ACTUALIZAR EN BASE DE DATOS

        resultado = actualizar_asistencia(
            self.id_asistencia_seleccionada,
            combo_estado.currentText(),
            hora_valida,
            observaciones.text().strip() or None
        )

        if resultado:

            QMessageBox.information(
                self,
                "Actualización",
                "El registro se actualizó correctamente."
            )

            self.cargar_datos()

        else:

            QMessageBox.warning(
                self,
                "Error",
                "No fue posible actualizar el registro."
            )

    # ======================================================
    # ELIMINAR REGISTRO
    # ======================================================

    def eliminar_registro(self):

        if self.id_asistencia_seleccionada is None:

            QMessageBox.warning(
                self,
                "Selecciona un registro",
                "Selecciona una asistencia de la tabla."
            )

            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Estás seguro de eliminar este registro de asistencia?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:

            return

        resultado = eliminar_asistencia(
            self.id_asistencia_seleccionada
        )

        if resultado:

            QMessageBox.information(
                self,
                "Registro eliminado",
                "El registro se eliminó correctamente."
            )

            self.cargar_datos()

        else:

            QMessageBox.warning(
                self,
                "Error",
                "No fue posible eliminar el registro."
            )

    # ======================================================
    # FORMATO DE FECHAS
    # ======================================================

    def formatear_fecha(self, valor):

        if not valor:
            return ""

        if isinstance(valor, (datetime, date)):

            return valor.strftime("%d/%m/%Y")

        try:

            return datetime.fromisoformat(
                str(valor)
            ).strftime("%d/%m/%Y")

        except ValueError:

            return str(valor)

    # ======================================================
    # FORMATO DE HORAS
    # ======================================================

    def formatear_hora(self, valor):

        if not valor:
            return ""

        if hasattr(valor, "strftime"):

            return valor.strftime("%H:%M")

        return str(valor)[:5]

    # ======================================================
    # FORMATO DE FECHA Y HORA
    # ======================================================

    def formatear_fecha_hora(self, valor):

        if not valor:

            return "No registrada"

        if hasattr(valor, "strftime"):

            return valor.strftime("%d/%m/%Y %H:%M:%S")

        try:

            return datetime.fromisoformat(
                str(valor)
            ).strftime("%d/%m/%Y %H:%M:%S")

        except ValueError:

            return str(valor)

    # ======================================================
    # ESTILOS
    # ======================================================

    def aplicar_estilos(self):

        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI";
                font-size: 10pt;
                color: #243447;
                background: #F3F6FA;
            }

            QLabel#titulo {
                font-size: 23pt;
                font-weight: 800;
                color: #001F3F;
                background: transparent;
            }

            QLabel#subtitulo,
            QLabel#ayuda {
                color: #718096;
                font-size: 9pt;
                background: transparent;
            }

            QFrame#marco {
                background: #FFFFFF;
                border: 1px solid #DFE7F0;
                border-radius: 12px;
            }

            QLabel#tituloSeccion {
                font-size: 12pt;
                font-weight: 800;
                color: #001F3F;
                background: transparent;
            }

            QLabel#etiquetaFiltro {
                color: #52677D;
                font-size: 8pt;
                font-weight: 800;
                background: transparent;
            }

            QLabel#contador {
                color: #52677D;
                font-weight: 700;
                background: #EDF3F8;
                border-radius: 7px;
                padding: 7px 11px;
            }

            QFrame#tarjetaAzul,
            QFrame#tarjetaNaranja,
            QFrame#tarjetaOscura {
                border-radius: 11px;
                min-height: 86px;
            }

            QFrame#tarjetaAzul {
                background: #003B73;
            }

            QFrame#tarjetaNaranja {
                background: #F28C28;
            }

            QFrame#tarjetaOscura {
                background: #001F3F;
            }

            QLabel#tarjetaTitulo {
                color: #FFFFFF;
                font-size: 9pt;
                font-weight: 800;
                background: transparent;
            }

            QLabel#tarjetaNumero {
                color: #FFFFFF;
                font-size: 23pt;
                font-weight: 800;
                background: transparent;
            }

            QLineEdit,
            QComboBox,
            QDateEdit {
                min-height: 38px;
                padding: 0px 10px;
                border: 1px solid #CCD7E3;
                border-radius: 7px;
                background: #FFFFFF;
                color: #243447;
                selection-background-color: #D5E8F8;
                selection-color: #001F3F;
            }

            QLineEdit:hover,
            QComboBox:hover,
            QDateEdit:hover {
                border: 1px solid #9DB4CA;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QDateEdit:focus {
                border: 1px solid #1672B8;
                background: #FFFFFF;
            }

            QComboBox::drop-down,
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #E1E8F0;
                border-top-right-radius: 7px;
                border-bottom-right-radius: 7px;
                background: #F5F8FB;
            }

            QComboBox QAbstractItemView {
                background: #FFFFFF;
                color: #243447;
                border: 1px solid #CCD7E3;
                selection-background-color: #DCEBFA;
                selection-color: #001F3F;
                padding: 4px;
                outline: 0;
            }

            QCalendarWidget QWidget {
                background: #FFFFFF;
                color: #243447;
            }

            QCalendarWidget QToolButton {
                color: #FFFFFF;
                background: #003B73;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }

            QCalendarWidget QAbstractItemView {
                selection-background-color: #003B73;
                selection-color: #FFFFFF;
            }

            QTableWidget#tablaAsistencias {
                background: #FFFFFF;
                alternate-background-color: #F6F9FC;
                border: 1px solid #DFE7F0;
                border-radius: 8px;
                gridline-color: #EDF1F5;
                selection-background-color: #CFE4F7;
                selection-color: #092746;
                outline: none;
            }

            QTableWidget#tablaAsistencias::item {
                padding: 7px 8px;
                border: none;
            }

            QTableWidget#tablaAsistencias::item:selected {
                background: #CFE4F7;
                color: #092746;
            }

            QHeaderView::section {
                background: #092746;
                color: #FFFFFF;
                padding: 11px 8px;
                border: none;
                border-right: 1px solid #23496C;
                font-weight: 800;
            }

            QPushButton {
                min-height: 38px;
                padding: 0px 16px;
                border-radius: 7px;
                font-weight: 800;
                border: none;
            }

            QPushButton#btnPrimario {
                background: #07558C;
                color: #FFFFFF;
            }

            QPushButton#btnPrimario:hover {
                background: #0B6EAD;
            }

            QPushButton#btnSecundario {
                background: #E8EEF5;
                color: #244765;
                border: 1px solid #D5E0EA;
            }

            QPushButton#btnSecundario:hover {
                background: #DCE7F1;
            }

            QPushButton#btnPeligro {
                background: #B42318;
                color: #FFFFFF;
            }

            QPushButton#btnPeligro:hover {
                background: #941B13;
            }

            QPushButton:disabled {
                background: #E5EAF0;
                color: #9AA8B7;
            }
        """)