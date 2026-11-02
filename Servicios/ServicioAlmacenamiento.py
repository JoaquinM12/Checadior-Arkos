import json
from pathlib import Path
from datetime import datetime


# Rutas del proyecto
RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_DATOS = RUTA_PROYECTO / "DatosLocales"
RUTA_MAESTROS = RUTA_DATOS / "maestros.json"


def preparar_almacenamiento():

    RUTA_DATOS.mkdir(parents=True, exist_ok=True)

    if not RUTA_MAESTROS.exists():
        with open(RUTA_MAESTROS, "w", encoding="utf-8") as archivo:
            json.dump([], archivo, ensure_ascii=False, indent=4)


def cargar_maestros():

    preparar_almacenamiento()

    print("\n========== CARGA DE MAESTROS ==========")
    print("Archivo utilizado:", RUTA_MAESTROS)

    try:
        with open(RUTA_MAESTROS, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        if not isinstance(datos, list):
            raise ValueError("El archivo no contiene una lista.")

        print("Datos encontrados:", datos)
        print("Cantidad de maestros:", len(datos))
        print("=======================================\n")

        return datos

    except json.JSONDecodeError as error:
        raise ValueError(
            "El archivo maestros.json tiene un formato incorrecto."
        ) from error


def guardar_maestros(maestros):

    preparar_almacenamiento()

    archivo_temporal = RUTA_MAESTROS.with_suffix(".tmp")

    with open(archivo_temporal, "w", encoding="utf-8") as archivo:
        json.dump(
            maestros,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    archivo_temporal.replace(RUTA_MAESTROS)


def generar_id_maestro():

    maestros = cargar_maestros()

    numeros = []

    for maestro in maestros:
        identificador = maestro.get("id", "")

        if identificador.startswith("MST-"):
            try:
                numeros.append(int(identificador.split("-")[1]))
            except (ValueError, IndexError):
                continue

    siguiente = max(numeros, default=0) + 1

    return f"MST-{siguiente:04d}"


def registrar_maestro(nombre, apellidos):

    nombre = nombre.strip()
    apellidos = apellidos.strip()

    if not nombre or not apellidos:
        raise ValueError("Debes ingresar nombre y apellidos.")

    maestros = cargar_maestros()

    nuevo_maestro = {
        "id": generar_id_maestro(),
        "nombre": nombre,
        "apellidos": apellidos,
        "activo": True,
        "fecha_registro": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    maestros.append(nuevo_maestro)

    guardar_maestros(maestros)

    return nuevo_maestro