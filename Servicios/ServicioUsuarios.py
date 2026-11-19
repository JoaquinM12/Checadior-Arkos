"""Operaciones de usuarios y autenticación para ARKOS CHECADOR."""

import hashlib
import hmac
import secrets

from Configuracion.ConexionMySQL import obtener_conexion


ROLES = ("Administrador", "Director", "Control Escolar", "Consulta")
ITERACIONES = 310000


def hash_password(password):
    sal = secrets.token_bytes(16)
    derivado = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), sal, ITERACIONES
    )
    return f"pbkdf2_sha256${ITERACIONES}${sal.hex()}${derivado.hex()}"


def verificar_password(password, almacenado):
    try:
        algoritmo, iteraciones, sal_hex, hash_hex = almacenado.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        derivado = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(sal_hex),
            int(iteraciones)
        )
        return hmac.compare_digest(derivado.hex(), hash_hex)
    except (AttributeError, ValueError, TypeError):
        return False


def asegurar_tabla_usuarios(conexion):
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tblUsuarios (
                idUsuario INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(120) NOT NULL,
                usuario VARCHAR(80) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(40) NOT NULL,
                activo TINYINT(1) NOT NULL DEFAULT 1,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conexion.commit()
        cursor.execute("SELECT COUNT(*) FROM tblUsuarios")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO tblUsuarios "
                "(nombre, usuario, password_hash, rol, activo) "
                "VALUES (%s, %s, %s, %s, 1)",
                ("Administrador", "admin", hash_password("Arkos2026!"),
                 "Administrador")
            )
            conexion.commit()
    finally:
        cursor.close()


def autenticar_usuario(usuario, password):
    conexion = obtener_conexion()
    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")
    cursor = None
    try:
        asegurar_tabla_usuarios(conexion)
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT idUsuario, nombre, usuario, password_hash, rol, activo "
            "FROM tblUsuarios WHERE usuario = %s LIMIT 1",
            (usuario.strip(),)
        )
        fila = cursor.fetchone()
        if not fila or not fila[5] or not verificar_password(password, fila[3]):
            return None
        return {"id": fila[0], "nombre": fila[1], "usuario": fila[2],
                "rol": fila[4]}
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def listar_usuarios():
    conexion = obtener_conexion()
    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")
    cursor = None
    try:
        asegurar_tabla_usuarios(conexion)
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT idUsuario, nombre, usuario, rol, activo "
            "FROM tblUsuarios ORDER BY nombre, usuario"
        )
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def guardar_usuario(nombre, usuario, rol, password=None, id_usuario=None):
    nombre, usuario = nombre.strip(), usuario.strip()
    if not nombre or not usuario or rol not in ROLES:
        raise ValueError("Completa nombre, usuario y un rol válido.")
    if password is not None and len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")

    conexion = obtener_conexion()
    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")
    cursor = None
    try:
        asegurar_tabla_usuarios(conexion)
        cursor = conexion.cursor()
        if id_usuario is None:
            if not password:
                raise ValueError("La contraseña es obligatoria para crear la cuenta.")
            cursor.execute(
                "INSERT INTO tblUsuarios "
                "(nombre, usuario, password_hash, rol, activo) "
                "VALUES (%s, %s, %s, %s, 1)",
                (nombre, usuario, hash_password(password), rol)
            )
        else:
            cursor.execute(
                "UPDATE tblUsuarios SET nombre=%s, usuario=%s, rol=%s "
                "WHERE idUsuario=%s",
                (nombre, usuario, rol, id_usuario)
            )
            if password:
                cursor.execute(
                    "UPDATE tblUsuarios SET password_hash=%s WHERE idUsuario=%s",
                    (hash_password(password), id_usuario)
                )
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def establecer_estado_usuario(id_usuario, activo):
    conexion = obtener_conexion()
    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")
    cursor = None
    try:
        asegurar_tabla_usuarios(conexion)
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM tblUsuarios "
            "WHERE rol='Administrador' AND activo=1"
        )
        administradores_activos = cursor.fetchone()[0]
        cursor.execute(
            "SELECT rol, activo FROM tblUsuarios WHERE idUsuario=%s",
            (id_usuario,)
        )
        fila = cursor.fetchone()
        if not fila:
            raise ValueError("No se encontró la cuenta seleccionada.")
        if not activo and fila[0] == "Administrador" and fila[1] and administradores_activos <= 1:
            raise ValueError("No puedes desactivar al último administrador activo.")
        cursor.execute(
            "UPDATE tblUsuarios SET activo=%s WHERE idUsuario=%s",
            (1 if activo else 0, id_usuario)
        )
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        conexion.close()
