import os
import cv2

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout,
    QCheckBox, QMessageBox
)

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap

from Servicios.ServicioRostros import (
    guardar_fotografia_rostro,
    contar_fotografias
)

from Servicios.ServicioReconocimiento import (
    generar_embeddings_maestro
)


class VisRostros(QWidget):

    volver_solicitado = Signal()

    MAX_FOTOGRAFIAS = 10

    def __init__(self, maestro):
        super().__init__()

        self.maestro = maestro

        self.camara = None
        self.frame_actual = None
        self.rostros_actuales = []

        self.procesando = False
        self.registro_completado = False

        self.detector_rostros = None

        self.crear_detector()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)

        self.crear_interfaz()
        self.actualizar_contador()

    # =====================================
    # DETECTOR FACIAL YUNET
    # =====================================

    def crear_detector(self):

        ruta_base = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        self.ruta_modelo_yunet = os.path.join(
            ruta_base,
            "Recursos",
            "ModelosIA",
            "yunet.onnx"
        )

        if not os.path.isfile(self.ruta_modelo_yunet):
            raise FileNotFoundError(
                f"No se encontró YuNet: {self.ruta_modelo_yunet}"
            )

        self.detector_rostros = cv2.FaceDetectorYN.create(
            self.ruta_modelo_yunet,
            "",
            (320, 320),
            0.7,
            0.3,
            5000
        )

        print("DETECTOR YUNET CARGADO")
        print(self.ruta_modelo_yunet)

    # =====================================
    # INTERFAZ
    # =====================================

    def crear_interfaz(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 25, 35, 25)
        layout.setSpacing(15)

        titulo = QLabel("REGISTRO FACIAL DE MAESTROS")
        titulo.setAlignment(Qt.AlignCenter)

        titulo.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #001F3F;
        """)

        nombre_completo = (
            f"{self.maestro.get('nombre', '')} "
            f"{self.maestro.get('apellidos', '')}"
        )

        self.lbl_maestro = QLabel(
            f"Maestro: {nombre_completo}\n"
            f"ID: {self.maestro.get('id', '')}"
        )

        self.lbl_maestro.setStyleSheet("""
            background-color: white;
            color: #003B73;
            font-size: 15px;
            font-weight: bold;
            padding: 12px;
            border-radius: 8px;
        """)

        self.chk_autorizacion = QCheckBox(
            "Confirmo que el docente fue informado y autorizó "
            "el registro de sus fotografías faciales."
        )

        self.chk_autorizacion.stateChanged.connect(
            self.actualizar_estado_botones
        )

        self.lbl_camara = QLabel("La cámara está detenida")
        self.lbl_camara.setAlignment(Qt.AlignCenter)
        self.lbl_camara.setMinimumSize(640, 380)

        self.lbl_camara.setStyleSheet("""
            background-color: #1C1C1C;
            color: white;
            font-size: 20px;
            border-radius: 10px;
        """)

        self.lbl_estado = QLabel(
            "Marca la autorización para comenzar."
        )

        self.lbl_estado.setAlignment(Qt.AlignCenter)

        self.lbl_estado.setStyleSheet("""
            color: #003B73;
            font-size: 15px;
            font-weight: bold;
            padding: 5px;
        """)

        self.lbl_contador = QLabel("Fotografías: 0 / 10")
        self.lbl_contador.setAlignment(Qt.AlignCenter)

        self.lbl_contador.setStyleSheet("""
            color: #001F3F;
            font-size: 17px;
            font-weight: bold;
        """)

        botones = QHBoxLayout()
        botones.setSpacing(10)

        self.btn_iniciar = QPushButton("INICIAR CÁMARA")
        self.btn_capturar = QPushButton("CAPTURAR ROSTRO")
        self.btn_detener = QPushButton("DETENER CÁMARA")
        self.btn_procesar = QPushButton("PROCESAR REGISTRO FACIAL")
        self.btn_volver = QPushButton("VOLVER")

        lista_botones = [
            self.btn_iniciar,
            self.btn_capturar,
            self.btn_detener,
            self.btn_procesar,
            self.btn_volver
        ]

        for boton in lista_botones:
            boton.setMinimumHeight(43)
            boton.setCursor(Qt.PointingHandCursor)

        self.btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: #003B73;
                color: white;
                border: none;
                border-radius: 7px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #1677C8;
            }
            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #64748B;
            }
        """)

        self.btn_capturar.setStyleSheet("""
            QPushButton {
                background-color: #16803C;
                color: white;
                border: none;
                border-radius: 7px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #22A052;
            }
            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #64748B;
            }
        """)

        self.btn_detener.setStyleSheet("""
            QPushButton {
                background-color: #C0392B;
                color: white;
                border: none;
                border-radius: 7px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #E74C3C;
            }
        """)

        self.btn_procesar.setStyleSheet("""
            QPushButton {
                background-color: #FF851B;
                color: white;
                border: none;
                border-radius: 7px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #E66F00;
            }
            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #64748B;
            }
        """)

        self.btn_volver.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                color: #001F3F;
                border: none;
                border-radius: 7px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #CBD5E1;
            }
        """)

        self.btn_iniciar.clicked.connect(self.iniciar_camara)
        self.btn_capturar.clicked.connect(self.capturar_rostro)
        self.btn_detener.clicked.connect(self.detener_camara)
        self.btn_procesar.clicked.connect(self.procesar_registro_facial)
        self.btn_volver.clicked.connect(self.volver)

        for boton in lista_botones:
            botones.addWidget(boton)

        layout.addWidget(titulo)
        layout.addWidget(self.lbl_maestro)
        layout.addWidget(self.chk_autorizacion)
        layout.addWidget(self.lbl_camara, 1)
        layout.addWidget(self.lbl_estado)
        layout.addWidget(self.lbl_contador)
        layout.addLayout(botones)

        self.actualizar_estado_botones()

        
    # =====================================
    # CONTADOR
    # =====================================

    def actualizar_contador(self):

        cantidad = contar_fotografias(
            self.maestro["id"]
        )

        self.lbl_contador.setText(
            f"Fotografías: {cantidad} / {self.MAX_FOTOGRAFIAS}"
        )

        self.actualizar_estado_botones()

    # =====================================
    # ESTADO DE BOTONES
    # =====================================

    def actualizar_estado_botones(self):

        autorizado = self.chk_autorizacion.isChecked()

        cantidad = contar_fotografias(
            self.maestro["id"]
        )

        self.btn_iniciar.setEnabled(
            autorizado
            and self.camara is None
            and cantidad < self.MAX_FOTOGRAFIAS
            and not self.procesando
            and not self.registro_completado
        )

        self.btn_capturar.setEnabled(
            autorizado
            and self.camara is not None
            and len(self.rostros_actuales) == 1
            and cantidad < self.MAX_FOTOGRAFIAS
            and not self.procesando
        )

        self.btn_detener.setEnabled(
            self.camara is not None
        )

        self.btn_procesar.setEnabled(
            autorizado
            and cantidad == self.MAX_FOTOGRAFIAS
            and self.camara is None
            and not self.procesando
            and not self.registro_completado
        )

    # =====================================
    # INICIAR CÁMARA
    # =====================================

    def iniciar_camara(self):

        if not self.chk_autorizacion.isChecked():
            QMessageBox.warning(
                self,
                "Autorización necesaria",
                "El docente debe autorizar el registro."
            )
            return

        if self.camara is not None:
            return

        self.camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        if not self.camara.isOpened():
            self.camara.release()
            self.camara = cv2.VideoCapture(0)

        if not self.camara.isOpened():

            self.camara.release()
            self.camara = None

            QMessageBox.critical(
                self,
                "Error",
                "No se pudo acceder a la cámara."
            )

            self.actualizar_estado_botones()
            return

        self.camara.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.lbl_estado.setText(
            "Cámara iniciada. Buscando rostro..."
        )

        self.timer.start(30)

        self.actualizar_estado_botones()

    # =====================================
    # ACTUALIZAR FRAME CON YUNET
    # =====================================

    def actualizar_frame(self):

        if self.camara is None:
            return

        correcto, frame = self.camara.read()

        if not correcto or frame is None:
            return

        frame = cv2.flip(frame, 1)

        alto, ancho = frame.shape[:2]

        try:

            self.detector_rostros.setInputSize(
                (ancho, alto)
            )

            _, detecciones = self.detector_rostros.detect(frame)

        except cv2.error as error:

            self.lbl_estado.setText(
                f"Error YuNet: {error}"
            )
            return

        rostros = []

        if detecciones is not None:

            for deteccion in detecciones:

                x, y, w, h = deteccion[:4]

                rostros.append((
                    max(0, int(x)),
                    max(0, int(y)),
                    int(w),
                    int(h)
                ))

        self.frame_actual = frame.copy()
        self.rostros_actuales = rostros

        for x, y, w, h in rostros:

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                3
            )

            cv2.putText(
                frame,
                "ROSTRO DETECTADO",
                (x, max(y - 10, 25)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        if len(rostros) == 0:
            self.lbl_estado.setText("No se detectaron rostros.")

        elif len(rostros) == 1:
            self.lbl_estado.setText(
                "Rostro detectado. Puedes capturar."
            )

        else:
            self.lbl_estado.setText(
                "Debe aparecer una sola persona."
            )

        self.actualizar_estado_botones()

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        alto, ancho, canales = frame_rgb.shape

        imagen = QImage(
            frame_rgb.data,
            ancho,
            alto,
            canales * ancho,
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

    # =====================================
    # CAPTURAR ROSTRO
    # =====================================

    def capturar_rostro(self):

        if not self.chk_autorizacion.isChecked():
            return

        if self.frame_actual is None:
            return

        if len(self.rostros_actuales) != 1:

            QMessageBox.warning(
                self,
                "Rostro no válido",
                "Debe aparecer exactamente un rostro."
            )
            return

        cantidad = contar_fotografias(
            self.maestro["id"]
        )

        if cantidad >= self.MAX_FOTOGRAFIAS:
            self.detener_camara()
            return

        x, y, ancho, alto = self.rostros_actuales[0]

        margen_x = int(ancho * 0.20)
        margen_y = int(alto * 0.20)

        inicio_x = max(0, x - margen_x)
        inicio_y = max(0, y - margen_y)

        fin_x = min(
            self.frame_actual.shape[1],
            x + ancho + margen_x
        )

        fin_y = min(
            self.frame_actual.shape[0],
            y + alto + margen_y
        )

        rostro = self.frame_actual[
            inicio_y:fin_y,
            inicio_x:fin_x
        ]

        if rostro.size == 0:
            return

        try:

            ruta = guardar_fotografia_rostro(
                self.maestro["id"],
                rostro
            )

            print("Fotografía guardada:", ruta)

            self.actualizar_contador()

            self.lbl_estado.setText(
                "Fotografía guardada correctamente."
            )

            if contar_fotografias(
                self.maestro["id"]
            ) >= self.MAX_FOTOGRAFIAS:

                self.detener_camara()

                QMessageBox.information(
                    self,
                    "Fotografías completadas",
                    "Se registraron las 10 fotografías."
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al guardar",
                str(error)
            )

    # =====================================
    # PROCESAR REGISTRO FACIAL
    # =====================================

    def procesar_registro_facial(self):

        if not self.chk_autorizacion.isChecked():
            return

        if self.camara is not None:
            self.detener_camara()

        cantidad = contar_fotografias(
            self.maestro["id"]
        )

        if cantidad != self.MAX_FOTOGRAFIAS:

            QMessageBox.warning(
                self,
                "Fotografías incompletas",
                f"Se necesitan 10 fotografías. Actualmente: {cantidad}"
            )
            return

        respuesta = QMessageBox.question(
            self,
            "Procesar registro facial",
            "Se procesarán las fotografías con AuraFace.\n¿Continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        self.procesando = True
        self.actualizar_estado_botones()

        self.lbl_estado.setText(
            "Procesando registro facial..."
        )

        try:

            resultado = generar_embeddings_maestro(
                self.maestro["id"]
            )

            procesadas = resultado.get(
                "fotografias_procesadas", 0
            )

            errores = resultado.get("errores", [])

            if procesadas != self.MAX_FOTOGRAFIAS:

                QMessageBox.warning(
                    self,
                    "Procesamiento incompleto",
                    f"Se procesaron {procesadas} de 10 fotografías.\n\n"
                    + "\n".join(errores)
                )

                return

            self.registro_completado = True

            self.lbl_estado.setText(
                "¡Registro facial completado!"
            )

            QMessageBox.information(
                self,
                "Registro exitoso",
                f"Maestro: {self.maestro.get('nombre', '')}\n"
                f"ID: {self.maestro['id']}\n"
                f"Fotografías procesadas: {procesadas}"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error de procesamiento",
                str(error)
            )

        finally:

            self.procesando = False
            self.actualizar_estado_botones()

    # =====================================
    # DETENER CÁMARA
    # =====================================

    def detener_camara(self):

        self.timer.stop()

        if self.camara is not None:
            self.camara.release()
            self.camara = None

        self.frame_actual = None
        self.rostros_actuales = []

        self.lbl_camara.setPixmap(QPixmap())
        self.lbl_camara.setText("La cámara está detenida")

        if not self.procesando:
            self.lbl_estado.setText("Cámara detenida.")

        self.actualizar_estado_botones()

    # =====================================
    # VOLVER
    # =====================================

    def volver(self):

        self.detener_camara()
        self.volver_solicitado.emit()

    # =====================================
    # CERRAR PANTALLA
    # =====================================

    def hideEvent(self, event):

        self.detener_camara()
        super().hideEvent(event)
