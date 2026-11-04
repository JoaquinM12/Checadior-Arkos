
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

ESCALA_RECORTE = 2.7

UMBRAL_ACEPTACION = 0.80

# Orden de clases utilizado por el test.py original
# de MiniVision Silent-Face-Anti-Spoofing.
#
# 0 = Fotografía
# 1 = Rostro real
# 2 = Reproducción en pantalla

CLASE_FOTOGRAFIA = 0
CLASE_REAL = 1
CLASE_PANTALLA = 2


# ==========================================================
# CARGAR MODELO
# ==========================================================

sesion = None

try:

    if not RUTA_MODELO.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo: {RUTA_MODELO}"
        )

    opciones = ort.SessionOptions()

    opciones.log_severity_level = 3

    sesion = ort.InferenceSession(
        str(RUTA_MODELO),
        sess_options=opciones,
        providers=["CPUExecutionProvider"]
    )

    entrada_modelo = sesion.get_inputs()[0].name
    salida_modelo = sesion.get_outputs()[0].name

    print("\n======================================")
    print(" MODELO ANTI-SPOOFING CARGADO")
    print("======================================")
    print(f"Modelo: {RUTA_MODELO}")
    print(f"Entrada: {entrada_modelo}")
    print(f"Salida: {salida_modelo}")
    print(f"Proveedor: {sesion.get_providers()}")
    print("======================================\n")

except Exception as error:

    print("\n[ERROR] No se pudo cargar MiniFASNet:")
    print(error)


# ==========================================================
# RECORTE FACIAL
# ==========================================================

def obtener_nueva_caja(
    ancho_imagen,
    alto_imagen,
    caja,
    escala
):
    """
    Reproduce el procedimiento de recorte de MiniVision.

    caja:
        x, y, ancho, alto
    """

    x, y, ancho, alto = caja

    if ancho <= 0 or alto <= 0:
        raise ValueError("La caja facial no es válida.")

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

    # Ajustar horizontalmente sin salir de la imagen.

    if izquierda < 0:
        derecha -= izquierda
        izquierda = 0

    if derecha > ancho_imagen - 1:
        izquierda -= derecha - (ancho_imagen - 1)
        derecha = ancho_imagen - 1

    # Ajustar verticalmente sin salir de la imagen.

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

    return izquierda, arriba, derecha, abajo, escala_real


def recortar_rostro(imagen_bgr, caja):

    if imagen_bgr is None or imagen_bgr.size == 0:
        raise ValueError("La imagen recibida está vacía.")

    alto_imagen, ancho_imagen = imagen_bgr.shape[:2]

    if len(caja) != 4:
        raise ValueError("La caja debe tener cuatro coordenadas.")

    # Se reciben coordenadas:
    # x1, y1, x2, y2

    x1, y1, x2, y2 = map(int, caja)

    ancho = x2 - x1
    alto = y2 - y1

    if ancho <= 0 or alto <= 0:
        raise ValueError("Las dimensiones del rostro no son válidas.")

    # Limitar la caja original a la imagen.

    x1 = max(0, min(x1, ancho_imagen - 1))
    y1 = max(0, min(y1, alto_imagen - 1))

    x2 = max(0, min(x2, ancho_imagen))
    y2 = max(0, min(y2, alto_imagen))

    ancho = x2 - x1
    alto = y2 - y1

    if ancho <= 0 or alto <= 0:
        raise ValueError("El rostro está fuera de la imagen.")

    # El modelo original recibe x, y, ancho, alto.

    nueva_caja = obtener_nueva_caja(
        ancho_imagen,
        alto_imagen,
        (x1, y1, ancho, alto),
        ESCALA_RECORTE
    )

    izquierda, arriba, derecha, abajo, escala_real = nueva_caja

    # El procedimiento original utiliza límites inclusivos.

    recorte = imagen_bgr[
        arriba:abajo + 1,
        izquierda:derecha + 1
    ]

    if recorte.size == 0:
        raise ValueError("No se pudo obtener el recorte facial.")

    print("\n[ANTI-SPOOF] Recorte original:", recorte.shape)

    print(
        "[ANTI-SPOOF] Caja:",
        (izquierda, arriba, derecha, abajo)
    )

    print(
        "[ANTI-SPOOF] Escala efectiva:",
        round(escala_real, 4)
    )

    proporcion = recorte.shape[1] / recorte.shape[0]

    print(
        "[ANTI-SPOOF] Proporcion del recorte:",
        round(proporcion, 4)
    )

    # Guardar imagen para inspección visual.

    try:

        RUTA_DEBUG.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        cv2.imwrite(
            str(RUTA_DEBUG),
            recorte
        )

        print(
            "[DEBUG] Imagen guardada:",
            RUTA_DEBUG
        )

    except Exception as error:

        print("[DEBUG] No se pudo guardar el recorte:", error)

    return recorte


# ==========================================================
# PREPROCESAMIENTO
# ==========================================================

def preparar_entrada(recorte):

    if recorte is None or recorte.size == 0:
        raise ValueError("El recorte está vacío.")

    # El modelo espera imagen BGR.

    imagen = cv2.resize(
        recorte,
        (TAMANO_ENTRADA, TAMANO_ENTRADA),
        interpolation=cv2.INTER_LINEAR
    )

    # Normalización original: valores entre 0 y 1.

    imagen = imagen.astype(np.float32) / 255.0

    # HWC -> CHW.

    imagen = np.transpose(
        imagen,
        (2, 0, 1)
    )

    # CHW -> NCHW.

    imagen = np.expand_dims(
        imagen,
        axis=0
    )

    print(
        "[ANTI-SPOOF] Entrada:",
        imagen.shape,
        "| Min:",
        round(float(imagen.min()), 4),
        "| Max:",
        round(float(imagen.max()), 4),
        "| Media:",
        round(float(imagen.mean()), 4)
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

    logits = logits - np.max(logits)

    exp_logits = np.exp(logits)

    probabilidades = exp_logits / np.sum(exp_logits)

    return probabilidades


# ==========================================================
# EVALUAR ANTI-SPOOFING
# ==========================================================

def evaluar_rostro(imagen_bgr, caja):

    if sesion is None:
        raise RuntimeError(
            "El modelo MiniFASNet no está cargado."
        )

    # 1. Recortar rostro.

    recorte = recortar_rostro(
        imagen_bgr,
        caja
    )

    # 2. Preparar entrada.

    entrada = preparar_entrada(recorte)

    # 3. Ejecutar modelo.

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
            f"El modelo devolvió {logits.size} clases en lugar de 3."
        )

    # 4. Calcular probabilidades.

    probabilidades = aplicar_softmax(logits)

    prob_fotografia = float(
        probabilidades[CLASE_FOTOGRAFIA]
    )

    prob_real = float(
        probabilidades[CLASE_REAL]
    )

    prob_pantalla = float(
        probabilidades[CLASE_PANTALLA]
    )

    clase = int(np.argmax(probabilidades))

    es_real = (
        clase == CLASE_REAL
        and prob_real >= UMBRAL_ACEPTACION
    )

    # 5. Mensaje.

    if es_real:

        mensaje = "Rostro real."

    elif clase == CLASE_FOTOGRAFIA:

        mensaje = "Posible fotografia."

    elif clase == CLASE_PANTALLA:

        mensaje = "Posible reproduccion en pantalla."

    else:

        mensaje = "Rostro no identificado."

    # 6. Depuración.

    print("\n========== DEBUG ANTI-SPOOFING ==========")

    print("Logits originales:", logits)

    print(
        "Probabilidad fotografia:",
        round(prob_fotografia, 4)
    )

    print(
        "Probabilidad rostro real:",
        round(prob_real, 4)
    )

    print(
        "Probabilidad pantalla:",
        round(prob_pantalla, 4)
    )

    print("Clase seleccionada:", clase)

    print(
        "Umbral de aceptacion:",
        UMBRAL_ACEPTACION
    )

    print("Resultado:", mensaje)

    print("Rostro aceptado:", es_real)

    print("=========================================\n")

    return {
        "correcto": es_real,
        "es_real": es_real,
        "clase": clase,
        "logits": logits,
        "porcentaje_foto": prob_fotografia,
        "porcentaje_real": prob_real,
        "porcentaje_pantalla": prob_pantalla,
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

        resultado = evaluar_rostro(
            imagen_bgr,
            caja
        )

        return resultado

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
