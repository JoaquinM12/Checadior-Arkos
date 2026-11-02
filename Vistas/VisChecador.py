
import cv2

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


class VisChecador(QWidget):

    INTERVALO_RECONOCIMIENTO = 30

    def __init__(self):
        super().__init__()

        self.camara = None
        self.contador_frames = 0

        self.resultado_reconocimiento = {
            "reconocido": False,
            "mensaje": "Esperando cámara..."
        }

        # Detector auxiliar para comprobar cuántos rostros hay.
        ruta_detector = (
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        self.detector_rostros = cv2.CascadeClassifier(
            ruta_detector
        )

        if self.detector_rostros.empty():
            raise RuntimeError(
                "No se pudo cargar el detector de rostros de OpenCV."
            )

        # Temporizador de cámara.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)

        self.crear_interfaz()

    # =================================================
    # INTERFAZ
    # =================================================

    def crear_interfaz(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        titulo = QLabel("CHECADOR FACIAL")

        titulo.setAlignment(Qt.AlignCenter)

        titulo.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #001F3F;
        """)

        self.lbl_camara = QLabel(
            "La cámara está detenida"
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
            "Esperando inicio de cámara..."
        )

        self.lbl_estado.setAlignment(Qt.AlignCenter)

        self.lbl_estado.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #003B73;
            padding: 5px;
        """)

        self.lbl_maestro = QLabel(
            "Ningún maestro identificado"
        )

        self.lbl_maestro.setAlignment(Qt.AlignCenter)

        self.lbl_maestro.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #001F3F;
            padding: 10px;
        """)

        # Botón iniciar.
        self.btn_iniciar = QPushButton(
            "INICIAR CÁMARA"
        )

        self.btn_iniciar.setMinimumHeight(45)
        self.btn_iniciar.setCursor(Qt.PointingHandCursor)

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

        # Botón detener.
        self.btn_detener = QPushButton(
            "DETENER CÁMARA"
        )

        self.btn_detener.setMinimumHeight(45)
        self.btn_detener.setCursor(Qt.PointingHandCursor)

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

    # =================================================
    # INICIAR CÁMARA
    # =================================================

    def iniciar_camara(self):

        if self.camara is not None:
            return

        self.camara = cv2.VideoCapture(
            0,
            cv2.CAP_DSHOW
        )

        if not self.camara.isOpened():

            self.lbl_camara.setText(
                "No se pudo acceder a la cámara"
            )

            self.lbl_estado.setText(
                "Error al iniciar la cámara"
            )

            self.camara.release()
            self.camara = None

            return

        self.contador_frames = (
            self.INTERVALO_RECONOCIMIENTO - 1
        )

        self.resultado_reconocimiento = {
            "reconocido": False,
            "mensaje": "Buscando rostro..."
        }

        self.lbl_estado.setText(
            "Buscando rostros..."
        )

        self.lbl_maestro.setText(
            "Esperando identificación..."
        )

        self.timer.start(30)

    # =================================================
    # ACTUALIZAR CÁMARA
    # =================================================

    def actualizar_frame(self):

        if self.camara is None:
            return

        correcto, frame_original = self.camara.read()

        if not correcto:
            return

        # Conservar imagen original para AuraFace.
        # La imagen mostrada se voltea como espejo.
        frame = cv2.flip(
            frame_original,
            1
        )

        gris = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # Detectar rostros.
        rostros = self.detector_rostros.detectMultiScale(
            gris,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        cantidad = len(rostros)

        # =============================================
        # SIN ROSTROS
        # =============================================

        if cantidad == 0:

            self.resultado_reconocimiento = {
                "reconocido": False,
                "mensaje": "No se detectaron rostros."
            }

            self.lbl_estado.setText(
                "No se detectaron rostros."
            )

            self.lbl_maestro.setText(
                "Acércate a la cámara."
            )

        # =============================================
        # VARIOS ROSTROS
        # =============================================

        elif cantidad > 1:

            self.resultado_reconocimiento = {
                "reconocido": False,
                "mensaje": "Hay varias personas frente a la cámara."
            }

            self.lbl_estado.setText(
                f"Se detectaron {cantidad} rostros."
            )

            self.lbl_maestro.setText(
                "Debe permanecer una sola persona."
            )

        # =============================================
        # UN SOLO ROSTRO
        # =============================================

        else:

            self.lbl_estado.setText(
                "Rostro detectado. Verificando identidad..."
            )

            self.contador_frames += 1

            # Ejecutar reconocimiento cada cierto número
            # de cuadros para reducir el consumo de CPU.
            if (
                self.contador_frames
                % self.INTERVALO_RECONOCIMIENTO == 0
            ):

                self.resultado_reconocimiento = (
                    reconocer_imagen(frame_original)
                )

            # Mostrar identificación.
            if self.resultado_reconocimiento.get(
                "reconocido"
            ):

                nombre = self.resultado_reconocimiento.get(
                    "nombre",
                    "Maestro identificado"
                )

                maestro_id = self.resultado_reconocimiento.get(
                    "maestro_id",
                    ""
                )

                self.lbl_estado.setText(
                    "MAESTRO IDENTIFICADO"
                )

                self.lbl_maestro.setText(
                    f"{nombre} | {maestro_id}"
                )

            else:

                mensaje = self.resultado_reconocimiento.get(
                    "mensaje",
                    "Rostro no reconocido."
                )

                self.lbl_estado.setText(
                    "IDENTIDAD NO CONFIRMADA"
                )

                self.lbl_maestro.setText(
                    mensaje
                )

        # =============================================
        # DIBUJAR ROSTROS
        # =============================================

        for (x, y, ancho, alto) in rostros:

            reconocido = (
                cantidad == 1
                and self.resultado_reconocimiento.get(
                    "reconocido",
                    False
                )
            )

            if reconocido:
                color = (0, 255, 0)
                texto = "MAESTRO IDENTIFICADO"

            else:
                color = (0, 165, 255)
                texto = "VERIFICANDO ROSTRO"

            cv2.rectangle(
                frame,
                (x, y),
                (x + ancho, y + alto),
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

        # =============================================
        # MOSTRAR IMAGEN EN PYSIDE6
        # =============================================

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

    # =================================================
    # DETENER CÁMARA
    # =================================================

    def detener_camara(self):

        self.timer.stop()

        if self.camara is not None:

            self.camara.release()
            self.camara = None

        self.resultado_reconocimiento = {
            "reconocido": False,
            "mensaje": "Cámara detenida."
        }

        self.lbl_camara.setPixmap(QPixmap())

        self.lbl_camara.setText(
            "La cámara está detenida"
        )

        self.lbl_estado.setText(
            "Esperando inicio de cámara..."
        )

        self.lbl_maestro.setText(
            "Ningún maestro identificado"
        )

    # =================================================
    # LIBERAR CÁMARA AL CAMBIAR DE PANTALLA
    # =================================================

    def hideEvent(self, event):

        self.detener_camara()

        super().hideEvent(event)
