
import cv2
import numpy as np

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

from Controladores.ControlReconocimiento import reconocer_imagen
from Servicios.ServicioAntiSpoofing import evaluar_rostro
from Servicios.ServicioParpadeo import DetectorParpadeo


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

    # Tiempo que se muestra el mensaje de identidad no reconocida.
    TIEMPO_RESULTADO_FALLIDO = 2500

    # ==================================================
    # INICIALIZACION
    # ==================================================

    def __init__(self):

        super().__init__()

        self.camara = None
        self.contador_frames = 0

        # Detector de parpadeo
        self.validador_parpadeo = DetectorParpadeo()
        self.parpadeo_confirmado = False

        # Estabilidad de deteccion
        self.contador_detecciones = 0
        self.ultima_caja_detectada = None
        self.deteccion_confirmada = False

        # Confirmacion de identidad
        self.ultimo_id_candidato = None
        self.confirmaciones = 0

        self.maestro_confirmado = None
        self.resultado_reconocimiento = None

        # Anti-spoofing
        self.contador_rostro_real = 0
        self.ultimo_resultado_anti_spoof = None

        # Estado para mostrar resultado fallido
        self.mostrar_resultado_fallido = False

        # Temporizador para regresar al inicio
        self.timer_resultado = QTimer(self)
        self.timer_resultado.setSingleShot(True)
        self.timer_resultado.timeout.connect(
            self.finalizar_intento_no_reconocido
        )

        # ==================================================
        # CARGAR MODELO YUNET
        # ==================================================

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

        # Temporizador principal de cámara
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)

    # ==================================================
    # INTERFAZ
    # ==================================================

    def crear_interfaz(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        titulo = QLabel("CHECADOR FACIAL ARKOS")
        titulo.setAlignment(Qt.AlignCenter)

        titulo.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #001F3F;
        """)

        self.lbl_camara = QLabel(
            "La camara esta detenida"
        )

        self.lbl_camara.setAlignment(Qt.AlignCenter)
        self.lbl_camara.setMinimumSize(640, 400)

        self.lbl_camara.setStyleSheet("""
            background-color: #1C1C1C;
            color: white;
            font-size: 20px;
            border-radius: 10px;
        """)

        self.lbl_estado = QLabel(
            "Esperando inicio de camara..."
        )

        self.lbl_estado.setAlignment(Qt.AlignCenter)

        self.lbl_estado.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #003B73;
            padding: 5px;
        """)

        self.lbl_maestro = QLabel(
            "Ningun maestro identificado"
        )

        self.lbl_maestro.setAlignment(Qt.AlignCenter)

        self.lbl_maestro.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #001F3F;
            padding: 10px;
        """)

        self.btn_iniciar = QPushButton(
            "INICIAR CAMARA"
        )

        self.btn_iniciar.setMinimumHeight(45)

        self.btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: #003B73;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #1677C8;
            }
        """)

        self.btn_iniciar.clicked.connect(
            self.iniciar_camara
        )

        self.btn_detener = QPushButton(
            "DETENER CAMARA"
        )

        self.btn_detener.setMinimumHeight(45)

        self.btn_detener.setStyleSheet("""
            QPushButton {
                background-color: #C0392B;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #E74C3C;
            }
        """)

        self.btn_detener.clicked.connect(
            self.detener_camara
        )

        botones = QHBoxLayout()
        botones.setSpacing(15)

        botones.addWidget(self.btn_iniciar)
        botones.addWidget(self.btn_detener)

        layout.addWidget(titulo)
        layout.addWidget(self.lbl_camara, 1)
        layout.addWidget(self.lbl_estado)
        layout.addWidget(self.lbl_maestro)
        layout.addLayout(botones)

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

        # Limpiar los datos de identificación.
        # No reiniciar todavía el detector de parpadeo.

        self.ultimo_id_candidato = None
        self.confirmaciones = 0

        self.maestro_confirmado = None
        self.resultado_reconocimiento = None

        self.contador_rostro_real = 0
        self.ultimo_resultado_anti_spoof = None

        # Bloquear temporalmente el procesamiento.
        self.mostrar_resultado_fallido = True

        self.lbl_estado.setText(
            "IDENTIDAD NO CONFIRMADA"
        )

        self.lbl_maestro.setText(
            mensaje or "MAESTRO NO RECONOCIDO"
        )

        print(
            "[CHECADOR] Maestro no reconocido. "
            "Mostrando resultado."
        )

        # Mostrar el mensaje durante 2.5 segundos.
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

        print(
            "[CHECADOR] Finalizando intento fallido. "
            "Preparando nuevo intento."
        )

        self.mostrar_resultado_fallido = False

        # Reiniciar todo, incluido el detector de parpadeo.
        self.reiniciar_proceso()

        self.lbl_estado.setText(
            "PRUEBA DE VIDA (PARPADEO)"
        )

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
        self.timer_resultado.stop()

        self.lbl_estado.setText(
            "Buscando rostro..."
        )

        self.lbl_maestro.setText(
            "Esperando identificacion..."
        )

        self.timer.start(30)

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

        # Evitar procesar más de una vez mientras se
        # muestra el mensaje de maestro no reconocido.

        if self.mostrar_resultado_fallido:
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

        maestro_id = resultado.get(
            "maestro_id"
        )

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

            self.lbl_estado.setText(
                "MAESTRO IDENTIFICADO Y CONFIRMADO"
            )

            self.lbl_maestro.setText(
                f"{resultado['nombre']} | {maestro_id}"
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

        # ==============================================
        # PAUSA PARA MOSTRAR RESULTADO NO RECONOCIDO
        # ==============================================

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

        # ==============================================
        # NINGUN ROSTRO
        # ==============================================

        if cantidad == 0:

            self.reiniciar_proceso()

            self.lbl_estado.setText(
                "No se detectaron rostros."
            )

            self.lbl_maestro.setText(
                "Colocate frente a la camara."
            )

        # ==============================================
        # VARIOS ROSTROS
        # ==============================================

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

        # ==============================================
        # UN SOLO ROSTRO
        # ==============================================

        else:

            rostro = rostros[0]

            x, y, w, h = map(
                int,
                rostro[:4]
            )

            confianza_detector = float(
                rostro[14]
            )

            # ==========================================
            # VALIDAR CONFIANZA
            # ==========================================

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

                # ======================================
                # VALIDAR CALIDAD
                # ======================================

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

                    # ==================================
                    # CONFIRMAR ESTABILIDAD
                    # ==================================

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

                        # ==================================
                        # 1. EVALUAR PARPADEO
                        # ==================================

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

                                texto = "PARPADEE..."

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

                                self._mostrar_frame_en_interfaz(
                                    frame
                                )

                                return

                        # ==================================
                        # 2. EJECUTAR ANTI-SPOOFING
                        # ==================================

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

                            # ==================================
                            # 3. EJECUTAR RECONOCIMIENTO
                            # ==================================

                            if seguridad_validada:

                                self.procesar_reconocimiento(
                                    frame_original
                                )

                        # ==================================
                        # DIBUJAR RECUADRO
                        # ==================================

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

        # ==============================================
        # MOSTRAR IMAGEN
        # ==============================================

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

        # Detener también el temporizador del resultado.
        self.timer_resultado.stop()

        self.mostrar_resultado_fallido = False

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

    # ==================================================
    # CERRAR APLICACION
    # ==================================================

    def closeEvent(self, event):

        self.detener_camara()

        event.accept()
