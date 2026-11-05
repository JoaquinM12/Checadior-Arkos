import json
from pathlib import Path
from datetime import datetime

from Configuracion.Firebase import db


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

COLECCION_MAESTROS = "tblMaestros"

RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_DATOS = RUTA_PROYECTO / "DatosLocales"
RUTA_MAESTROS = RUTA_DATOS / "maestros.json"


# ==========================================================
# VALIDAR IDENTIFICADOR
# ==========================================================

def es_id_maestro_valido(identificador):

    identificador = str(identificador).strip()

    if not identificador.startswith("MST-"):
        return False

    numero = identificador[4:]

    return numero.isdigit()


# ==========================================================
# PREPARAR ALMACENAMIENTO LOCAL
# ==========================================================

def preparar_almacenamiento():

    RUTA_DATOS.mkdir(
        parents=True,
        exist_ok=True
    )

    if not RUTA_MAESTROS.exists():

        with open(
            RUTA_MAESTROS,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                [],
                archivo,
                ensure_ascii=False,
                indent=4
            )


# ==========================================================
# REFERENCIA A LA COLECCIÓN
# ==========================================================

def obtener_coleccion_maestros():

    return db.collection(COLECCION_MAESTROS)


# ==========================================================
# CARGAR MAESTROS DESDE FIREBASE
# ==========================================================

def cargar_maestros():

    print("\n========== CARGA DE MAESTROS ==========")
    print("Origen: Firebase Firestore")
    print("Colección:", COLECCION_MAESTROS)

    try:

        documentos = obtener_coleccion_maestros().stream()

        maestros = []

        for documento in documentos:

            identificador = documento.id

            # Ignorar documentos con ID automático de Firebase
            if not es_id_maestro_valido(identificador):
                print("Documento ignorado:", identificador)
                continue

            maestro = documento.to_dict() or {}

            nombre = str(maestro.get("nombre", "")).strip()
            apellidos = str(maestro.get("apellidos", "")).strip()

            # Ignorar registros incompletos
            if not nombre or not apellidos:
                print("Maestro incompleto ignorado:", identificador)
                continue

            maestro["id"] = identificador

            maestros.append(maestro)

        maestros.sort(
            key=lambda maestro: int(maestro["id"].split("-")[1])
        )

        print("Cantidad de maestros:", len(maestros))
        print("=======================================\n")

        return maestros

    except Exception as error:

        print("ERROR AL CARGAR MAESTROS:", error)
        raise


# ==========================================================
# GUARDAR MAESTROS EN FIREBASE
# ==========================================================

def guardar_maestros(maestros):

    if not isinstance(maestros, list):

        raise ValueError(
            "Los datos de maestros deben estar en una lista."
        )

    try:

        coleccion = obtener_coleccion_maestros()

        for inicio in range(0, len(maestros), 450):

            lote = db.batch()

            grupo = maestros[inicio:inicio + 450]

            for maestro in grupo:

                identificador = str(
                    maestro.get("id", "")
                ).strip()

                if not es_id_maestro_valido(identificador):

                    raise ValueError(
                        f"Identificador de maestro inválido: {identificador}"
                    )

                datos = maestro.copy()
                datos["id"] = identificador

                referencia = coleccion.document(identificador)

                # Guardar sin eliminar otros documentos
                lote.set(referencia, datos)

            lote.commit()

        print("Maestros guardados correctamente en Firebase.")

    except Exception as error:

        print("ERROR AL GUARDAR MAESTROS:", error)
        raise


# ==========================================================
# GENERAR ID AUTOMÁTICO
# ==========================================================

def generar_id_maestro(maestros=None):

    if maestros is None:
        maestros = cargar_maestros()

    numeros = []

    for maestro in maestros:

        identificador = str(
            maestro.get("id", "")
        ).strip()

        if es_id_maestro_valido(identificador):

            numeros.append(
                int(identificador.split("-")[1])
            )

    siguiente = max(numeros, default=0) + 1

    return f"MST-{siguiente:04d}"


# ==========================================================
# REGISTRAR NUEVO MAESTRO
# ==========================================================

def registrar_maestro(nombre, apellidos):

    nombre = nombre.strip()
    apellidos = apellidos.strip()

    if not nombre or not apellidos:

        raise ValueError(
            "Debes ingresar nombre y apellidos."
        )

    try:

        maestros = cargar_maestros()

        identificador = generar_id_maestro(maestros)

        nuevo_maestro = {

            "id": identificador,
            "nombre": nombre,
            "apellidos": apellidos,
            "activo": True,

            "fecha_registro": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        }

        referencia = obtener_coleccion_maestros().document(
            identificador
        )

        # Evitar sobrescribir un documento existente
        referencia.create(nuevo_maestro)

        print("Maestro registrado:", identificador)

        return nuevo_maestro

    except Exception as error:

        print("ERROR AL REGISTRAR MAESTRO:", error)
        raise


# ==========================================================
# ACTUALIZAR MAESTRO
# ==========================================================

def actualizar_maestro(
    id_maestro,
    nombre,
    apellidos,
    activo
):

    nombre = nombre.strip()
    apellidos = apellidos.strip()

    if not nombre or not apellidos:

        raise ValueError(
            "Debes ingresar nombre y apellidos."
        )

    if not es_id_maestro_valido(id_maestro):

        raise ValueError(
            "El identificador del maestro no es válido."
        )

    try:

        referencia = obtener_coleccion_maestros().document(
            id_maestro
        )

        documento = referencia.get()

        if not documento.exists:

            raise ValueError(
                "No se encontró el maestro seleccionado."
            )

        datos_actualizados = {

            "nombre": nombre,
            "apellidos": apellidos,
            "activo": bool(activo)

        }

        referencia.update(datos_actualizados)

        maestro = documento.to_dict()
        maestro.update(datos_actualizados)
        maestro["id"] = id_maestro

        print("Maestro actualizado:", id_maestro)

        return maestro

    except Exception as error:

        print("ERROR AL ACTUALIZAR MAESTRO:", error)
        raise


# ==========================================================
# BUSCAR MAESTRO POR ID
# ==========================================================

def buscar_maestro(id_maestro):

    if not es_id_maestro_valido(id_maestro):
        return None

    try:

        referencia = obtener_coleccion_maestros().document(
            id_maestro
        )

        documento = referencia.get()

        if not documento.exists:
            return None

        maestro = documento.to_dict() or {}

        if not maestro.get("nombre") or not maestro.get("apellidos"):
            return None

        maestro["id"] = documento.id

        return maestro

    except Exception as error:

        print("ERROR AL BUSCAR MAESTRO:", error)
        raise


# ==========================================================
# MIGRAR MAESTROS LOCALES A FIREBASE
# ==========================================================

def migrar_maestros_locales_a_firebase():

    preparar_almacenamiento()

    print("\n========== MIGRACIÓN A FIREBASE ==========")

    try:

        with open(
            RUTA_MAESTROS,
            "r",
            encoding="utf-8"
        ) as archivo:

            maestros_locales = json.load(archivo)

        if not isinstance(maestros_locales, list):

            raise ValueError(
                "El archivo maestros.json no contiene una lista."
            )

        coleccion = obtener_coleccion_maestros()

        documentos_actuales = {
            documento.id
            for documento in coleccion.stream()
        }

        migrados = 0
        omitidos = 0

        batch = db.batch()
        operaciones_lote = 0

        for maestro in maestros_locales:

            identificador = str(
                maestro.get("id", "")
            ).strip()

            # Solo migrar identificadores MST válidos
            if not es_id_maestro_valido(identificador):

                omitidos += 1
                continue

            if identificador in documentos_actuales:

                omitidos += 1
                continue

            datos = maestro.copy()
            datos["id"] = identificador

            referencia = coleccion.document(identificador)

            batch.set(referencia, datos)

            migrados += 1
            operaciones_lote += 1

            if operaciones_lote >= 450:

                batch.commit()

                batch = db.batch()
                operaciones_lote = 0

        if operaciones_lote > 0:
            batch.commit()

        resultado = {

            "migrados": migrados,
            "omitidos": omitidos,
            "total_locales": len(maestros_locales)

        }

        print("Migración terminada.")
        print("Maestros migrados:", migrados)
        print("Maestros omitidos:", omitidos)
        print("==========================================\n")

        return resultado

    except Exception as error:

        print("ERROR EN LA MIGRACIÓN:", error)
        raise
