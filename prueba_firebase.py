
from Configuracion.Firebase import db


def probar_firebase():
    print("\nIniciando prueba de Firestore...")

    referencia = db.collection("tblPruebasConexion").document(
        "prueba_python"
    )

    datos = {
        "mensaje": "Conexion desde Python",
        "estado": "Correcto"
    }

    try:
        # ESCRIBIR
        referencia.set(datos)
        print("1. Escritura: CORRECTA")

        # LEER
        documento = referencia.get()

        if documento.exists:
            print("2. Lectura: CORRECTA")
            print("Datos recibidos:", documento.to_dict())
        else:
            print("2. Lectura: NO SE ENCONTRO EL DOCUMENTO")
            return

        # ELIMINAR DOCUMENTO DE PRUEBA
        referencia.delete()
        print("3. Limpieza: CORRECTA")

        print("\nFIRESTORE FUNCIONA CORRECTAMENTE")

    except Exception as error:
        print("\nERROR AL PROBAR FIRESTORE:")
        print(error)


if __name__ == "__main__":
    probar_firebase()
