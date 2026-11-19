
import mysql.connector
from mysql.connector import Error


def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            port=3306,
            database="arkos",
            user="arkos_app",
            password="Arkos2026_Segura"
        )

        if conexion.is_connected():
            return conexion

    except Error as error:
        print(f"Error al conectar con MySQL: {error}")

    return None


def probar_conexion():
    conexion = obtener_conexion()

    if conexion is None:
        print("No fue posible conectar con MySQL.")
        return False

    cursor = None

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT DATABASE(), VERSION()")

        resultado = cursor.fetchone()

        print("================================")
        print("ARKOS - CONEXION MYSQL EXITOSA")
        print("================================")
        print(f"Base de datos: {resultado[0]}")
        print(f"Version MySQL: {resultado[1]}")

        return True

    except Error as error:
        print(f"Error al consultar MySQL: {error}")
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()
