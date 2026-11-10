
# ==========================================================
# SERVICIO DE CLASES IMPARTIDAS
# Archivo: Servicios/ServicioClasesImpartidas.py
# ==========================================================

from datetime import datetime, timedelta

from Configuracion.Firebase import db
from Servicios.ServicioHorarios import cargar_horarios

from google.api_core.exceptions import AlreadyExists


COLECCION_CLASES = "tblClasesImpartidas"

# Minutos que el maestro puede anticiparse a su clase cambiar despues a 15min antes.
MINUTOS_ANTICIPACION = 30

DIAS_SEMANA = [
    "LUNES",
    "MARTES",
    "MIÉRCOLES",
    "JUEVES",
    "VIERNES",
    "SÁBADO",
    "DOMINGO"
]


# ==========================================================
# OBTENER CLASE ACTUAL
# ==========================================================

def obtener_clase_actual(id_maestro, fecha_hora=None):

    if fecha_hora is None:
        fecha_hora = datetime.now()

    dia_actual = DIAS_SEMANA[fecha_hora.weekday()]

    horarios = cargar_horarios(
        solo_activos=True,
        id_maestro=id_maestro
    )

    for horario in horarios:

        dia_horario = str(
            horario.get("dia", "")
        ).strip().upper()

        if dia_horario != dia_actual:
            continue

        inicio = str(
            horario.get("hora_inicio", "")
        ).strip()

        fin = str(
            horario.get("hora_fin", "")
        ).strip()

        try:
            hora_inicio = datetime.strptime(
                inicio[:5],
                "%H:%M"
            ).time()

            hora_fin = datetime.strptime(
                fin[:5],
                "%H:%M"
            ).time()

        except ValueError:
            continue

        inicio_clase = datetime.combine(
            fecha_hora.date(),
            hora_inicio
        )

        fin_clase = datetime.combine(
            fecha_hora.date(),
            hora_fin
        )

        # Permitir checar antes del inicio de clase.
        inicio_permitido = (
            inicio_clase
            - timedelta(minutes=MINUTOS_ANTICIPACION)
        )

        # Aceptar desde 10 minutos antes hasta el final
        # de la clase.
        if inicio_permitido <= fecha_hora < fin_clase:
            return horario

    return None


# ==========================================================
# OBTENER PRÓXIMA CLASE DEL DÍA
# ==========================================================

def obtener_proxima_clase(id_maestro, fecha_hora=None):

    if fecha_hora is None:
        fecha_hora = datetime.now()

    dia_actual = DIAS_SEMANA[fecha_hora.weekday()]

    horarios = cargar_horarios(
        solo_activos=True,
        id_maestro=id_maestro
    )

    proximas = []

    for horario in horarios:

        dia_horario = str(
            horario.get("dia", "")
        ).strip().upper()

        if dia_horario != dia_actual:
            continue

        inicio = str(
            horario.get("hora_inicio", "")
        ).strip()

        try:
            hora_inicio = datetime.strptime(
                inicio[:5],
                "%H:%M"
            ).time()

        except ValueError:
            continue

        inicio_clase = datetime.combine(
            fecha_hora.date(),
            hora_inicio
        )

        if inicio_clase > fecha_hora:
            proximas.append(horario)

    proximas.sort(
        key=lambda horario: horario.get("hora_inicio", "")
    )

    if proximas:
        return proximas[0]

    return None


# ==========================================================
# GENERAR IDENTIFICADOR ÚNICO DE ASISTENCIA
# ==========================================================

def generar_id_clase(id_maestro, id_horario, fecha_hora):

    fecha = fecha_hora.strftime("%Y%m%d")

    return (
        f"CLA-{id_maestro}-"
        f"{id_horario}-{fecha}"
    )


# ==========================================================
# CONSULTAR SI YA SE REGISTRÓ LA CLASE
# ==========================================================

def buscar_registro_clase(
    id_maestro,
    id_horario,
    fecha_hora
):

    identificador = generar_id_clase(
        id_maestro,
        id_horario,
        fecha_hora
    )

    documento = db.collection(
        COLECCION_CLASES
    ).document(identificador).get()

    if documento.exists:
        datos = documento.to_dict() or {}
        datos["id"] = documento.id
        return datos

    return None


# ==========================================================
# REGISTRAR ASISTENCIA Y TEMAS
# ==========================================================

def registrar_clase_impartida(
    maestro,
    horario,
    fecha_hora_reconocimiento,
    temas
):

    if not maestro or not horario:
        raise ValueError(
            "Faltan los datos del maestro o del horario."
        )

    if not isinstance(fecha_hora_reconocimiento, datetime):
        raise ValueError(
            "La fecha de reconocimiento no es válida."
        )

    temas = str(temas).strip()

    if not temas:
        raise ValueError(
            "Debes escribir los temas impartidos."
        )

    id_maestro = maestro.get("id")
    id_horario = horario.get("id")

    if not id_maestro or not id_horario:
        raise ValueError(
            "No se encontró el identificador del maestro "
            "o del horario."
        )

    identificador = generar_id_clase(
        id_maestro,
        id_horario,
        fecha_hora_reconocimiento
    )

    datos = {

        "id": identificador,

        "id_maestro": id_maestro,

        "maestro": (
            maestro.get("nombre")
            or horario.get("maestro")
            or id_maestro
        ),

        "id_horario": id_horario,
        "id_materia": horario.get("id_materia"),

        "materia": horario.get("materia"),
        "carrera": horario.get("carrera"),
        "cuatrimestre": horario.get("cuatrimestre"),

        "dia": horario.get("dia"),

        "hora_inicio_clase": horario.get("hora_inicio"),
        "hora_fin_clase": horario.get("hora_fin"),

        "fecha": fecha_hora_reconocimiento.strftime(
            "%Y-%m-%d"
        ),

        "hora_asistencia": fecha_hora_reconocimiento.strftime(
            "%H:%M:%S"
        ),

        "fecha_hora_reconocimiento": (
            fecha_hora_reconocimiento.isoformat()
        ),

        "temas": temas,

        "estado": "REGISTRADA"

    }

    referencia = db.collection(
        COLECCION_CLASES
    ).document(identificador)

    try:

        # Evita sobrescribir una asistencia existente.
        referencia.create(datos)

    except AlreadyExists:

        raise ValueError(
            "La asistencia de esta clase ya fue registrada."
        )

    return identificador
