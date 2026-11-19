
import cv2
import json
import numpy as np
import onnxruntime as ort

from pathlib import Path
from datetime import datetime

from Configuracion.ConexionMySQL import obtener_conexion


# =====================================================
# RUTAS
# =====================================================

RUTA_PROYECTO = Path(__file__).resolve().parent.parent

RUTA_MODELOS = RUTA_PROYECTO / "Recursos" / "ModelosIA"

RUTA_YUNET = RUTA_MODELOS / "yunet.onnx"
RUTA_AURAFACE = RUTA_MODELOS / "auraface.onnx"

RUTA_ROSTROS = RUTA_PROYECTO / "DatosLocales" / "Rostros"

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
_tabla_embeddings_asegurada = False


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
    """Carga los vectores faciales desde MySQL."""

    conexion = obtener_conexion()
    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        asegurar_tabla_embeddings(conexion, cursor)
        cursor.execute("""
            SELECT
                id_maestro,
                embeddings,
                embedding_promedio,
                cantidad_fotografias,
                modelo,
                fecha_procesamiento
            FROM tblEmbeddingsRostros
        """)

        datos = {}
        for registro in cursor.fetchall():
            maestro_id = f"MST-{int(registro['id_maestro']):04d}"
            embeddings = registro["embeddings"]
            promedio = registro["embedding_promedio"]

            if isinstance(embeddings, str):
                embeddings = json.loads(embeddings)
            if isinstance(promedio, str):
                promedio = json.loads(promedio)

            fecha = registro["fecha_procesamiento"]
            datos[maestro_id] = {
                "embeddings": embeddings,
                "embedding_promedio": promedio,
                "cantidad_fotografias": registro["cantidad_fotografias"],
                "modelo": registro["modelo"],
                "fecha_procesamiento": (
                    fecha.strftime("%Y-%m-%d %H:%M:%S")
                    if hasattr(fecha, "strftime") else str(fecha)
                ),
            }
        return datos
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def asegurar_tabla_embeddings(conexion=None, cursor=None):
    """Crea la tabla de vectores si aún no existe."""

    global _tabla_embeddings_asegurada
    if _tabla_embeddings_asegurada:
        return

    conexion_propia = conexion is None
    if conexion_propia:
        conexion = obtener_conexion()
        if conexion is None:
            raise ConnectionError("No fue posible conectar con MySQL.")

    cursor_propio = cursor is None
    if cursor_propio:
        cursor = conexion.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tblEmbeddingsRostros (
                id_maestro INT NOT NULL PRIMARY KEY,
                embeddings JSON NOT NULL,
                embedding_promedio JSON NOT NULL,
                cantidad_fotografias TINYINT UNSIGNED NOT NULL,
                dimension_vector SMALLINT UNSIGNED NOT NULL,
                modelo VARCHAR(64) NOT NULL DEFAULT 'AuraFace',
                fecha_procesamiento DATETIME NOT NULL,
                CONSTRAINT FK_tblEmbeddingsRostros_tblMaestros
                    FOREIGN KEY (id_maestro)
                    REFERENCES tblMaestros (id_maestro)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        _tabla_embeddings_asegurada = True
        if conexion_propia:
            conexion.commit()
    finally:
        if cursor_propio:
            cursor.close()
        if conexion_propia:
            conexion.close()


# =====================================================
# GUARDAR CARACTERÍSTICAS
# =====================================================

def guardar_embeddings_guardados(datos):
    """Guarda o actualiza los vectores de maestros en MySQL."""

    if not isinstance(datos, dict):
        raise ValueError("Los vectores faciales no tienen un formato válido.")

    conexion = obtener_conexion()
    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None
    try:
        cursor = conexion.cursor()
        asegurar_tabla_embeddings(conexion, cursor)
        filas = []

        for maestro_id, informacion in datos.items():
            identificador = str(maestro_id).strip().upper()
            if not identificador.startswith("MST-") or not identificador[4:].isdigit():
                raise ValueError(f"ID de maestro no válido: {maestro_id}")
            id_maestro = int(identificador[4:])

            promedio = np.asarray(
                informacion.get("embedding_promedio"),
                dtype=np.float32
            ).reshape(-1)
            embeddings = np.asarray(
                informacion.get("embeddings", [promedio.tolist()]),
                dtype=np.float32
            )

            if promedio.size == 0 or embeddings.ndim != 2:
                raise ValueError(
                    f"Los vectores de {identificador} están incompletos."
                )
            if embeddings.shape[1] != promedio.size:
                raise ValueError(
                    f"Las dimensiones de los vectores de {identificador} "
                    "no coinciden."
                )
            if not np.isfinite(promedio).all() or not np.isfinite(embeddings).all():
                raise ValueError(
                    f"Los vectores de {identificador} contienen valores no válidos."
                )

            fecha_texto = informacion.get("fecha_procesamiento")
            if fecha_texto:
                fecha = datetime.strptime(
                    str(fecha_texto), "%Y-%m-%d %H:%M:%S"
                )
            else:
                fecha = datetime.now()

            filas.append((
                id_maestro,
                json.dumps(embeddings.tolist(), separators=(",", ":")),
                json.dumps(promedio.tolist(), separators=(",", ":")),
                int(informacion.get("cantidad_fotografias", len(embeddings))),
                int(promedio.size),
                str(informacion.get("modelo", "AuraFace"))[:64],
                fecha,
            ))

        if filas:
            cursor.executemany("""
                INSERT INTO tblEmbeddingsRostros (
                    id_maestro,
                    embeddings,
                    embedding_promedio,
                    cantidad_fotografias,
                    dimension_vector,
                    modelo,
                    fecha_procesamiento
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    embeddings = VALUES(embeddings),
                    embedding_promedio = VALUES(embedding_promedio),
                    cantidad_fotografias = VALUES(cantidad_fotografias),
                    dimension_vector = VALUES(dimension_vector),
                    modelo = VALUES(modelo),
                    fecha_procesamiento = VALUES(fecha_procesamiento)
            """, filas)

        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        conexion.close()


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

    # Guardar únicamente este maestro; el UPSERT conserva los demás registros.
    datos = {
        maestro_id: {

            "embeddings": embeddings,

            "embedding_promedio": promedio.tolist(),

            "cantidad_fotografias": len(embeddings),

            "modelo": "AuraFace",

            "fecha_procesamiento": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }
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

    print("Almacenamiento: MySQL / tblEmbeddingsRostros")

    print("================================\n")

    return {
        "maestro_id": maestro_id,
        "fotografias_encontradas": len(fotografias),
        "fotografias_procesadas": len(embeddings),
        "errores": errores,
        "almacenamiento": "MySQL / tblEmbeddingsRostros"
    }
