
from pathlib import Path
from datetime import datetime

from Configuracion.ConexionMySQL import obtener_conexion


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

TABLA_MAESTROS = "tblMaestros"

RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_DATOS = RUTA_PROYECTO / "DatosLocales"
RUTA_ARCHIVO_MAESTROS = RUTA_DATOS / "maestros.json"


# ==========================================================
# VALIDAR IDENTIFICADOR
# ==========================================================

def es_id_maestro_valido(identificador):

    identificador = str(identificador).strip()

    if not identificador.startswith("MST-"):
        return False

    numero = identificador[4:]

    return numero.isdigit()


def convertir_id_a_numero(identificador):

    if not es_id_maestro_valido(identificador):
        raise ValueError(
            "El identificador del maestro no es válido."
        )

    return int(str(identificador).strip()[4:])


def convertir_numero_a_id(numero):

    return f"MST-{int(numero):04d}"


# ==========================================================
# PREPARAR ALMACENAMIENTO LOCAL
# ==========================================================

def preparar_almacenamiento():

    RUTA_DATOS.mkdir(
        parents=True,
        exist_ok=True
    )


# ==========================================================
# CONVERTIR REGISTRO MYSQL A DICCIONARIO
# ==========================================================

def convertir_registro_maestro(registro):

    if not registro:
        return None

    nombre = str(
        registro.get("nombre") or ""
    ).strip()

    apellidos = str(
        registro.get("apellido") or ""
    ).strip()

    if not nombre or not apellidos:
        return None

    fecha = registro.get("fecha_registro")

    if isinstance(fecha, datetime):
        fecha = fecha.strftime("%Y-%m-%d %H:%M:%S")
    elif fecha is not None:
        fecha = str(fecha)

    return {
        "id": convertir_numero_a_id(
            registro["id_maestro"]
        ),
        "nombre": nombre,
        "apellidos": apellidos,
        "activo": str(
            registro.get("estado", "")
        ).upper() == "ACTIVO",
        "fecha_registro": fecha
    }


# ==========================================================
# CARGAR MAESTROS DESDE MYSQL
# ==========================================================

def cargar_maestros():

    print("\n========== CARGA DE MAESTROS ==========")
    print("Origen: MySQL")
    print("Tabla:", TABLA_MAESTROS)

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError(
            "No fue posible conectar con MySQL."
        )

    cursor = None

    try:

        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_maestro,
                nombre,
                apellido,
                estado,
                fecha_registro
            FROM tblMaestros
            ORDER BY id_maestro ASC
        """)

        registros = cursor.fetchall()

        maestros = []

        for registro in registros:

            maestro = convertir_registro_maestro(
                registro
            )

            if maestro:
                maestros.append(maestro)

        print("Cantidad de maestros:", len(maestros))
        print("=======================================\n")

        return maestros

    except Exception as error:

        print("ERROR AL CARGAR MAESTROS:", error)
        raise

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# ==========================================================
# GUARDAR MAESTROS EN MYSQL
# ==========================================================

def guardar_maestros(maestros):

    if not isinstance(maestros, list):

        raise ValueError(
            "Los datos de maestros deben estar en una lista."
        )

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError(
            "No fue posible conectar con MySQL."
        )

    cursor = None

    try:

        cursor = conexion.cursor()

        for maestro in maestros:

            identificador = str(
                maestro.get("id", "")
            ).strip()

            numero = convertir_id_a_numero(
                identificador
            )

            nombre = str(
                maestro.get("nombre", "")
            ).strip()

            apellidos = str(
                maestro.get("apellidos", "")
            ).strip()

            activo = bool(
                maestro.get("activo", True)
            )

            if not nombre or not apellidos:
                raise ValueError(
                    f"Datos incompletos para el maestro {identificador}."
                )

            estado = (
                "ACTIVO"
                if activo
                else "INACTIVO"
            )

            cursor.execute("""
                INSERT INTO tblMaestros (
                    id_maestro,
                    nombre,
                    apellido,
                    estado
                )
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    nombre = VALUES(nombre),
                    apellido = VALUES(apellido),
                    estado = VALUES(estado)
            """, (
                numero,
                nombre,
                apellidos,
                estado
            ))

        conexion.commit()

        print(
            "Maestros guardados correctamente en MySQL."
        )

    except Exception as error:

        conexion.rollback()

        print("ERROR AL GUARDAR MAESTROS:", error)
        raise

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# ==========================================================
# GENERAR ID AUTOMÁTICO
# ==========================================================

def generar_id_maestro(maestros=None):

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError(
            "No fue posible conectar con MySQL."
        )

    cursor = None

    try:

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT COALESCE(MAX(id_maestro), 0) + 1
            FROM tblMaestros
        """)

        siguiente = cursor.fetchone()[0]

        return convertir_numero_a_id(siguiente)

    except Exception as error:

        print("ERROR AL GENERAR ID:", error)
        raise

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# ==========================================================
# REGISTRAR NUEVO MAESTRO
# ==========================================================

def registrar_maestro(nombre, apellidos):

    nombre = str(nombre).strip()
    apellidos = str(apellidos).strip()

    if not nombre or not apellidos:

        raise ValueError(
            "Debes ingresar nombre y apellidos."
        )

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError(
            "No fue posible conectar con MySQL."
        )

    cursor = None

    try:

        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO tblMaestros (
                nombre,
                apellido,
                estado
            )
            VALUES (%s, %s, %s)
        """, (
            nombre,
            apellidos,
            "ACTIVO"
        ))

        numero = cursor.lastrowid

        conexion.commit()

        identificador = convertir_numero_a_id(
            numero
        )

        maestro = {
            "id": identificador,
            "nombre": nombre,
            "apellidos": apellidos,
            "activo": True,
            "fecha_registro": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        print(
            "Maestro registrado:",
            identificador
        )

        return maestro

    except Exception as error:

        conexion.rollback()

        print("ERROR AL REGISTRAR MAESTRO:", error)
        raise

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# ==========================================================
# ACTUALIZAR MAESTRO
# ==========================================================

def actualizar_maestro(
    id_maestro,
    nombre,
    apellidos,
    activo
):

    nombre = str(nombre).strip()
    apellidos = str(apellidos).strip()

    if not nombre or not apellidos:

        raise ValueError(
            "Debes ingresar nombre y apellidos."
        )

    if not es_id_maestro_valido(id_maestro):

        raise ValueError(
            "El identificador del maestro no es válido."
        )

    numero = convertir_id_a_numero(id_maestro)

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError(
            "No fue posible conectar con MySQL."
        )

    cursor = None

    try:

        cursor = conexion.cursor(dictionary=True)

        # COMPROBAR QUE EXISTA EL MAESTRO
        cursor.execute("""
            SELECT id_maestro
            FROM tblMaestros
            WHERE id_maestro = %s
        """, (numero,))

        if not cursor.fetchone():

            raise ValueError(
                "No se encontró el maestro seleccionado."
            )

        estado = (
            "ACTIVO"
            if bool(activo)
            else "INACTIVO"
        )

        # ACTUALIZAR
        cursor.execute("""
            UPDATE tblMaestros
            SET
                nombre = %s,
                apellido = %s,
                estado = %s
            WHERE id_maestro = %s
        """, (
            nombre,
            apellidos,
            estado,
            numero
        ))

        # RECUPERAR LOS DATOS ACTUALIZADOS
        cursor.execute("""
            SELECT
                id_maestro,
                nombre,
                apellido,
                estado,
                fecha_registro
            FROM tblMaestros
            WHERE id_maestro = %s
        """, (numero,))

        registro = cursor.fetchone()

        conexion.commit()

        maestro = convertir_registro_maestro(
            registro
        )

        print(
            "Maestro actualizado:",
            id_maestro
        )

        return maestro

    except Exception as error:

        conexion.rollback()

        print("ERROR AL ACTUALIZAR MAESTRO:", error)
        raise

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# ==========================================================
# BUSCAR MAESTRO POR ID
# ==========================================================

def buscar_maestro(id_maestro):

    if not es_id_maestro_valido(id_maestro):
        return None

    numero = convertir_id_a_numero(
        id_maestro
    )

    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError(
            "No fue posible conectar con MySQL."
        )

    cursor = None

    try:

        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_maestro,
                nombre,
                apellido,
                estado,
                fecha_registro
            FROM tblMaestros
            WHERE id_maestro = %s
        """, (numero,))

        registro = cursor.fetchone()

        return convertir_registro_maestro(
            registro
        )

    except Exception as error:

        print("ERROR AL BUSCAR MAESTRO:", error)
        raise

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# ==========================================================
# MIGRAR MAESTROS LOCALES A MYSQL
# ==========================================================

def migrar_maestros_locales_a_mysql():

    preparar_almacenamiento()

    print("\n========== MIGRACIÓN A MYSQL ==========")

    try:

        import json

        if not RUTA_ARCHIVO_MAESTROS.exists():

            print(
                "No existe el archivo maestros.json."
            )

            return {
                "migrados": 0,
                "omitidos": 0,
                "total_locales": 0
            }

        with open(
            RUTA_ARCHIVO_MAESTROS,
            "r",
            encoding="utf-8"
        ) as archivo:

            maestros_locales = json.load(archivo)

        if not isinstance(maestros_locales, list):

            raise ValueError(
                "El archivo maestros.json no contiene una lista."
            )

        conexion = obtener_conexion()

        if conexion is None:
            raise ConnectionError(
                "No fue posible conectar con MySQL."
            )

        cursor = None

        try:

            cursor = conexion.cursor()

            migrados = 0
            omitidos = 0

            for maestro in maestros_locales:

                identificador = str(
                    maestro.get("id", "")
                ).strip()

                if not es_id_maestro_valido(
                    identificador
                ):

                    omitidos += 1
                    continue

                numero = convertir_id_a_numero(
                    identificador
                )

                nombre = str(
                    maestro.get("nombre", "")
                ).strip()

                apellidos = str(
                    maestro.get("apellidos", "")
                ).strip()

                if not nombre or not apellidos:

                    omitidos += 1
                    continue

                cursor.execute("""
                    SELECT id_maestro
                    FROM tblMaestros
                    WHERE id_maestro = %s
                """, (numero,))

                if cursor.fetchone():

                    omitidos += 1
                    continue

                estado = (
                    "ACTIVO"
                    if maestro.get("activo", True)
                    else "INACTIVO"
                )

                cursor.execute("""
                    INSERT INTO tblMaestros (
                        id_maestro,
                        nombre,
                        apellido,
                        estado
                    )
                    VALUES (%s, %s, %s, %s)
                """, (
                    numero,
                    nombre,
                    apellidos,
                    estado
                ))

                migrados += 1

            conexion.commit()

        except Exception:

            conexion.rollback()
            raise

        finally:

            if cursor:
                cursor.close()

            conexion.close()

        resultado = {
            "migrados": migrados,
            "omitidos": omitidos,
            "total_locales": len(maestros_locales)
        }

        print("Migración terminada.")
        print("Maestros migrados:", migrados)
        print("Maestros omitidos:", omitidos)
        print("=======================================\n")

        return resultado

    except Exception as error:

        print("ERROR EN LA MIGRACIÓN:", error)
        raise
