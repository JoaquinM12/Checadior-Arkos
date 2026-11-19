import cv2
import mediapipe as mp
from math import hypot


class DetectorParpadeo:
    def __init__(self, umbral_ear=0.21, frames_consecutivos=2):
        # Umbral para considerar que el ojo está cerrado
        self.umbral_ear = umbral_ear
        # Cuántos frames seguidos debe estar cerrado para contar como parpadeo real
        self.frames_consecutivos = frames_consecutivos
        
        self.contador_frames = 0
        self.parpadeo_detectado = False

        # Inicializar MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Índices de los puntos clave (landmarks) de los ojos en MediaPipe
        self.ojo_izq_indices = [362, 385, 387, 263, 373, 380]
        self.ojo_der_indices = [33, 160, 158, 133, 153, 144]

    def _calcular_ear(self, puntos_ojo, landmarks):
        """Calcula la Relación de Aspecto del Ojo (EAR)"""
        try:
            p0, p1, p2, p3, p4, p5 = (
                landmarks[indice]
                for indice in puntos_ojo
            )

            # Calcular las distancias sin crear arreglos temporales.
            dist_v1 = hypot(p1.x - p5.x, p1.y - p5.y)
            dist_v2 = hypot(p2.x - p4.x, p2.y - p4.y)
            dist_h = hypot(p0.x - p3.x, p0.y - p3.y)

            if dist_h == 0:
                return 0.0

            ear = (dist_v1 + dist_v2) / (2.0 * dist_h)
            return ear
        except Exception:
            return 0.3

    def evaluar_fotograma(self, imagen_bgr):
        """
        Analiza un fotograma para detectar si ocurrió un parpadeo.
        Devuelve True si se detecta un parpadeo válido, False si no.
        """
        imagen_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)
        resultados = self.face_mesh.process(imagen_rgb)

        if not resultados.multi_face_landmarks:
            return False

        landmarks = resultados.multi_face_landmarks[0].landmark

        ear_izq = self._calcular_ear(self.ojo_izq_indices, landmarks)
        ear_der = self._calcular_ear(self.ojo_der_indices, landmarks)
        
        ear_promedio = (ear_izq + ear_der) / 2.0

        if ear_promedio < self.umbral_ear:
            self.contador_frames += 1
        else:
            if self.contador_frames >= self.frames_consecutivos:
                self.parpadeo_detectado = True
            self.contador_frames = 0

        return self.parpadeo_detectado

    def reiniciar(self):
        """Reinicia el estado del parpadeo"""
        self.contador_frames = 0
        self.parpadeo_detectado = False
