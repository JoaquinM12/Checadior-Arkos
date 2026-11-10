
# ==========================================================
# SERVICIO DE HORARIOS
# Archivo: Servicios/ServicioHorarios.py
# ==========================================================

from datetime import datetime

from Configuracion.Firebase import db
from Servicios.ServicioMaterias import cargar_materias
from Servicios.ServicioAlmacenamiento import cargar_maestros


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

COLECCION_HORARIOS = "tblHorarios"
COLECCION_MAESTROS = "tblMaestros"

DIAS_VALIDOS = [
    "LUNES",
    "MARTES",
    "MIÉRCOLES",
    "JUEVES",
    "VIERNES",
    "SÁBADO"
]


# ==========================================================
# GENERAR ID DE HORARIO
# ==========================================================

def generar_id_horario():

    documentos = db.collection(
        COLECCION_HORARIOS
    ).stream()

    mayor = 0

    for documento in documentos:

        identificador = documento.id

        if identificador.startswith("HOR-"):

            try:
                numero = int(
                    identificador.replace("HOR-", "")
                )

                mayor = max(mayor, numero)

            except ValueError:
                continue

    return f"HOR-{mayor + 1:04d}"


# ==========================================================
# VALIDAR HORARIO
# ==========================================================

def validar_horario(
    id_materia,
    id_maestro,
    dia,
    hora_inicio,
    hora_fin
):

    if not id_materia:
        raise ValueError(
            "Debes seleccionar una materia."
        )

    if not id_maestro:
        raise ValueError(
            "Debes seleccionar un maestro."
        )

    dia = str(dia).strip().upper()

    if dia not in DIAS_VALIDOS:
        raise ValueError(
            "El día seleccionado no es válido."
        )

    try:
        inicio = datetime.strptime(
            str(hora_inicio),
            "%H:%M"
        )

        fin = datetime.strptime(
            str(hora_fin),
            "%H:%M"
        )

    except ValueError:
        raise ValueError(
            "El formato de las horas debe ser HH:MM."
        )

    if fin <= inicio:
        raise ValueError(
            "La hora de salida debe ser posterior "
            "a la hora de entrada."
        )

    return {
        "id_materia": id_materia,
        "id_maestro": id_maestro,
        "dia": dia,
        "hora_inicio": str(hora_inicio),
        "hora_fin": str(hora_fin)
    }


# ==========================================================
# OBTENER MATERIA
# ==========================================================

def obtener_materia(id_materia):

    referencia = db.collection(
        "tblMaterias"
    ).document(id_materia)

    documento = referencia.get()

    if not documento.exists:
        raise ValueError(
            "La materia seleccionada no existe."
        )

    materia = documento.to_dict() or {}

    if materia.get("activo", True) is False:
        raise ValueError(
            "La materia seleccionada está desactivada."
        )

    materia["id"] = documento.id

    return materia


# ==========================================================
# OBTENER MAESTRO
# ==========================================================

def obtener_maestro(id_maestro):

    maestros = cargar_maestros()

    for maestro in maestros:

        if maestro.get("id") == id_maestro:

            if maestro.get(
                "activo",
                maestro.get("Activo", True)
            ) is False:

                raise ValueError(
                    "El maestro seleccionado está desactivado."
                )

            nombre = (
                maestro.get("nombre")
                or maestro.get("Nombre")
                or ""
            )

            apellidos = (
                maestro.get("apellidos")
                or maestro.get("Apellidos")
                or ""
            )

            nombre_completo = (
                f"{nombre} {apellidos}"
            ).strip()

            if not nombre_completo:
                nombre_completo = id_maestro

            return {
                "id": id_maestro,
                "nombre": nombre_completo
            }

    raise ValueError(
        "No se encontró el maestro seleccionado."
    )


# ==========================================================
# VERIFICAR CRUCE DE HORARIOS
# ==========================================================

def verificar_cruce_horario(
    id_maestro,
    dia,
    hora_inicio,
    hora_fin,
    excluir_id=None
):

    documentos = db.collection(
        COLECCION_HORARIOS
    ).stream()

    for documento in documentos:

        if documento.id == excluir_id:
            continue

        horario = documento.to_dict() or {}

        if horario.get("activo", True) is False:
            continue

        if horario.get("id_maestro") != id_maestro:
            continue

        if horario.get("dia") != dia:
            continue

        inicio_existente = horario.get(
            "hora_inicio",
            ""
        )

        fin_existente = horario.get(
            "hora_fin",
            ""
        )

        # Comprobar si los horarios se cruzan.
        if (
            hora_inicio < fin_existente
            and hora_fin > inicio_existente
        ):

            raise ValueError(
                "El maestro ya tiene otro horario "
                f"registrado el día {dia} "
                f"de {inicio_existente} a {fin_existente}."
            )


# ==========================================================
# REGISTRAR HORARIO
# ==========================================================

def registrar_horario(
    id_materia,
    id_maestro,
    dia,
    hora_inicio,
    hora_fin
):

    datos = validar_horario(
        id_materia,
        id_maestro,
        dia,
        hora_inicio,
        hora_fin
    )

    materia = obtener_materia(id_materia)
    maestro = obtener_maestro(id_maestro)

    verificar_cruce_horario(
        id_maestro,
        datos["dia"],
        datos["hora_inicio"],
        datos["hora_fin"]
    )

    identificador = generar_id_horario()

    datos.update({
        "id": identificador,
        "maestro": maestro["nombre"],
        "materia": materia["nombre"],
        "carrera": materia["carrera"],
        "cuatrimestre": materia["cuatrimestre"],
        "activo": True
    })

    db.collection(
        COLECCION_HORARIOS
    ).document(identificador).create(datos)

    return identificador


# ==========================================================
# CARGAR HORARIOS
# ==========================================================

def cargar_horarios(
    solo_activos=True,
    id_maestro=None,
    id_materia=None
):

    documentos = db.collection(
        COLECCION_HORARIOS
    ).stream()

    horarios = []

    for documento in documentos:

        horario = documento.to_dict() or {}

        horario["id"] = documento.id

        if (
            solo_activos
            and horario.get("activo", True) is False
        ):
            continue

        if (
            id_maestro
            and horario.get("id_maestro") != id_maestro
        ):
            continue

        if (
            id_materia
            and horario.get("id_materia") != id_materia
        ):
            continue

        horarios.append(horario)

    horarios.sort(
        key=lambda horario: (
            DIAS_VALIDOS.index(horario.get("dia"))
            if horario.get("dia") in DIAS_VALIDOS
            else 99,
            horario.get("hora_inicio", "")
        )
    )

    return horarios


# ==========================================================
# ACTUALIZAR HORARIO
# ==========================================================

def actualizar_horario(
    identificador,
    id_materia,
    id_maestro,
    dia,
    hora_inicio,
    hora_fin
):

    if not identificador:
        raise ValueError(
            "No se proporcionó el ID del horario."
        )

    referencia = db.collection(
        COLECCION_HORARIOS
    ).document(identificador)

    documento = referencia.get()

    if not documento.exists:
        raise ValueError(
            "El horario que intentas modificar no existe."
        )

    horario_actual = documento.to_dict() or {}

    if horario_actual.get("activo", True) is False:
        raise ValueError(
            "No puedes modificar un horario desactivado."
        )

    datos = validar_horario(
        id_materia,
        id_maestro,
        dia,
        hora_inicio,
        hora_fin
    )

    materia = obtener_materia(id_materia)
    maestro = obtener_maestro(id_maestro)

    verificar_cruce_horario(
        id_maestro,
        datos["dia"],
        datos["hora_inicio"],
        datos["hora_fin"],
        excluir_id=identificador
    )

    datos.update({
        "maestro": maestro["nombre"],
        "materia": materia["nombre"],
        "carrera": materia["carrera"],
        "cuatrimestre": materia["cuatrimestre"]
    })

    referencia.update(datos)


# ==========================================================
# DESACTIVAR HORARIO
# ==========================================================

def desactivar_horario(identificador):

    if not identificador:
        raise ValueError(
            "No se proporcionó el ID del horario."
        )

    referencia = db.collection(
        COLECCION_HORARIOS
    ).document(identificador)

    documento = referencia.get()

    if not documento.exists:
        raise ValueError(
            "El horario no existe."
        )

    referencia.update({
        "activo": False
    })


# ==========================================================
# REACTIVAR HORARIO
# ==========================================================

def reactivar_horario(identificador):

    if not identificador:
        raise ValueError(
            "No se proporcionó el ID del horario."
        )

    referencia = db.collection(
        COLECCION_HORARIOS
    ).document(identificador)

    documento = referencia.get()

    if not documento.exists:
        raise ValueError(
            "El horario no existe."
        )

    horario = documento.to_dict() or {}

    if horario.get("activo", True):
        raise ValueError(
            "El horario ya está activo."
        )

    verificar_cruce_horario(
        horario.get("id_maestro"),
        horario.get("dia"),
        horario.get("hora_inicio"),
        horario.get("hora_fin"),
        excluir_id=identificador
    )

    referencia.update({
        "activo": True
    })
