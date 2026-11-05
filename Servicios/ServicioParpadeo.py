import cv2
import mediapipe as mp
import numpy as np


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
            p1 = np.array([landmarks[puntos_ojo[1]].x, landmarks[puntos_ojo[1]].y])
            p5 = np.array([landmarks[puntos_ojo[5]].x, landmarks[puntos_ojo[5]].y])
            
            p2 = np.array([landmarks[puntos_ojo[2]].x, landmarks[puntos_ojo[2]].y])
            p4 = np.array([landmarks[puntos_ojo[4]].x, landmarks[puntos_ojo[4]].y])
            
            p0 = np.array([landmarks[puntos_ojo[0]].x, landmarks[puntos_ojo[0]].y])
            p3 = np.array([landmarks[puntos_ojo[3]].x, landmarks[puntos_ojo[3]].y])

            # Distancias verticales y horizontal
            dist_v1 = np.linalg.norm(p1 - p5)
            dist_v2 = np.linalg.norm(p2 - p4)
            dist_h = np.linalg.norm(p0 - p3)

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