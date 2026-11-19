
# ==========================================================
# SERVICIO DE CLASES IMPARTIDAS
# Archivo: Servicios/ServicioClasesImpartidas.py
# Base de datos: MySQL
# ==========================================================

from datetime import datetime, timedelta, time

from Configuracion.ConexionMySQL import obtener_conexion


# Minutos de anticipación permitidos para registrar asistencia.
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
# CONVERTIR HORA DE MYSQL A DATETIME.TIME
# ==========================================================

def convertir_hora(valor):

    if isinstance(valor, time):
        return valor

    if isinstance(valor, timedelta):

        segundos = int(valor.total_seconds())

        horas = (segundos // 3600) % 24
        minutos = (segundos % 3600) // 60
        segundos = segundos % 60

        return time(horas, minutos, segundos)

    if isinstance(valor, str):

        valor = valor.strip()

        for formato in ("%H:%M:%S", "%H:%M"):

            try:
                return datetime.strptime(
                    valor[:8],
                    formato
                ).time()

            except ValueError:
                continue

    raise ValueError(
        f"Formato de hora no válido: {valor}"
    )


# ==========================================================
# CONVERTIR IDENTIFICADORES A ID NUMÉRICO DE MYSQL
# ==========================================================

def convertir_id_maestro(id_maestro):

    if id_maestro is None:
        raise ValueError(
            "No se proporcionó el identificador del maestro."
        )

    if isinstance(id_maestro, int):
        return id_maestro

    texto = str(id_maestro).strip().upper()

    if texto.startswith("MST-"):
        texto = texto.replace("MST-", "", 1)

    try:
        return int(texto)

    except ValueError:
        raise ValueError(
            f"El identificador del maestro no es válido: {id_maestro}"
        )


def convertir_id_horario(id_horario):

    if id_horario is None:
        raise ValueError(
            "No se proporcionó el identificador del horario."
        )

    if isinstance(id_horario, int):
        return id_horario

    texto = str(id_horario).strip().upper()

    if texto.startswith("HOR-"):
        texto = texto.replace("HOR-", "", 1)

    try:
        return int(texto)

    except ValueError:
        raise ValueError(
            f"El identificador del horario no es válido: {id_horario}"
        )


# ==========================================================
# CONSULTAR HORARIOS DE UN MAESTRO
# ==========================================================

def cargar_horarios_maestro(id_maestro):

    conexion = None
    cursor = None

    try:

        id_maestro_sql = convertir_id_maestro(id_maestro)

        conexion = obtener_conexion()

        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                h.id_horario AS id,
                h.id_maestro,
                h.id_materia,
                h.dia,
                h.hora_inicio,
                h.hora_fin,
                h.turno,
                h.estado,

                m.nombre AS materia,
                m.carrera,
                m.cuatrimestre,

                CONCAT(ma.nombre, ' ', ma.apellido) AS maestro

            FROM tblHorarios h

            INNER JOIN tblMaterias m
                ON h.id_materia = m.id_materia

            INNER JOIN tblMaestros ma
                ON h.id_maestro = ma.id_maestro

            WHERE
                h.id_maestro = %s
                AND h.estado = 'ACTIVO'
                AND ma.estado = 'ACTIVO'

            ORDER BY
                FIELD(
                    h.dia,
                    'LUNES',
                    'MARTES',
                    'MIÉRCOLES',
                    'JUEVES',
                    'VIERNES',
                    'SÁBADO',
                    'DOMINGO'
                ),
                h.hora_inicio
        """

        cursor.execute(
            consulta,
            (id_maestro_sql,)
        )

        horarios = cursor.fetchall()

        return horarios

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


# ==========================================================
# OBTENER CLASE ACTUAL
# ==========================================================

def obtener_clase_actual(id_maestro, fecha_hora=None):

    if fecha_hora is None:
        fecha_hora = datetime.now()

    if not isinstance(fecha_hora, datetime):
        raise ValueError(
            "La fecha y hora proporcionadas no son válidas."
        )

    dia_actual = DIAS_SEMANA[fecha_hora.weekday()]

    horarios = cargar_horarios_maestro(id_maestro)

    for horario in horarios:

        dia_horario = str(
            horario.get("dia", "")
        ).strip().upper()

        if dia_horario != dia_actual:
            continue

        try:

            hora_inicio = convertir_hora(
                horario.get("hora_inicio")
            )

            hora_fin = convertir_hora(
                horario.get("hora_fin")
            )

        except (ValueError, TypeError):
            continue

        inicio_clase = datetime.combine(
            fecha_hora.date(),
            hora_inicio
        )

        fin_clase = datetime.combine(
            fecha_hora.date(),
            hora_fin
        )

        # Permitir registrar asistencia antes de la clase.
        inicio_permitido = (
            inicio_clase
            - timedelta(minutes=MINUTOS_ANTICIPACION)
        )

        if inicio_permitido <= fecha_hora < fin_clase:
            return horario

    return None


# ==========================================================
# OBTENER PRÓXIMA CLASE DEL DÍA
# ==========================================================

def obtener_proxima_clase(id_maestro, fecha_hora=None):

    if fecha_hora is None:
        fecha_hora = datetime.now()

    if not isinstance(fecha_hora, datetime):
        raise ValueError(
            "La fecha y hora proporcionadas no son válidas."
        )

    dia_actual = DIAS_SEMANA[fecha_hora.weekday()]

    horarios = cargar_horarios_maestro(id_maestro)

    proximas = []

    for horario in horarios:

        dia_horario = str(
            horario.get("dia", "")
        ).strip().upper()

        if dia_horario != dia_actual:
            continue

        try:

            hora_inicio = convertir_hora(
                horario.get("hora_inicio")
            )

        except (ValueError, TypeError):
            continue

        inicio_clase = datetime.combine(
            fecha_hora.date(),
            hora_inicio
        )

        if inicio_clase > fecha_hora:
            proximas.append(horario)

    proximas.sort(
        key=lambda horario: convertir_hora(
            horario.get("hora_inicio")
        )
    )

    if proximas:
        return proximas[0]

    return None


# ==========================================================
# GENERAR IDENTIFICADOR DE REFERENCIA
# ==========================================================

def generar_id_clase(id_maestro, id_horario, fecha_hora):

    id_maestro_sql = convertir_id_maestro(id_maestro)

    id_horario_sql = convertir_id_horario(id_horario)

    fecha = fecha_hora.strftime("%Y%m%d")

    return (
        f"CLA-{id_maestro_sql}-"
        f"{id_horario_sql}-{fecha}"
    )


# ==========================================================
# CONSULTAR SI YA SE REGISTRÓ LA CLASE
# ==========================================================

def buscar_registro_clase(
    id_maestro,
    id_horario,
    fecha_hora
):

    conexion = None
    cursor = None

    try:

        id_maestro_sql = convertir_id_maestro(id_maestro)

        id_horario_sql = convertir_id_horario(id_horario)

        if not isinstance(fecha_hora, datetime):
            raise ValueError(
                "La fecha de consulta no es válida."
            )

        conexion = obtener_conexion()

        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                ci.id_clase AS id,
                ci.id_maestro,
                ci.id_horario,
                ci.fecha,
                ci.hora_asistencia,
                ci.estado,
                ci.observaciones,

                CONCAT(ma.nombre, ' ', ma.apellido) AS maestro,
                ma.nombre,
                ma.apellido,

                m.nombre AS materia,
                m.carrera,
                m.cuatrimestre,

                h.dia,
                h.hora_inicio,
                h.hora_fin

            FROM tblClasesImpartidas ci

            INNER JOIN tblMaestros ma
                ON ci.id_maestro = ma.id_maestro

            INNER JOIN tblHorarios h
                ON ci.id_horario = h.id_horario

            INNER JOIN tblMaterias m
                ON h.id_materia = m.id_materia

            WHERE
                ci.id_maestro = %s
                AND ci.id_horario = %s
                AND DATE(ci.fecha) = %s

            LIMIT 1
        """

        cursor.execute(
            consulta,
            (
                id_maestro_sql,
                id_horario_sql,
                fecha_hora.date()
            )
        )

        return cursor.fetchone()

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


# ==========================================================
# REGISTRAR ASISTENCIA Y TEMAS IMPARTIDOS
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

    id_maestro_sql = convertir_id_maestro(id_maestro)

    id_horario_sql = convertir_id_horario(id_horario)

    hora_inicio = convertir_hora(
        horario.get("hora_inicio")
    )

    inicio_clase = datetime.combine(
        fecha_hora_reconocimiento.date(),
        hora_inicio
    )

    # Determinar si la asistencia fue puntual o retardo.
    if fecha_hora_reconocimiento > inicio_clase:
        estado = "RETARDO"
    else:
        estado = "ASISTENCIA"

    observaciones = f"Temas impartidos:\n{temas}"

    if len(observaciones) > 500:
        raise ValueError(
            "Los temas exceden los 500 caracteres permitidos "
            "por la columna observaciones de MySQL."
        )

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor(dictionary=True)

        # Verificar que el maestro exista y esté activo.
        cursor.execute(
            """
            SELECT id_maestro
            FROM tblMaestros
            WHERE
                id_maestro = %s
                AND estado = 'ACTIVO'
            """,
            (id_maestro_sql,)
        )

        if not cursor.fetchone():
            raise ValueError(
                "El maestro no existe o se encuentra inactivo."
            )

        # Verificar que el horario pertenezca al maestro.
        cursor.execute(
            """
            SELECT id_horario
            FROM tblHorarios
            WHERE
                id_horario = %s
                AND id_maestro = %s
                AND estado = 'ACTIVO'
            """,
            (
                id_horario_sql,
                id_maestro_sql
            )
        )

        if not cursor.fetchone():
            raise ValueError(
                "El horario no existe, está inactivo "
                "o no pertenece al maestro."
            )

        # Evitar duplicar la asistencia de la misma clase.
        cursor.execute(
            """
            SELECT id_clase
            FROM tblClasesImpartidas
            WHERE
                id_maestro = %s
                AND id_horario = %s
                AND DATE(fecha) = %s
            LIMIT 1
            """,
            (
                id_maestro_sql,
                id_horario_sql,
                fecha_hora_reconocimiento.date()
            )
        )

        registro_existente = cursor.fetchone()

        if registro_existente:
            raise ValueError(
                "La asistencia de esta clase ya fue registrada."
            )

        # Insertar asistencia en MySQL.
        consulta = """
            INSERT INTO tblClasesImpartidas (
                id_maestro,
                id_horario,
                fecha,
                hora_asistencia,
                estado,
                observaciones
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            consulta,
            (
                id_maestro_sql,
                id_horario_sql,
                fecha_hora_reconocimiento,
                fecha_hora_reconocimiento,
                estado,
                observaciones
            )
        )

        id_clase = cursor.lastrowid

        conexion.commit()

        return id_clase

    except Exception:

        if conexion:
            conexion.rollback()

        raise

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()
