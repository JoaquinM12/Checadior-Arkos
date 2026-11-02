
import numpy as np

from Servicios.ServicioReconocimiento import (
    generar_embedding,
    cargar_embeddings_guardados
)

from Servicios.ServicioAlmacenamiento import (
    cargar_maestros
)


# =====================================================
# CONFIGURACIÓN
# =====================================================

# Umbral provisional. Se ajustará con pruebas reales.
UMBRAL_SIMILITUD = 0.45


# =====================================================
# CARGAR MAESTROS REGISTRADOS
# =====================================================

def obtener_maestros_activos():

    maestros = cargar_maestros()

    return {
        maestro["id"]: maestro
        for maestro in maestros
        if maestro.get("activo", True)
    }


# =====================================================
# COMPARAR CARACTERÍSTICAS FACIALES
# =====================================================

def calcular_similitud(embedding1, embedding2):

    vector1 = np.asarray(
        embedding1,
        dtype=np.float32
    )

    vector2 = np.asarray(
        embedding2,
        dtype=np.float32
    )

    if vector1.shape != vector2.shape:
        raise ValueError(
            "Las características faciales tienen dimensiones diferentes."
        )

    norma1 = np.linalg.norm(vector1)
    norma2 = np.linalg.norm(vector2)

    if norma1 == 0 or norma2 == 0:
        raise ValueError(
            "Se encontró una representación facial inválida."
        )

    similitud = np.dot(
        vector1,
        vector2
    ) / (norma1 * norma2)

    return float(similitud)


# =====================================================
# RECONOCER MAESTRO
# =====================================================

def reconocer_imagen(imagen):

    if imagen is None:
        return {
            "reconocido": False,
            "mensaje": "No se recibió ninguna imagen."
        }

    try:

        # Generar características del rostro capturado.
        embedding_actual, confianza = generar_embedding(
            imagen
        )

        # Cargar características guardadas.
        embeddings_guardados = cargar_embeddings_guardados()

        if not embeddings_guardados:

            return {
                "reconocido": False,
                "mensaje": "No hay maestros registrados facialmente."
            }

        # Consultar maestros activos.
        maestros = obtener_maestros_activos()

        mejor_id = None
        mejor_similitud = -1.0

        # Comparar con cada maestro.
        for maestro_id, datos in embeddings_guardados.items():

            if maestro_id not in maestros:
                continue

            embedding_referencia = datos.get(
                "embedding_promedio"
            )

            if embedding_referencia is None:
                continue

            similitud = calcular_similitud(
                embedding_actual,
                embedding_referencia
            )

            if similitud > mejor_similitud:

                mejor_similitud = similitud
                mejor_id = maestro_id

        # No hubo coincidencias válidas.
        if mejor_id is None:

            return {
                "reconocido": False,
                "mensaje": "No se encontró un maestro registrado.",
                "similitud": None
            }

        # Verificar umbral.
        if mejor_similitud < UMBRAL_SIMILITUD:

            return {
                "reconocido": False,
                "mensaje": "Rostro no reconocido.",
                "similitud": round(mejor_similitud, 4),
                "umbral": UMBRAL_SIMILITUD
            }

        maestro = maestros[mejor_id]

        nombre_completo = (
            maestro.get("nombre", "")
            + " "
            + maestro.get("apellidos", "")
        ).strip()

        return {
            "reconocido": True,
            "maestro_id": mejor_id,
            "nombre": nombre_completo,
            "similitud": round(mejor_similitud, 4),
            "confianza_deteccion": round(confianza, 4),
            "mensaje": "Maestro identificado correctamente."
        }

    except Exception as error:

        return {
            "reconocido": False,
            "mensaje": str(error)
        }
