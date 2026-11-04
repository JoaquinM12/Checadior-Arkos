
import cv2
import json
import numpy as np
import onnxruntime as ort

from pathlib import Path
from datetime import datetime


# =====================================================
# RUTAS
# =====================================================

RUTA_PROYECTO = Path(__file__).resolve().parent.parent

RUTA_MODELOS = RUTA_PROYECTO / "Recursos" / "ModelosIA"

RUTA_YUNET = RUTA_MODELOS / "yunet.onnx"
RUTA_AURAFACE = RUTA_MODELOS / "auraface.onnx"

RUTA_ROSTROS = RUTA_PROYECTO / "DatosLocales" / "Rostros"

RUTA_EMBEDDINGS = (
    RUTA_PROYECTO / "DatosLocales" / "embeddings_rostros.json"
)


# =====================================================
# CONFIGURACIÓN
# =====================================================

TAMANO_ROSTRO = (112, 112)

UMBRAL_DETECCION = 0.60

PUNTOS_DESTINO = np.array(
    [
        [38.2946, 51.6963],
        [73.5318, 51.5014],
        [56.0252, 71.7366],
        [41.5493, 92.3655],
        [70.7299, 92.2041]
    ],
    dtype=np.float32
)


# =====================================================
# MODELOS IA
# =====================================================

_sesion_auraface = None
_detector_yunet = None


def cargar_modelos():

    global _sesion_auraface
    global _detector_yunet

    if not RUTA_YUNET.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo YuNet: {RUTA_YUNET}"
        )

    if not RUTA_AURAFACE.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo AuraFace: {RUTA_AURAFACE}"
        )

    if _sesion_auraface is None:

        _sesion_auraface = ort.InferenceSession(
            str(RUTA_AURAFACE),
            providers=["CPUExecutionProvider"]
        )

    if _detector_yunet is None:

        _detector_yunet = cv2.FaceDetectorYN.create(
            str(RUTA_YUNET),
            "",
            (640, 640),
            UMBRAL_DETECCION,
            0.30,
            5000
        )

    return _detector_yunet, _sesion_auraface


# =====================================================
# DETECTAR ROSTRO
# =====================================================

def detectar_rostro(imagen):

    detector, _ = cargar_modelos()

    alto, ancho = imagen.shape[:2]

    detector.setInputSize((ancho, alto))

    _, rostros = detector.detect(imagen)

    if rostros is None or len(rostros) == 0:
        raise ValueError("No se detectó ningún rostro.")

    # Seleccionar el rostro de mayor tamaño.
    rostro = max(
        rostros,
        key=lambda r: float(r[2] * r[3])
    )

    confianza = float(rostro[14])

    if confianza < UMBRAL_DETECCION:
        raise ValueError(
            "La confianza de detección es insuficiente."
        )

    puntos = rostro[4:14].reshape(5, 2).astype(
        np.float32
    )

    return puntos, confianza


# =====================================================
# ALINEAR ROSTRO
# =====================================================

def alinear_rostro(imagen, puntos):

    matriz, _ = cv2.estimateAffinePartial2D(
        puntos,
        PUNTOS_DESTINO,
        method=cv2.LMEDS
    )

    if matriz is None:
        raise ValueError(
            "No fue posible alinear el rostro."
        )

    rostro_alineado = cv2.warpAffine(
        imagen,
        matriz,
        TAMANO_ROSTRO,
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0)
    )

    return rostro_alineado


# =====================================================
# GENERAR CARACTERÍSTICAS FACIALES
# =====================================================

def generar_embedding(imagen):

    _, sesion = cargar_modelos()

    puntos, confianza = detectar_rostro(imagen)

    rostro = alinear_rostro(
        imagen,
        puntos
    )

    # Convertir BGR a RGB.
    rostro = cv2.cvtColor(
        rostro,
        cv2.COLOR_BGR2RGB
    )

    # Normalización de imagen.
    rostro = rostro.astype(np.float32)

    rostro = (rostro - 127.5) / 127.5

    # HWC a CHW.
    entrada = np.transpose(
        rostro,
        (2, 0, 1)
    )

    # Agregar dimensión de lote.
    entrada = np.expand_dims(
        entrada,
        axis=0
    ).astype(np.float32)

    nombre_entrada = sesion.get_inputs()[0].name

    resultado = sesion.run(
        None,
        {
            nombre_entrada: entrada
        }
    )[0]

    embedding = resultado[0].astype(
        np.float32
    )

    # Normalización L2.
    norma = np.linalg.norm(embedding)

    if norma == 0:
        raise ValueError(
            "Se generaron características faciales inválidas."
        )

    embedding = embedding / norma

    return embedding, confianza


# =====================================================
# CARGAR CARACTERÍSTICAS GUARDADAS
# =====================================================

def cargar_embeddings_guardados():

    if not RUTA_EMBEDDINGS.exists():
        return {}

    try:

        with open(
            RUTA_EMBEDDINGS,
            "r",
            encoding="utf-8"
        ) as archivo:

            datos = json.load(archivo)

        if not isinstance(datos, dict):
            raise ValueError(
                "El archivo de características tiene formato incorrecto."
            )

        return datos

    except json.JSONDecodeError as error:

        raise ValueError(
            "El archivo embeddings_rostros.json está dañado."
        ) from error


# =====================================================
# GUARDAR CARACTERÍSTICAS
# =====================================================

def guardar_embeddings_guardados(datos):

    RUTA_EMBEDDINGS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    archivo_temporal = RUTA_EMBEDDINGS.with_suffix(
        ".tmp"
    )

    with open(
        archivo_temporal,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            datos,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    archivo_temporal.replace(
        RUTA_EMBEDDINGS
    )


# =====================================================
# PROCESAR FOTOGRAFÍAS DE UN MAESTRO
# =====================================================

def generar_embeddings_maestro(maestro_id):

    carpeta = RUTA_ROSTROS / maestro_id

    if not carpeta.exists():
        raise FileNotFoundError(
            f"No existe la carpeta del maestro: {carpeta}"
        )

    fotografias = sorted(
        [
            archivo
            for archivo in carpeta.iterdir()
            if archivo.suffix.lower() in (
                ".jpg",
                ".jpeg",
                ".png"
            )
        ]
    )

    if not fotografias:
        raise ValueError(
            "El maestro no tiene fotografías registradas."
        )

    embeddings = []
    errores = []

    print("\n========== PROCESAMIENTO FACIAL ==========")

    print("Maestro:", maestro_id)

    print("Fotografías encontradas:", len(fotografias))

    for fotografia in fotografias:

        imagen = cv2.imread(
            str(fotografia)
        )

        if imagen is None:

            errores.append(
                f"{fotografia.name}: no se pudo leer."
            )

            continue

        try:

            embedding, confianza = generar_embedding(
                imagen
            )

            embeddings.append(
                embedding.tolist()
            )

            print(
                f"[CORRECTO] {fotografia.name} "
                f"| Confianza: {confianza:.3f}"
            )

        except Exception as error:

            errores.append(
                f"{fotografia.name}: {error}"
            )

            print(
                f"[ERROR] {fotografia.name}: {error}"
            )

    if not embeddings:

        raise ValueError(
            "No se pudo procesar ninguna fotografía.\n"
            + "\n".join(errores)
        )

    # Calcular representación promedio.
    promedio = np.mean(
        np.array(
            embeddings,
            dtype=np.float32
        ),
        axis=0
    )

    norma = np.linalg.norm(promedio)

    if norma == 0:
        raise ValueError(
            "No se pudo generar la representación promedio."
        )

    promedio = promedio / norma

    # Guardar información del maestro.
    datos = cargar_embeddings_guardados()

    datos[maestro_id] = {

        "embeddings": embeddings,

        "embedding_promedio": promedio.tolist(),

        "cantidad_fotografias": len(embeddings),

        "fecha_procesamiento": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    guardar_embeddings_guardados(datos)

    print("\n========== RESULTADO ==========")

    print(
        "Fotografías procesadas:",
        len(embeddings)
    )

    print(
        "Fotografías con errores:",
        len(errores)
    )

    print(
        "Archivo:",
        RUTA_EMBEDDINGS
    )

    print("================================\n")

    return {
        "maestro_id": maestro_id,
        "fotografias_encontradas": len(fotografias),
        "fotografias_procesadas": len(embeddings),
        "errores": errores,
        "archivo_guardado": str(RUTA_EMBEDDINGS)
    }
