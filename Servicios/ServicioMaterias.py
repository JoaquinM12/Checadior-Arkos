
# ==========================================================
# SERVICIO DE MATERIAS
# Archivo: Servicios/ServicioMaterias.py
# ==========================================================

from Configuracion.Firebase import db


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

COLECCION_MATERIAS = "tblMaterias"

CARRERAS_VALIDAS = [
    "LAET",
    "LCON",
    "LDER"
]

CUATRIMESTRES_VALIDOS = [
    "PRIMERO",
    "SEGUNDO",
    "TERCERO",
    "CUARTO",
    "QUINTO",
    "SEXTO",
    "SÉPTIMO",
    "OCTAVO",
    "NOVENO"
]


# ==========================================================
# GENERAR ID DE MATERIA
# ==========================================================

def generar_id_materia():

    documentos = db.collection(
        COLECCION_MATERIAS
    ).stream()

    mayor = 0

    for documento in documentos:

        identificador = documento.id

        if identificador.startswith("MAT-"):

            try:
                numero = int(
                    identificador.replace("MAT-", "")
                )

                mayor = max(mayor, numero)

            except ValueError:
                continue

    return f"MAT-{mayor + 1:04d}"


# ==========================================================
# VALIDAR DATOS
# ==========================================================

def validar_materia(nombre, carrera, cuatrimestre):

    nombre = str(nombre).strip()
    carrera = str(carrera).strip().upper()
    cuatrimestre = str(cuatrimestre).strip().upper()

    if not nombre:
        raise ValueError(
            "El nombre de la materia es obligatorio."
        )

    if carrera not in CARRERAS_VALIDAS:
        raise ValueError(
            "La carrera seleccionada no es válida."
        )

    if cuatrimestre not in CUATRIMESTRES_VALIDOS:
        raise ValueError(
            "El cuatrimestre seleccionado no es válido."
        )

    return {
        "nombre": nombre,
        "carrera": carrera,
        "cuatrimestre": cuatrimestre
    }


# ==========================================================
# VERIFICAR MATERIAS DUPLICADAS
# ==========================================================

def existe_materia(
    nombre,
    carrera,
    cuatrimestre,
    excluir_id=None
):

    documentos = db.collection(
        COLECCION_MATERIAS
    ).stream()

    nombre_busqueda = nombre.strip().casefold()

    for documento in documentos:

        if documento.id == excluir_id:
            continue

        materia = documento.to_dict() or {}

        if materia.get("activo", True) is False:
            continue

        mismo_nombre = (
            materia.get("nombre", "").strip().casefold()
            == nombre_busqueda
        )

        misma_carrera = (
            materia.get("carrera", "").upper()
            == carrera
        )

        mismo_cuatrimestre = (
            materia.get("cuatrimestre", "").upper()
            == cuatrimestre
        )

        if (
            mismo_nombre
            and misma_carrera
            and mismo_cuatrimestre
        ):
            return True

    return False


# ==========================================================
# REGISTRAR MATERIA
# ==========================================================

def registrar_materia(nombre, carrera, cuatrimestre):

    datos = validar_materia(
        nombre,
        carrera,
        cuatrimestre
    )

    if existe_materia(
        datos["nombre"],
        datos["carrera"],
        datos["cuatrimestre"]
    ):
        raise ValueError(
            "Esta materia ya está registrada "
            "para esa carrera y cuatrimestre."
        )

    identificador = generar_id_materia()

    datos["id"] = identificador
    datos["activo"] = True

    db.collection(
        COLECCION_MATERIAS
    ).document(identificador).create(datos)

    return identificador


# ==========================================================
# CARGAR MATERIAS
# ==========================================================

def cargar_materias(solo_activas=True):

    documentos = db.collection(
        COLECCION_MATERIAS
    ).stream()

    materias = []

    for documento in documentos:

        materia = documento.to_dict() or {}

        materia["id"] = documento.id

        if (
            solo_activas
            and materia.get("activo", True) is False
        ):
            continue

        materias.append(materia)

    materias.sort(
        key=lambda materia: (
            materia.get("carrera", ""),
            materia.get("cuatrimestre", ""),
            materia.get("nombre", "").casefold()
        )
    )

    return materias


# ==========================================================
# ACTUALIZAR MATERIA
# ==========================================================

def actualizar_materia(
    identificador,
    nombre,
    carrera,
    cuatrimestre
):

    if not identificador:
        raise ValueError(
            "No se proporcionó el ID de la materia."
        )

    referencia = db.collection(
        COLECCION_MATERIAS
    ).document(identificador)

    documento = referencia.get()

    if not documento.exists:
        raise ValueError(
            "La materia que intentas modificar no existe."
        )

    datos = validar_materia(
        nombre,
        carrera,
        cuatrimestre
    )

    if existe_materia(
        datos["nombre"],
        datos["carrera"],
        datos["cuatrimestre"],
        excluir_id=identificador
    ):
        raise ValueError(
            "Ya existe otra materia con ese nombre, "
            "carrera y cuatrimestre."
        )

    referencia.update(datos)


# ==========================================================
# DESACTIVAR MATERIA
# ==========================================================

def desactivar_materia(identificador):

    if not identificador:
        raise ValueError(
            "No se proporcionó el ID de la materia."
        )

    referencia = db.collection(
        COLECCION_MATERIAS
    ).document(identificador)

    documento = referencia.get()

    if not documento.exists:
        raise ValueError(
            "La materia no existe."
        )

    referencia.update({
        "activo": False
    })


# ==========================================================
# REACTIVAR MATERIA
# ==========================================================

def reactivar_materia(identificador):

    if not identificador:
        raise ValueError(
            "No se proporcionó el ID de la materia."
        )

    referencia = db.collection(
        COLECCION_MATERIAS
    ).document(identificador)

    documento = referencia.get()

    if not documento.exists:
        raise ValueError(
            "La materia no existe."
        )

    referencia.update({
        "activo": True
    })
