
import cv2
from pathlib import Path
import re


# =====================================
# RUTAS
# =====================================

RUTA_PROYECTO = Path(__file__).resolve().parent.parent

RUTA_ROSTROS = (
    RUTA_PROYECTO /
    "DatosLocales" /
    "Rostros"
)


# =====================================
# PREPARAR ALMACENAMIENTO
# =====================================

def preparar_almacenamiento_rostros():

    RUTA_ROSTROS.mkdir(
        parents=True,
        exist_ok=True
    )


# =====================================
# OBTENER CARPETA DEL MAESTRO
# =====================================

def obtener_carpeta_maestro(maestro_id):

    preparar_almacenamiento_rostros()

    maestro_id = str(maestro_id).strip()

    if not re.fullmatch(r"MST-\d{4,}", maestro_id):
        raise ValueError("El ID del maestro no es válido.")

    carpeta = RUTA_ROSTROS / maestro_id

    carpeta.mkdir(
        parents=True,
        exist_ok=True
    )

    return carpeta


# =====================================
# CONTAR FOTOGRAFÍAS
# =====================================

def contar_fotografias(maestro_id):

    carpeta = obtener_carpeta_maestro(maestro_id)

    fotografias = list(
        carpeta.glob("rostro_*.jpg")
    )

    return len(fotografias)


# =====================================
# GUARDAR FOTOGRAFÍA
# =====================================

def guardar_fotografia_rostro(maestro_id, imagen):

    if imagen is None or imagen.size == 0:
        raise ValueError("La fotografía está vacía.")

    carpeta = obtener_carpeta_maestro(maestro_id)

    existentes = list(
        carpeta.glob("rostro_*.jpg")
    )

    numero = len(existentes) + 1

    ruta_imagen = (
        carpeta /
        f"rostro_{numero:02d}.jpg"
    )

    guardado = cv2.imwrite(
        str(ruta_imagen),
        imagen,
        [cv2.IMWRITE_JPEG_QUALITY, 95]
    )

    if not guardado:
        raise IOError("No se pudo guardar la fotografía.")

    return ruta_imagen


# =====================================
# CONSULTAR FOTOGRAFÍAS
# =====================================

def obtener_fotografias(maestro_id):

    carpeta = obtener_carpeta_maestro(maestro_id)

    fotografias = sorted(
        carpeta.glob("rostro_*.jpg")
    )

    return fotografias
