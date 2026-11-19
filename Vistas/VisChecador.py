# ==========================================================
# ARKOS CHECADOR
# Archivo: Vistas/VisChecador.py
# ==========================================================

import cv2
import numpy as np

from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox
)

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

from Controladores.ControlReconocimiento import reconocer_imagen

from Servicios.ServicioAntiSpoofing import evaluar_rostro
from Servicios.ServicioParpadeo import DetectorParpadeo

from Servicios.ServicioAlmacenamiento import buscar_maestro

from Servicios.ServicioClasesImpartidas import (
    obtener_clase_actual,
    buscar_registro_clase
)

from Vistas.VisRegistroClase import VisRegistroClase


class VisChecador(QWidget):

    # ==================================================
    # CONFIGURACION DE SEGURIDAD
    # ==================================================

    INTERVALO_RECONOCIMIENTO = 15

    CONFIANZA_DETECCION = 0.88

    TAMANO_MINIMO_ROSTRO = 110

    BRILLO_MINIMO = 55
    BRILLO_MAXIMO = 200

    NITIDEZ_MINIMA = 45

    CONFIRMACIONES_NECESARIAS = 3

    CONFIRMACIONES_ANTI_SPOOF = 3

    DETECCIONES_NECESARIAS = 4

    UMBRAL_ESTABILIDAD = 0.35

    TIEMPO_RESULTADO_FALLIDO = 2500

    # ==================================================
    # INICIALIZACION
    # ==================================================

    def __init__(self):

        super().__init__()

        self.camara = None
        self.contador_frames = 0

        self.validador_parpadeo = DetectorParpadeo()
        self.parpadeo_confirmado = False

        self.contador_detecciones = 0
        self.ultima_caja_detectada = None
        self.deteccion_confirmada = False

        self.ultimo_id_candidato = None
        self.confirmaciones = 0

        self.maestro_confirmado = None
        self.resultado_reconocimiento = None

        self.contador_rostro_real = 0
        self.ultimo_resultado_anti_spoof = None

        self.mostrar_resultado_fallido = False

        self.ventana_clase_abierta = False

        self.esperando_retiro_rostro = False

        self.fecha_hora_reconocimiento = None

        self.timer_resultado = QTimer(self)
        self.timer_resultado.setSingleShot(True)
        self.timer_resultado.timeout.connect(
            self.finalizar_intento_no_reconocido
        )

        # Cargar modelo YuNet

        ruta_proyecto = Path(__file__).resolve().parent.parent

        ruta_yunet = (
            ruta_proyecto
            / "Recursos"
            / "ModelosIA"
            / "yunet.onnx"
        )

        if not ruta_yunet.exists():

            raise FileNotFoundError(
                f"No se encontro el modelo YuNet: {ruta_yunet}"
            )

        self.detector_yunet = cv2.FaceDetectorYN.create(
            str(ruta_yunet),
            "",
            (640, 480),
            self.CONFIANZA_DETECCION,
            0.30,
            5000
        )

        self.crear_interfaz()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)

    # ==================================================
    # INTERFAZ
    # ==================================================

    def crear_interfaz(self):

        self.setWindowTitle("ARKOS | Checador facial")
        self.setMinimumSize(1050, 650)

        self.setStyleSheet("""
            QWidget {
                background-color: #F3F6FA;
                color: #172B4D;
                font-family: Segoe UI;
                font-size: 10pt;
            }

            /* Evita que las etiquetas hereden el fondo general.
               Esta regla elimina las franjas vacias que aparecian
               detras de los textos. */

            QLabel {
                background-color: transparent;
            }

            QFrame#encabezado {
                background-color: #001F3F;
                border-radius: 14px;
            }

            QFrame#panelCamara,
            QFrame#panelControl {
                background-color: #FFFFFF;
                border: 1px solid #DCE4EE;
                border-radius: 14px;
            }

            QLabel#tituloPrincipal {
                background-color: transparent;
                color: #FFFFFF;
                font-size: 21pt;
                font-weight: 700;
            }

            QLabel#subtitulo {
                background-color: transparent;
                color: #C8D8E8;
                font-size: 9pt;
            }

            QLabel#tituloPanel {
                background-color: transparent;
                color: #001F3F;
                font-size: 12pt;
                font-weight: 700;
            }

            QLabel#camara {
                background-color: #101820;
                color: #DCE6F1;
                border: 2px solid #243B53;
                border-radius: 10px;
                font-size: 13pt;
            }

            QLabel#estado {
                background-color: #EAF2FA;
                color: #003B73;
                border-radius: 8px;
                padding: 12px;
                font-size: 11pt;
                font-weight: 700;
            }

            QLabel#maestro {
                background-color: #F5F8FC;
                color: #001F3F;
                border: 1px solid #E0E8F0;
                border-radius: 8px;
                padding: 14px;
                font-size: 11pt;
                font-weight: 600;
            }

            QLabel#nota {
                background-color: transparent;
                color: #66788A;
                font-size: 9pt;
            }

            QPushButton {
                min-height: 44px;
                border: none;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 700;
            }

            QPushButton#btnIniciar {
                background-color: #003B73;
                color: white;
            }

            QPushButton#btnIniciar:hover {
                background-color: #075A9E;
            }

            QPushButton#btnDetener {
                background-color: #E9EEF4;
                color: #34495E;
                border: 1px solid #D3DDE7;
            }

            QPushButton#btnDetener:hover {
                background-color: #DCE5EE;
            }

            QPushButton:disabled {
                background-color: #DCE2E8;
                color: #8995A1;
            }
        """)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(22, 18, 22, 22)
        layout_principal.setSpacing(16)

        # ENCABEZADO

        encabezado = QFrame()
        encabezado.setObjectName("encabezado")

        encabezado_layout = QVBoxLayout(encabezado)
        encabezado_layout.setContentsMargins(22, 16, 22, 16)
        encabezado_layout.setSpacing(4)

        titulo = QLabel("ARKOS | CHECADOR FACIAL")
        titulo.setObjectName("tituloPrincipal")

        subtitulo = QLabel(
            "Sistema de identificación y registro de clases"
        )
        subtitulo.setObjectName("subtitulo")

        encabezado_layout.addWidget(titulo)
        encabezado_layout.addWidget(subtitulo)

        layout_principal.addWidget(encabezado)

        # CONTENIDO PRINCIPAL

        contenido = QHBoxLayout()
        contenido.setSpacing(16)

        # PANEL DE CAMARA

        panel_camara = QFrame()
        panel_camara.setObjectName("panelCamara")

        camara_layout = QVBoxLayout(panel_camara)
        camara_layout.setContentsMargins(16, 16, 16, 16)
        camara_layout.setSpacing(8)

        titulo_camara = QLabel("Vista de cámara")
        titulo_camara.setObjectName("tituloPanel")

        self.lbl_camara = QLabel("La cámara está detenida")
        self.lbl_camara.setObjectName("camara")
        self.lbl_camara.setAlignment(Qt.AlignCenter)
        self.lbl_camara.setMinimumSize(520, 380)
        self.lbl_camara.setScaledContents(False)

        nota_camara = QLabel(
            "Colócate frente a la cámara y mantén el rostro visible."
        )
        nota_camara.setObjectName("nota")
        nota_camara.setWordWrap(True)

        camara_layout.addWidget(titulo_camara)
        camara_layout.addWidget(self.lbl_camara, 1)
        camara_layout.addWidget(nota_camara)

        contenido.addWidget(panel_camara, 3)

        # PANEL DE IDENTIFICACION

        panel_control = QFrame()
        panel_control.setObjectName("panelControl")

        control_layout = QVBoxLayout(panel_control)
        control_layout.setContentsMargins(18, 18, 18, 18)
        control_layout.setSpacing(14)

        titulo_control = QLabel("Panel de identificación")
        titulo_control.setObjectName("tituloPanel")

        descripcion = QLabel("Estado del proceso")
        descripcion.setObjectName("nota")

        self.lbl_estado = QLabel("Esperando inicio de cámara...")
        self.lbl_estado.setObjectName("estado")
        self.lbl_estado.setAlignment(Qt.AlignCenter)
        self.lbl_estado.setWordWrap(True)
        self.lbl_estado.setMinimumHeight(76)

        etiqueta_maestro = QLabel("Maestro")
        etiqueta_maestro.setObjectName("nota")

        self.lbl_maestro = QLabel("Ningún maestro identificado")
        self.lbl_maestro.setObjectName("maestro")
        self.lbl_maestro.setAlignment(Qt.AlignCenter)
        self.lbl_maestro.setWordWrap(True)
        self.lbl_maestro.setMinimumHeight(105)

        separador = QLabel("INSTRUCCIONES")
        separador.setStyleSheet("""
            background-color: transparent;
            color: #003B73;
            font-weight: 700;
            font-size: 9pt;
        """)

        instrucciones = QLabel(
            "1. Inicia la cámara.\n"
            "2. Colócate frente a ella.\n"
            "3. Realiza la prueba de vida.\n"
            "4. Espera la confirmación de identidad."
        )
        instrucciones.setObjectName("nota")
        instrucciones.setWordWrap(True)

        self.btn_iniciar = QPushButton("INICIAR CÁMARA")
        self.btn_iniciar.setObjectName("btnIniciar")
        self.btn_iniciar.clicked.connect(self.iniciar_camara)

        self.btn_detener = QPushButton("DETENER CÁMARA")
        self.btn_detener.setObjectName("btnDetener")
        self.btn_detener.clicked.connect(self.detener_camara)
        self.btn_detener.setEnabled(False)

        control_layout.addWidget(titulo_control)
        control_layout.addWidget(descripcion)
        control_layout.addWidget(self.lbl_estado)
        control_layout.addWidget(etiqueta_maestro)
        control_layout.addWidget(self.lbl_maestro)
        control_layout.addSpacing(8)
        control_layout.addWidget(separador)
        control_layout.addWidget(instrucciones)
        control_layout.addStretch(1)
        control_layout.addWidget(self.btn_iniciar)
        control_layout.addWidget(self.btn_detener)

        contenido.addWidget(panel_control, 2)

        layout_principal.addLayout(contenido, 1)

    # ==================================================
    # REINICIAR ESTABILIDAD
    # ==================================================

    def reiniciar_deteccion(self):

        self.contador_detecciones = 0
        self.ultima_caja_detectada = None
        self.deteccion_confirmada = False

    # ==================================================
    # REINICIAR IDENTIFICACION
    # ==================================================

    def reiniciar_identificacion(self):

        self.ultimo_id_candidato = None
        self.confirmaciones = 0

        self.maestro_confirmado = None
        self.resultado_reconocimiento = None

        self.contador_rostro_real = 0
        self.ultimo_resultado_anti_spoof = None

        self.parpadeo_confirmado = False
        self.validador_parpadeo.reiniciar()

    # ==================================================
    # REINICIAR TODO EL PROCESO
    # ==================================================

    def reiniciar_proceso(self):

        self.reiniciar_deteccion()
        self.reiniciar_identificacion()

        self.contador_frames = 0

    # ==================================================
    # MOSTRAR MAESTRO NO RECONOCIDO
    # ==================================================

    def mostrar_maestro_no_reconocido(self, mensaje=None):

        if self.mostrar_resultado_fallido:
            return

        self.ultimo_id_candidato = None
        self.confirmaciones = 0

        self.maestro_confirmado = None
        self.resultado_reconocimiento = None

        self.contador_rostro_real = 0
        self.ultimo_resultado_anti_spoof = None

        self.mostrar_resultado_fallido = True

        self.lbl_estado.setText("IDENTIDAD NO CONFIRMADA")

        self.lbl_maestro.setText(
            mensaje or "MAESTRO NO RECONOCIDO"
        )

        print("[CHECADOR] Maestro no reconocido.")

        self.timer_resultado.start(
            self.TIEMPO_RESULTADO_FALLIDO
        )

    # ==================================================
    # FINALIZAR INTENTO FALLIDO
    # ==================================================

    def finalizar_intento_no_reconocido(self):

        if self.camara is None:

            self.mostrar_resultado_fallido = False
            return

        self.mostrar_resultado_fallido = False

        self.reiniciar_proceso()

        self.lbl_estado.setText("PRUEBA DE VIDA (PARPADEO)")

        self.lbl_maestro.setText(
            "Por favor, parpadee frente a la camara..."
        )

    # ==================================================
    # COMPARAR POSICION DE DETECCIONES
    # ==================================================

    def calcular_iou(self, caja1, caja2):

        x1, y1, w1, h1 = caja1
        x2, y2, w2, h2 = caja2

        izquierda = max(x1, x2)
        arriba = max(y1, y2)

        derecha = min(
            x1 + w1,
            x2 + w2
        )

        abajo = min(
            y1 + h1,
            y2 + h2
        )

        ancho_interseccion = max(
            0,
            derecha - izquierda
        )

        alto_interseccion = max(
            0,
            abajo - arriba
        )

        area_interseccion = (
            ancho_interseccion * alto_interseccion
        )

        area1 = w1 * h1
        area2 = w2 * h2

        area_union = (
            area1 + area2 - area_interseccion
        )

        if area_union <= 0:
            return 0

        return area_interseccion / area_union

    # ==================================================
    # CONFIRMAR ESTABILIDAD DEL ROSTRO
    # ==================================================

    def confirmar_deteccion(
        self,
        x,
        y,
        ancho,
        alto
    ):

        caja_actual = (
            x,
            y,
            ancho,
            alto
        )

        if self.ultima_caja_detectada is None:

            self.contador_detecciones = 1
            self.ultima_caja_detectada = caja_actual
            self.deteccion_confirmada = False

            return False

        similitud = self.calcular_iou(
            self.ultima_caja_detectada,
            caja_actual
        )

        if similitud >= self.UMBRAL_ESTABILIDAD:

            self.contador_detecciones += 1

        else:

            self.contador_detecciones = 1
            self.deteccion_confirmada = False

        self.ultima_caja_detectada = caja_actual

        if (
            self.contador_detecciones
            >= self.DETECCIONES_NECESARIAS
        ):

            self.deteccion_confirmada = True

        return self.deteccion_confirmada

    # ==================================================
    # INICIAR CAMARA
    # ==================================================

    def iniciar_camara(self):

        if self.camara is not None:
            return

        self.camara = cv2.VideoCapture(
            0,
            cv2.CAP_DSHOW
        )

        if not self.camara.isOpened():

            self.lbl_camara.setText(
                "No se pudo acceder a la camara"
            )

            self.lbl_estado.setText(
                "Error al iniciar la camara"
            )

            self.camara.release()
            self.camara = None

            return

        self.reiniciar_proceso()

        self.mostrar_resultado_fallido = False
        self.esperando_retiro_rostro = False

        self.timer_resultado.stop()

        self.lbl_estado.setText("Buscando rostro...")

        self.lbl_maestro.setText(
            "Esperando identificacion..."
        )

        self.timer.start(30)

        self.btn_iniciar.setEnabled(False)
        self.btn_detener.setEnabled(True)

    # ==================================================
    # FILTRO DE CALIDAD FACIAL
    # ==================================================

    def validar_calidad_rostro(
        self,
        frame,
        x,
        y,
        ancho,
        alto
    ):

        alto_frame, ancho_frame = frame.shape[:2]

        if (
            ancho < self.TAMANO_MINIMO_ROSTRO
            or alto < self.TAMANO_MINIMO_ROSTRO
        ):

            return False, "Acercate mas a la camara."

        x1 = max(0, x)
        y1 = max(0, y)

        x2 = min(
            ancho_frame,
            x + ancho
        )

        y2 = min(
            alto_frame,
            y + alto
        )

        if x2 <= x1 or y2 <= y1:

            return False, "Rostro fuera de los limites."

        rostro = frame[y1:y2, x1:x2]

        if rostro.size == 0:

            return False, "No se pudo analizar el rostro."

        gris = cv2.cvtColor(
            rostro,
            cv2.COLOR_BGR2GRAY
        )

        brillo = np.mean(gris)

        if brillo < self.BRILLO_MINIMO:

            return False, "Hay poca iluminacion."

        if brillo > self.BRILLO_MAXIMO:

            return False, "Hay demasiada iluminacion."

        nitidez = cv2.Laplacian(
            gris,
            cv2.CV_64F
        ).var()

        if nitidez < self.NITIDEZ_MINIMA:

            return False, "Rostro borroso. Mantente quieto."

        return True, "Calidad facial correcta."

    # ==================================================
    # PROCESAR ANTI-SPOOFING
    # ==================================================

    def procesar_anti_spoofing(
        self,
        frame,
        x,
        y,
        ancho,
        alto
    ):

        caja = (
            x,
            y,
            x + ancho,
            y + alto
        )

        resultado = evaluar_rostro(
            frame,
            caja
        )

        self.ultimo_resultado_anti_spoof = resultado

        if not resultado.get("correcto"):

            self.reiniciar_identificacion()

            self.lbl_estado.setText(
                "ERROR EN ANTI-SPOOFING"
            )

            self.lbl_maestro.setText(
                resultado.get(
                    "mensaje",
                    "No se pudo analizar el rostro."
                )
            )

            return False

        if not resultado.get("es_real"):

            self.reiniciar_identificacion()

            self.lbl_estado.setText(
                "VERIFICACION DE SEGURIDAD RECHAZADA"
            )

            self.lbl_maestro.setText(
                resultado.get(
                    "mensaje",
                    "No se pudo validar el rostro."
                )
            )

            return False

        self.contador_rostro_real += 1

        if (
            self.contador_rostro_real
            < self.CONFIRMACIONES_ANTI_SPOOF
        ):

            self.lbl_estado.setText(
                "Verificando autenticidad del rostro..."
            )

            self.lbl_maestro.setText(
                f"Comprobacion de seguridad "
                f"{self.contador_rostro_real}/"
                f"{self.CONFIRMACIONES_ANTI_SPOOF}"
            )

            return False

        self.lbl_estado.setText(
            "SEGURIDAD FACIAL VALIDADA"
        )

        return True

    # ==================================================
    # PROCESAR RECONOCIMIENTO
    # ==================================================

    def procesar_reconocimiento(self, frame_original):

        if self.mostrar_resultado_fallido:
            return

        if self.ventana_clase_abierta:
            return

        resultado = reconocer_imagen(
            frame_original
        )

        if not resultado.get("reconocido"):

            mensaje = resultado.get(
                "mensaje",
                "MAESTRO NO RECONOCIDO"
            )

            self.mostrar_maestro_no_reconocido(
                mensaje
            )

            return

        maestro_id = resultado.get("maestro_id")

        if not maestro_id:

            self.mostrar_maestro_no_reconocido(
                "MAESTRO NO RECONOCIDO"
            )

            return

        if maestro_id == self.ultimo_id_candidato:

            self.confirmaciones += 1

        else:

            self.ultimo_id_candidato = maestro_id
            self.confirmaciones = 1
            self.maestro_confirmado = None

        if (
            self.confirmaciones
            >= self.CONFIRMACIONES_NECESARIAS
        ):

            self.maestro_confirmado = resultado
            self.resultado_reconocimiento = resultado

            # Capturar la hora al confirmar la identidad.

            self.fecha_hora_reconocimiento = datetime.now()

            self.lbl_estado.setText(
                "MAESTRO IDENTIFICADO Y CONFIRMADO"
            )

            self.lbl_maestro.setText(
                f"{resultado.get('nombre', maestro_id)} | {maestro_id}"
            )

            print(
                "[CHECADOR] Maestro confirmado:",
                maestro_id
            )

            print(
                "[CHECADOR] Hora de reconocimiento:",
                self.fecha_hora_reconocimiento.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            self.abrir_registro_clase(
                maestro_id,
                resultado
            )

        else:

            self.lbl_estado.setText(
                "Verificando identidad..."
            )

            self.lbl_maestro.setText(
                f"Coincidencia {self.confirmaciones}/"
                f"{self.CONFIRMACIONES_NECESARIAS}"
            )

    # ==================================================
    # ABRIR REGISTRO DE CLASE
    # ==================================================

    def abrir_registro_clase(
        self,
        maestro_id,
        resultado_reconocimiento
    ):

        if self.ventana_clase_abierta:
            return

        self.ventana_clase_abierta = True

        # Detener el análisis para impedir otro reconocimiento.

        self.timer.stop()

        try:

            fecha_reconocimiento = (
                self.fecha_hora_reconocimiento
            )

            # BUSCAR DATOS DEL MAESTRO EN MYSQL

            maestro = buscar_maestro(maestro_id)

            if not maestro:

                raise ValueError(
                    "No se encontraron los datos del maestro en MySQL."
                )

            if not maestro.get("activo", True):

                raise ValueError(
                    "El maestro se encuentra inactivo."
                )

            nombre_completo = (
                f"{maestro.get('nombre', '').strip()} "
                f"{maestro.get('apellidos', '').strip()}"
            ).strip()

            maestro["nombre"] = nombre_completo

            # BUSCAR CLASE VIGENTE

            horario = obtener_clase_actual(
                maestro_id,
                fecha_reconocimiento
            )

            if not horario:

                mensaje = (
                    f"Maestro: {nombre_completo}\n\n"
                    "No tienes una clase programada en este momento."
                )

                QMessageBox.information(
                    self,
                    "Sin clase programada",
                    mensaje
                )

                return

            # VERIFICAR SI YA EXISTE LA ASISTENCIA

            registro_existente = buscar_registro_clase(
                maestro_id,
                horario.get("id"),
                fecha_reconocimiento
            )

            if registro_existente:

                QMessageBox.information(
                    self,
                    "Clase ya registrada",
                    "La asistencia y los temas de esta clase "
                    "ya fueron registrados anteriormente.\n\n"
                    "No es necesario volver a registrarlos."
                )

                return

            # ABRIR VENTANA DE REGISTRO

            ventana = VisRegistroClase(
                maestro=maestro,
                horario=horario,
                fecha_hora_reconocimiento=fecha_reconocimiento,
                parent=self
            )

            ventana.exec()

            if ventana.registro_guardado:

                self.lbl_estado.setText(
                    "CLASE REGISTRADA CORRECTAMENTE"
                )

                self.lbl_maestro.setText(
                    f"{nombre_completo} | ASISTENCIA GUARDADA"
                )

                print(
                    "[CHECADOR] Clase registrada correctamente:",
                    horario.get("id")
                )

            else:

                self.lbl_estado.setText(
                    "REGISTRO DE CLASE CANCELADO"
                )

                self.lbl_maestro.setText(
                    "Retira tu rostro para realizar otro intento."
                )

        except Exception as error:

            print(
                "[CHECADOR] Error al abrir registro:",
                error
            )

            QMessageBox.critical(
                self,
                "Error de registro",
                str(error)
            )

        finally:

            self.ventana_clase_abierta = False

            # Exigir que el maestro retire su rostro
            # antes de comenzar un nuevo reconocimiento.

            self.esperando_retiro_rostro = True

            if self.camara is not None:
                self.timer.start(30)

    # ==================================================
    # ACTUALIZAR CAMARA
    # ==================================================

    def actualizar_frame(self):

        if self.camara is None:
            return

        correcto, frame_original = self.camara.read()

        if not correcto:
            return

        frame = cv2.flip(
            frame_original,
            1
        )

        # PAUSA PARA RESULTADO NO RECONOCIDO

        if self.mostrar_resultado_fallido:

            self._mostrar_frame_en_interfaz(frame)
            return

        alto, ancho = frame.shape[:2]

        self.detector_yunet.setInputSize(
            (ancho, alto)
        )

        _, rostros = self.detector_yunet.detect(
            frame
        )

        if rostros is None:
            rostros = []

        cantidad = len(rostros)

        # ESPERAR A QUE EL MAESTRO RETIRE SU ROSTRO

        if self.esperando_retiro_rostro:

            if cantidad > 0:

                self.lbl_estado.setText(
                    "REGISTRO FINALIZADO"
                )

                self.lbl_maestro.setText(
                    "Retira tu rostro para continuar."
                )

                self._mostrar_frame_en_interfaz(frame)
                return

            else:

                self.esperando_retiro_rostro = False

                self.reiniciar_proceso()

                self.lbl_estado.setText(
                    "Buscando rostro..."
                )

                self.lbl_maestro.setText(
                    "Esperando identificacion..."
                )

        # NINGUN ROSTRO

        if cantidad == 0:

            self.reiniciar_proceso()

            self.lbl_estado.setText(
                "No se detectaron rostros."
            )

            self.lbl_maestro.setText(
                "Colocate frente a la camara."
            )

        # VARIOS ROSTROS

        elif cantidad > 1:

            self.reiniciar_proceso()

            self.lbl_estado.setText(
                "VARIAS PERSONAS DETECTADAS"
            )

            self.lbl_maestro.setText(
                "Debe permanecer una sola persona."
            )

            for rostro in rostros:

                x, y, w, h = map(
                    int,
                    rostro[:4]
                )

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "DETECCION RECHAZADA",
                    (x, max(y - 10, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2
                )

        # UN SOLO ROSTRO

        else:

            rostro = rostros[0]

            x, y, w, h = map(
                int,
                rostro[:4]
            )

            confianza_detector = float(
                rostro[14]
            )

            # VALIDAR CONFIANZA

            if (
                confianza_detector
                < self.CONFIANZA_DETECCION
            ):

                self.reiniciar_proceso()

                self.lbl_estado.setText(
                    "DETECCION FACIAL INSUFICIENTE"
                )

                self.lbl_maestro.setText(
                    "Coloca tu rostro correctamente."
                )

            else:

                # VALIDAR CALIDAD

                calidad_correcta, mensaje = (
                    self.validar_calidad_rostro(
                        frame,
                        x,
                        y,
                        w,
                        h
                    )
                )

                if not calidad_correcta:

                    self.reiniciar_proceso()

                    self.lbl_estado.setText(
                        "FILTRO DE CALIDAD"
                    )

                    self.lbl_maestro.setText(
                        mensaje
                    )

                else:

                    # CONFIRMAR ESTABILIDAD

                    deteccion_estable = (
                        self.confirmar_deteccion(
                            x,
                            y,
                            w,
                            h
                        )
                    )

                    if not deteccion_estable:

                        self.reiniciar_identificacion()

                        self.contador_frames = 0

                        self.lbl_estado.setText(
                            "COMPROBANDO DETECCION FACIAL"
                        )

                        self.lbl_maestro.setText(
                            f"Detecciones estables: "
                            f"{self.contador_detecciones}/"
                            f"{self.DETECCIONES_NECESARIAS}"
                        )

                    else:

                        self.contador_frames += 1

                        # 1. EVALUAR PARPADEO

                        if not self.parpadeo_confirmado:

                            self.parpadeo_confirmado = (
                                self.validador_parpadeo.evaluar_fotograma(
                                    frame
                                )
                            )

                            if not self.parpadeo_confirmado:

                                self.lbl_estado.setText(
                                    "PRUEBA DE VIDA (PARPADEO)"
                                )

                                self.lbl_maestro.setText(
                                    "Por favor, parpadee frente a la camara..."
                                )

                                color = (0, 165, 255)

                                cv2.rectangle(
                                    frame,
                                    (x, y),
                                    (x + w, y + h),
                                    color,
                                    3
                                )

                                cv2.putText(
                                    frame,
                                    "PARPADEE...",
                                    (x, max(y - 10, 25)),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6,
                                    color,
                                    2
                                )

                                self._mostrar_frame_en_interfaz(
                                    frame
                                )

                                return

                        # 2. EJECUTAR ANTI-SPOOFING

                        if (
                            self.contador_frames
                            % self.INTERVALO_RECONOCIMIENTO == 0
                        ):

                            seguridad_validada = (
                                self.procesar_anti_spoofing(
                                    frame,
                                    x,
                                    y,
                                    w,
                                    h
                                )
                            )

                            # 3. EJECUTAR RECONOCIMIENTO

                            if seguridad_validada:

                                self.procesar_reconocimiento(
                                    frame_original
                                )

                        # DIBUJAR RECUADRO

                        if not deteccion_estable:

                            color = (0, 165, 255)
                            texto = "CONFIRMANDO ROSTRO"

                        elif self.maestro_confirmado:

                            color = (0, 255, 0)
                            texto = "IDENTIDAD CONFIRMADA"

                        elif (
                            self.contador_rostro_real
                            >= self.CONFIRMACIONES_ANTI_SPOOF
                        ):

                            color = (0, 255, 255)
                            texto = "ROSTRO VALIDADO"

                        else:

                            color = (0, 165, 255)
                            texto = "VERIFICANDO SEGURIDAD"

                        cv2.rectangle(
                            frame,
                            (x, y),
                            (x + w, y + h),
                            color,
                            3
                        )

                        cv2.putText(
                            frame,
                            texto,
                            (x, max(y - 10, 25)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            color,
                            2
                        )

        self._mostrar_frame_en_interfaz(frame)

    # ==================================================
    # MOSTRAR IMAGEN EN INTERFAZ
    # ==================================================

    def _mostrar_frame_en_interfaz(self, frame):

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        alto, ancho, canales = frame_rgb.shape

        bytes_por_linea = canales * ancho

        imagen = QImage(
            frame_rgb.data,
            ancho,
            alto,
            bytes_por_linea,
            QImage.Format_RGB888
        ).copy()

        pixmap = QPixmap.fromImage(imagen)

        self.lbl_camara.setPixmap(
            pixmap.scaled(
                self.lbl_camara.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # ==================================================
    # DETENER CAMARA
    # ==================================================

    def detener_camara(self):

        self.timer.stop()
        self.timer_resultado.stop()

        self.mostrar_resultado_fallido = False
        self.esperando_retiro_rostro = False

        if self.camara is not None:

            self.camara.release()
            self.camara = None

        self.reiniciar_proceso()

        self.lbl_camara.setPixmap(
            QPixmap()
        )

        self.lbl_camara.setText(
            "La camara esta detenida"
        )

        self.lbl_estado.setText(
            "Esperando inicio de camara..."
        )

        self.lbl_maestro.setText(
            "Ningun maestro identificado"
        )

        self.btn_iniciar.setEnabled(True)
        self.btn_detener.setEnabled(False)

    # ==================================================
    # CERRAR APLICACION
    # ==================================================

    def closeEvent(self, event):

        self.detener_camara()

        event.accept()