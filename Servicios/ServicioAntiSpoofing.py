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

RUTA_DEBUG = (
    RUTA_PROYECTO
    / "DatosLocales"
    / "debug_antispoof.jpg"
)


# ==========================================================
# CONFIGURACION
# ==========================================================

TAMANO_ENTRADA = 80
ESCALA_RECORTE = 4.0

# Umbral de aceptación (puedes ajustarlo entre 0.70 y 0.85 según necesites)
UMBRAL_ACEPTACION = 0.95

# ----------------------------------------------------------
# ORDEN DE CLASES CORREGIDO SEGÚN TUS LOGS:
# Clase 2 arrojaba el 99.38% con tu rostro real.
# ----------------------------------------------------------
CLASE_FOTOGRAFIA = 0
CLASE_REAL = 2        
CLASE_PANTALLA = 1    

ORDEN_CLASES_VERIFICADO = True

sesion = None
entrada_modelo = None
salida_modelo = None


# ==========================================================
# CARGAR MODELO
# ==========================================================

def cargar_modelo():

    global sesion
    global entrada_modelo
    global salida_modelo

    if not RUTA_MODELO.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo: {RUTA_MODELO}"
        )

    opciones = ort.SessionOptions()
    opciones.log_severity_level = 3

    nueva_sesion = ort.InferenceSession(
        str(RUTA_MODELO),
        sess_options=opciones,
        providers=["CPUExecutionProvider"]
    )

    entrada = nueva_sesion.get_inputs()[0]
    salida = nueva_sesion.get_outputs()[0]

    print("\n========== INFORMACIÓN MINIFASNET ==========")
    print("Modelo:", RUTA_MODELO)
    print("Entrada:", entrada.name)
    print("Forma:", entrada.shape)
    print("Tipo:", entrada.type)
    print("Salida:", salida.name)
    print("Forma:", salida.shape)
    print("Tipo:", salida.type)
    print("Proveedor:", nueva_sesion.get_providers())
    print("============================================\n")

    sesion = nueva_sesion
    entrada_modelo = entrada.name
    salida_modelo = salida.name


try:
    cargar_modelo()

except Exception as error:
    sesion = None
    print("[ERROR] No se pudo cargar MiniFASNet:", error)


# ==========================================================
# OBTENER CAJA FACIAL
# ==========================================================

def obtener_nueva_caja(
    ancho_imagen,
    alto_imagen,
    caja,
    escala
):

    x, y, ancho, alto = caja

    if ancho <= 0 or alto <= 0:
        raise ValueError("Caja facial no válida.")

    escala_real = min(
        (alto_imagen - 1) / alto,
        (ancho_imagen - 1) / ancho,
        escala
    )

    nuevo_ancho = ancho * escala_real
    nuevo_alto = alto * escala_real

    centro_x = x + ancho / 2
    centro_y = y + alto / 2

    izquierda = centro_x - nuevo_ancho / 2
    derecha = centro_x + nuevo_ancho / 2

    arriba = centro_y - nuevo_alto / 2
    abajo = centro_y + nuevo_alto / 2

    if izquierda < 0:
        derecha -= izquierda
        izquierda = 0

    if derecha > ancho_imagen - 1:
        izquierda -= derecha - (ancho_imagen - 1)
        derecha = ancho_imagen - 1

    if arriba < 0:
        abajo -= arriba
        arriba = 0

    if abajo > alto_imagen - 1:
        arriba -= abajo - (alto_imagen - 1)
        abajo = alto_imagen - 1

    izquierda = max(0, int(izquierda))
    arriba = max(0, int(arriba))

    derecha = min(ancho_imagen - 1, int(derecha))
    abajo = min(alto_imagen - 1, int(abajo))

    return izquierda, arriba, derecha, abajo


# ==========================================================
# RECORTAR ROSTRO
# ==========================================================

def recortar_rostro(imagen_bgr, caja):

    if imagen_bgr is None or imagen_bgr.size == 0:
        raise ValueError("Imagen vacía.")

    alto_imagen, ancho_imagen = imagen_bgr.shape[:2]

    if len(caja) != 4:
        raise ValueError("La caja debe tener cuatro coordenadas.")

    x1, y1, x2, y2 = map(int, caja)

    x1 = max(0, min(x1, ancho_imagen - 1))
    y1 = max(0, min(y1, alto_imagen - 1))

    x2 = max(0, min(x2, ancho_imagen))
    y2 = max(0, min(y2, alto_imagen))

    ancho = x2 - x1
    alto = y2 - y1

    if ancho <= 0 or alto <= 0:
        raise ValueError("Dimensiones faciales incorrectas.")

    izquierda, arriba, derecha, abajo = obtener_nueva_caja(
        ancho_imagen,
        alto_imagen,
        (x1, y1, ancho, alto),
        ESCALA_RECORTE
    )

    recorte = imagen_bgr[
        arriba:abajo + 1,
        izquierda:derecha + 1
    ]

    if recorte.size == 0:
        raise ValueError("Recorte facial vacío.")

    RUTA_DEBUG.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not cv2.imwrite(str(RUTA_DEBUG), recorte):
        raise RuntimeError("No se pudo guardar la imagen de depuración.")

    return recorte


# ==========================================================
# PREPARAR ENTRADA
# ==========================================================

def preparar_entrada(recorte):

    if recorte is None or recorte.size == 0:
        raise ValueError("Recorte vacío.")

    imagen = cv2.resize(
        recorte,
        (TAMANO_ENTRADA, TAMANO_ENTRADA),
        interpolation=cv2.INTER_LINEAR
    )

    imagen = imagen.astype(np.float32) / 255.0

    imagen = np.transpose(
        imagen,
        (2, 0, 1)
    )

    imagen = np.expand_dims(
        imagen,
        axis=0
    )

    return imagen.astype(np.float32)


# ==========================================================
# SOFTMAX
# ==========================================================

def aplicar_softmax(logits):

    logits = np.asarray(
        logits,
        dtype=np.float32
    ).reshape(-1)

    if not np.all(np.isfinite(logits)):
        raise ValueError("El modelo produjo valores no válidos.")

    logits = logits - np.max(logits)

    exp_logits = np.exp(logits)

    suma = np.sum(exp_logits)

    if suma <= 0 or not np.isfinite(suma):
        raise ValueError("No se pudieron calcular probabilidades.")

    return exp_logits / suma


# ==========================================================
# EVALUAR ROSTRO
# ==========================================================

def evaluar_rostro(imagen_bgr, caja):

    if sesion is None:
        raise RuntimeError("MiniFASNet no está cargado.")

    recorte = recortar_rostro(
        imagen_bgr,
        caja
    )

    entrada = preparar_entrada(recorte)

    resultados = sesion.run(
        [salida_modelo],
        {
            entrada_modelo: entrada
        }
    )

    logits = np.asarray(
        resultados[0],
        dtype=np.float32
    ).reshape(-1)

    if logits.size != 3:
        raise ValueError(
            f"Se esperaban 3 salidas y llegaron {logits.size}."
        )

    probabilidades = aplicar_softmax(logits)

    clase = int(np.argmax(probabilidades))

    print("\n========== DEBUG ANTI-SPOOFING ==========")
    print("Logits:", logits)

    for i, probabilidad in enumerate(probabilidades):
        print(
            f"Clase {i}: {probabilidad * 100:.2f}%"
        )

    print("Clase ganadora:", clase)
    print("=========================================\n")

    if not ORDEN_CLASES_VERIFICADO:
        return {
            "correcto": False,
            "es_real": False,
            "clase": clase,
            "logits": logits,
            "probabilidades": probabilidades,
            "porcentaje_foto": float(probabilidades[0]),
            "porcentaje_real": float(probabilidades[1]),
            "porcentaje_pantalla": float(probabilidades[2]),
            "mensaje": "Pendiente de verificar el orden de clases."
        }

    prob_real = float(
        probabilidades[CLASE_REAL]
    )

    es_real = (
        clase == CLASE_REAL
        and prob_real >= UMBRAL_ACEPTACION
    )

    if es_real:
        mensaje = "Rostro real."
    elif clase == CLASE_FOTOGRAFIA:
        mensaje = "Posible fotografía."
    elif clase == CLASE_PANTALLA:
        mensaje = "Posible reproducción en pantalla."
    else:
        mensaje = "Rostro no identificado."

    return {
        "correcto": es_real,
        "es_real": es_real,
        "clase": clase,
        "logits": logits,
        "probabilidades": probabilidades,
        "porcentaje_foto": float(probabilidades[CLASE_FOTOGRAFIA]),
        "porcentaje_real": prob_real,
        "porcentaje_pantalla": float(probabilidades[CLASE_PANTALLA]),
        "mensaje": mensaje
    }


# ==========================================================
# FUNCION PARA VISCHECADOR
# ==========================================================

def procesar_anti_spoofing(
    imagen_bgr,
    x,
    y,
    ancho,
    alto
):

    try:

        caja = (
            int(x),
            int(y),
            int(x + ancho),
            int(y + alto)
        )

        return evaluar_rostro(
            imagen_bgr,
            caja
        )

    except Exception as error:

        print("\n[ERROR ANTI-SPOOFING]")
        print(error)

        return {
            "correcto": False,
            "es_real": False,
            "clase": -1,
            "logits": None,
            "porcentaje_foto": 0.0,
            "porcentaje_real": 0.0,
            "porcentaje_pantalla": 0.0,
            "mensaje": "Error al evaluar el rostro."
        }