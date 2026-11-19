
# ==========================================================
# SERVICIO DE ASISTENCIAS
# Archivo: Servicios/ServicioAsistencias.py
# Base de datos: MySQL - ARKOS
# ==========================================================

from Configuracion.ConexionMySQL import obtener_conexion
from datetime import datetime


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
            consulta += " AND DATE(ci.fecha) >= %s"
            parametros.append(fecha_inicio)

        if fecha_fin:
            consulta += " AND DATE(ci.fecha) <= %s"
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
