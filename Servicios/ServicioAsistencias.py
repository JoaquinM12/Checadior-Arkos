
# ==========================================================
# SERVICIO DE ASISTENCIAS
# Archivo: Servicios/ServicioAsistencias.py
# Base de datos: MySQL - ARKOS
# ==========================================================

from Configuracion.ConexionMySQL import obtener_conexion
from datetime import date, datetime, timedelta


def cargar_control_diario(fecha):
    """Devuelve las clases activas del día y su última asistencia."""

    if isinstance(fecha, datetime):
        fecha = fecha.date()

    if not isinstance(fecha, date):
        raise ValueError("La fecha del control diario no es válida.")

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                h.id_horario,
                h.id_maestro,
                CONCAT(m.nombre, ' ', m.apellido) AS maestro,
                ma.nombre AS materia,
                ma.carrera,
                ma.cuatrimestre,
                h.hora_inicio,
                h.hora_fin,
                ci.id_clase AS asistencia_id,
                ci.estado AS estado_asistencia,
                ci.hora_asistencia,
                ci.observaciones AS observaciones_asistencia,
                falta.id_falta,
                falta.tipo AS estado_falta,
                falta.maestro_cubrio,
                falta.observaciones AS observaciones_falta
            FROM tblHorarios h
            INNER JOIN tblMaestros m
                ON h.id_maestro = m.id_maestro
            INNER JOIN tblMaterias ma
                ON h.id_materia = ma.id_materia
            LEFT JOIN (
                SELECT id_horario, id_maestro, MAX(id_clase) AS id_clase
                FROM tblClasesImpartidas
                WHERE fecha >= %s AND fecha < %s
                GROUP BY id_horario, id_maestro
            ) ultima
                ON ultima.id_horario = h.id_horario
                AND ultima.id_maestro = h.id_maestro
            LEFT JOIN tblClasesImpartidas ci
                ON ci.id_clase = ultima.id_clase
            LEFT JOIN (
                SELECT id_horario, id_maestro, MAX(id_falta) AS id_falta
                FROM tblFaltas
                WHERE fecha >= %s AND fecha < %s
                GROUP BY id_horario, id_maestro
            ) ultima_falta
                ON ultima_falta.id_horario = h.id_horario
                AND ultima_falta.id_maestro = h.id_maestro
            LEFT JOIN tblFaltas falta
                ON falta.id_falta = ultima_falta.id_falta
            WHERE h.estado = 'ACTIVO'
                AND m.estado = 'ACTIVO'
                AND h.dia = %s
            ORDER BY h.hora_inicio, m.apellido, m.nombre
            """,
            (
                fecha,
                fecha + timedelta(days=1),
                fecha,
                fecha + timedelta(days=1),
                (
                    "LUNES", "MARTES", "MIÉRCOLES", "JUEVES",
                    "VIERNES", "SÁBADO", "DOMINGO"
                )[fecha.weekday()]
            )
        )
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def registrar_asistencia_manual(
    id_maestro,
    id_horario,
    fecha_hora,
    estado,
    observaciones="Asistencia registrada manualmente."
):
    """Registra manualmente una asistencia para una clase del día."""

    if estado not in ("ASISTENCIA", "RETARDO"):
        raise ValueError("El estado debe ser ASISTENCIA o RETARDO.")

    if not isinstance(fecha_hora, datetime):
        raise ValueError("La fecha y hora de asistencia no son válidas.")

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id_clase
            FROM tblClasesImpartidas
            WHERE id_maestro = %s
                AND id_horario = %s
                AND fecha >= %s
                AND fecha < %s
            LIMIT 1
            """,
            (
                id_maestro,
                id_horario,
                fecha_hora.date(),
                fecha_hora.date() + timedelta(days=1)
            )
        )

        if cursor.fetchone():
            raise ValueError("Esta clase ya tiene una asistencia registrada.")

        cursor.execute(
            """
            SELECT id_falta
            FROM tblFaltas
            WHERE id_maestro = %s
                AND id_horario = %s
                AND fecha >= %s
                AND fecha < %s
            LIMIT 1
            """,
            (
                id_maestro,
                id_horario,
                fecha_hora.date(),
                fecha_hora.date() + timedelta(days=1)
            )
        )

        if cursor.fetchone():
            raise ValueError("Esta clase ya tiene una falta registrada.")

        cursor.execute(
            """
            INSERT INTO tblClasesImpartidas (
                id_maestro,
                id_horario,
                fecha,
                hora_asistencia,
                estado,
                observaciones
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                id_maestro,
                id_horario,
                fecha_hora,
                fecha_hora,
                estado,
                observaciones
            )
        )
        id_clase = cursor.lastrowid
        conexion.commit()
        return id_clase
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def registrar_falta_manual(
    id_maestro,
    id_horario,
    fecha_hora,
    tipo,
    motivo,
    maestro_cubrio=None
):
    """Registra una falta manual, justificada o no justificada."""

    if tipo not in ("FALTA", "JUSTIFICADA"):
        raise ValueError("El tipo de falta no es válido.")

    if not isinstance(fecha_hora, datetime):
        raise ValueError("La fecha de la falta no es válida.")

    motivo = str(motivo or "").strip()
    maestro_cubrio = str(maestro_cubrio or "").strip() or None

    if not motivo:
        raise ValueError("Escribe el motivo de la falta.")

    if len(motivo) > 500:
        raise ValueError("El motivo no puede superar 500 caracteres.")

    if maestro_cubrio and len(maestro_cubrio) > 150:
        raise ValueError("El nombre del suplente no puede superar 150 caracteres.")

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No fue posible conectar con MySQL.")

    cursor = None

    try:
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT id_clase
            FROM tblClasesImpartidas
            WHERE id_maestro = %s
                AND id_horario = %s
                AND fecha >= %s
                AND fecha < %s
            LIMIT 1
            """,
            (
                id_maestro,
                id_horario,
                fecha_hora.date(),
                fecha_hora.date() + timedelta(days=1)
            )
        )
        if cursor.fetchone():
            raise ValueError("Esta clase ya tiene una asistencia registrada.")

        cursor.execute(
            """
            SELECT id_falta
            FROM tblFaltas
            WHERE id_maestro = %s
                AND id_horario = %s
                AND fecha >= %s
                AND fecha < %s
            LIMIT 1
            """,
            (
                id_maestro,
                id_horario,
                fecha_hora.date(),
                fecha_hora.date() + timedelta(days=1)
            )
        )
        if cursor.fetchone():
            raise ValueError("Esta clase ya tiene una falta registrada.")

        cursor.execute(
            """
            INSERT INTO tblFaltas (
                id_maestro,
                id_horario,
                fecha,
                tipo,
                maestro_cubrio,
                observaciones
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                id_maestro,
                id_horario,
                fecha_hora,
                tipo,
                maestro_cubrio,
                motivo
            )
        )
        id_falta = cursor.lastrowid
        conexion.commit()
        return id_falta
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def cargar_asistencias(fecha_inicio=None, fecha_fin=None):
    """
    Consulta las asistencias y retardos registrados.
    Permite filtrar por un rango de fechas.
    """

    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                ci.id_clase,
                ci.id_maestro,
                ci.id_horario,
                ci.fecha,
                ci.hora_asistencia,
                ci.estado,
                ci.observaciones,
                m.nombre,
                m.apellido,
                ma.nombre AS materia,
                ma.carrera,
                ma.cuatrimestre,
                h.dia,
                h.hora_inicio,
                h.hora_fin,
                h.turno
            FROM tblClasesImpartidas ci
            INNER JOIN tblMaestros m
                ON ci.id_maestro = m.id_maestro
            INNER JOIN tblHorarios h
                ON ci.id_horario = h.id_horario
            INNER JOIN tblMaterias ma
                ON h.id_materia = ma.id_materia
            WHERE ci.estado IN ('ASISTENCIA', 'RETARDO')
        """

        parametros = []

        if fecha_inicio:
            consulta += " AND ci.fecha >= %s"
            parametros.append(fecha_inicio)

        if fecha_fin:
            consulta += " AND ci.fecha < DATE_ADD(%s, INTERVAL 1 DAY)"
            parametros.append(fecha_fin)

        consulta += " ORDER BY ci.fecha DESC, ci.hora_asistencia DESC"

        cursor.execute(consulta, parametros)
        resultados = cursor.fetchall()

        cursor.close()

        return resultados

    except Exception as error:
        print("Error al cargar asistencias:", error)
        return []

    finally:
        if conexion:
            conexion.close()


def registrar_asistencia(
    id_maestro,
    id_horario,
    fecha,
    hora_asistencia,
    estado,
    observaciones=None
):
    """
    Registra una asistencia o retardo.
    """

    conexion = None

    try:
        if estado not in ("ASISTENCIA", "RETARDO"):
            raise ValueError("El estado debe ser ASISTENCIA o RETARDO.")

        conexion = obtener_conexion()
        cursor = conexion.cursor()

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
                id_maestro,
                id_horario,
                fecha,
                hora_asistencia,
                estado,
                observaciones
            )
        )

        conexion.commit()
        id_registro = cursor.lastrowid

        cursor.close()

        return {
            "exito": True,
            "id_clase": id_registro,
            "mensaje": "Asistencia registrada correctamente."
        }

    except Exception as error:
        if conexion:
            conexion.rollback()

        print("Error al registrar asistencia:", error)

        return {
            "exito": False,
            "id_clase": None,
            "mensaje": str(error)
        }

    finally:
        if conexion:
            conexion.close()


def actualizar_asistencia(
    id_clase,
    estado,
    hora_asistencia=None,
    observaciones=None
):
    """
    Actualiza el estado, hora y observaciones de una asistencia.
    """

    conexion = None

    try:
        if estado not in ("ASISTENCIA", "RETARDO"):
            raise ValueError("El estado debe ser ASISTENCIA o RETARDO.")

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        consulta = """
            UPDATE tblClasesImpartidas
            SET
                estado = %s,
                hora_asistencia = %s,
                observaciones = %s
            WHERE id_clase = %s
        """

        cursor.execute(
            consulta,
            (
                estado,
                hora_asistencia,
                observaciones,
                id_clase
            )
        )

        conexion.commit()
        actualizado = cursor.rowcount > 0

        cursor.close()

        return actualizado

    except Exception as error:
        if conexion:
            conexion.rollback()

        print("Error al actualizar asistencia:", error)
        return False

    finally:
        if conexion:
            conexion.close()


def eliminar_asistencia(id_clase):
    """
    Elimina un registro de asistencia.
    """

    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            DELETE FROM tblClasesImpartidas
            WHERE id_clase = %s
            """,
            (id_clase,)
        )

        conexion.commit()
        eliminado = cursor.rowcount > 0

        cursor.close()

        return eliminado

    except Exception as error:
        if conexion:
            conexion.rollback()

        print("Error al eliminar asistencia:", error)
        return False

    finally:
        if conexion:
            conexion.close()


def buscar_asistencia(id_clase):
    """
    Busca una asistencia por su identificador.
    """

    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM tblClasesImpartidas
            WHERE id_clase = %s
            """,
            (id_clase,)
        )

        resultado = cursor.fetchone()
        cursor.close()

        return resultado

    except Exception as error:
        print("Error al buscar asistencia:", error)
        return None

    finally:
        if conexion:
            conexion.close()
