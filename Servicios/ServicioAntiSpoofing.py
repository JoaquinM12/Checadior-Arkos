
import cv2
import numpy as np
import onnxruntime as ort

from pathlib import Path


# ==========================================================
# RUTAS
# ==========================================================

RUTA_PROYECTO = Path(__file__).resolve().parent.parent

RUTA_MODELO = (
    RUTA_PROYECTO
    / "Recursos"
    / "ModelosIA"
    / "minifasnet_v2.onnx"
)


# ==========================================================
# CONFIGURACION
# ==========================================================

TAMANO_MODELO = 80
FACTOR_EXPANSION = 2.7

# Umbral provisional para aceptar un rostro.
# Se calibrara posteriormente con pruebas reales.
UMBRAL_REAL = 0.80

_sesion = None
_nombre_entrada = None
_nombre_salida = None


# ==========================================================
# CARGAR MODELO
# ==========================================================

def cargar_modelo():

    global _sesion
    global _nombre_entrada
    global _nombre_salida

    if _sesion is not None:
        return True

    if not RUTA_MODELO.exists():
        raise FileNotFoundError(
            f"No se encontro el modelo: {RUTA_MODELO}"
        )

    opciones = ort.SessionOptions()

    opciones.graph_optimization_level = (
        ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    )

    opciones.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

    _sesion = ort.InferenceSession(
        str(RUTA_MODELO),
        sess_options=opciones,
        providers=["CPUExecutionProvider"]
    )

    entradas = _sesion.get_inputs()
    salidas = _sesion.get_outputs()

    if not entradas or not salidas:
        raise RuntimeError("El modelo no tiene entradas o salidas.")

    forma = entradas[0].shape

    if len(forma) != 4 or forma[1:] != [3, 80, 80]:
        raise RuntimeError(
            f"Entrada incompatible con MiniFASNet: {forma}"
        )

    if len(salidas[0].shape) != 2 or salidas[0].shape[-1] != 3:
        raise RuntimeError(
            f"Salida incompatible con MiniFASNet: {salidas[0].shape}"
        )

    _nombre_entrada = entradas[0].name
    _nombre_salida = salidas[0].name

    return True


# ==========================================================
# RECORTAR ROSTRO
# ==========================================================

def recortar_rostro(imagen_bgr, caja):

    alto, ancho = imagen_bgr.shape[:2]

    x1, y1, x2, y2 = map(int, caja)

    w = x2 - x1
    h = y2 - y1

    if w <= 0 or h <= 0:
        raise ValueError("Caja facial invalida.")

    lado = max(w, h)

    centro_x = x1 + w / 2
    centro_y = y1 + h / 2

    tamano = int(lado * FACTOR_EXPANSION)

    x = int(centro_x - tamano / 2)
    y = int(centro_y - tamano / 2)

    x_final = x + tamano
    y_final = y + tamano

    recorte = imagen_bgr[
        max(0, y):min(alto, y_final),
        max(0, x):min(ancho, x_final)
    ]

    if recorte.size == 0:
        raise ValueError("No se pudo recortar el rostro.")

    arriba = max(0, -y)
    izquierda = max(0, -x)
    abajo = max(0, y_final - alto)
    derecha = max(0, x_final - ancho)

    if arriba or izquierda or abajo or derecha:
        recorte = cv2.copyMakeBorder(
            recorte,
            arriba,
            abajo,
            izquierda,
            derecha,
            cv2.BORDER_REFLECT_101
        )

    return recorte


# ==========================================================
# PREPARAR IMAGEN
# ==========================================================

def preparar_imagen(imagen_bgr):

    if imagen_bgr is None or imagen_bgr.size == 0:
        raise ValueError("Imagen vacia.")

    imagen = cv2.resize(
        imagen_bgr,
        (TAMANO_MODELO, TAMANO_MODELO),
        interpolation=cv2.INTER_LINEAR
    )

    # MiniFASNet espera BGR, no RGB.
    imagen = imagen.astype(np.float32) / 255.0

    imagen = imagen.transpose(2, 0, 1)

    return np.expand_dims(imagen, axis=0)


# ==========================================================
# EVALUAR ROSTRO
# ==========================================================

def evaluar_rostro(imagen_bgr, caja):

    try:

        cargar_modelo()

        if imagen_bgr is None or imagen_bgr.size == 0:
            raise ValueError("No se recibio una imagen valida.")

        rostro = recortar_rostro(
            imagen_bgr,
            caja
        )

        entrada = preparar_imagen(rostro)

        resultado = _sesion.run(
            [_nombre_salida],
            {_nombre_entrada: entrada}
        )

        salida = np.asarray(
            resultado[0],
            dtype=np.float32
        ).reshape(-1)

        if salida.size != 3:
            raise RuntimeError(
                f"Se esperaban 3 clases. Recibidas: {salida.size}"
            )

        # El modelo devuelve logits.
        # Orden documentado:
        # 0 = fotografia impresa
        # 1 = rostro real
        # 2 = reproduccion en pantalla

        logits = salida - np.max(salida)

        probabilidades = np.exp(logits)
        probabilidades /= np.sum(probabilidades)

        prob_foto = float(probabilidades[0])
        prob_real = float(probabilidades[1])
        prob_pantalla = float(probabilidades[2])

        clase = int(np.argmax(probabilidades))

        es_real = (
            clase == 1
            and prob_real >= UMBRAL_REAL
        )

        if clase == 1:
            mensaje = (
                "Rostro aparentemente real."
                if es_real
                else "Confianza insuficiente para aceptar el rostro."
            )

        elif clase == 0:
            mensaje = "Posible fotografia impresa."

        else:
            mensaje = "Posible reproduccion en pantalla."

        return {
            "correcto": True,
            "es_real": bool(es_real),
            "clase": clase,
            "porcentaje_real": prob_real,
            "porcentaje_foto": prob_foto,
            "porcentaje_pantalla": prob_pantalla,
            "mensaje": mensaje
        }

    except Exception as error:

        return {
            "correcto": False,
            "es_real": False,
            "clase": -1,
            "porcentaje_real": 0.0,
            "porcentaje_foto": 0.0,
            "porcentaje_pantalla": 0.0,
            "mensaje": str(error)
        }


# ==========================================================
# COMPROBAR MODELO
# ==========================================================

def comprobar_anti_spoofing():

    try:

        cargar_modelo()

        return {
            "correcto": True,
            "mensaje": "MiniFASNet-V2 cargado correctamente."
        }

    except Exception as error:

        return {
            "correcto": False,
            "mensaje": str(error)
        }
