
import json
from pathlib import Path
from datetime import datetime


# =====================================
# RUTAS DEL ALMACENAMIENTO
# =====================================

RUTA_PROYECTO = Path(__file__).resolve().parent.parent

RUTA_DATOS = RUTA_PROYECTO / "DatosLocales"

RUTA_MAESTROS = RUTA_DATOS / "maestros.json"


# =====================================
# PREPARAR ALMACENAMIENTO
# =====================================

def preparar_almacenamiento():

    RUTA_DATOS.mkdir(
        parents=True,
        exist_ok=True
    )

    if not RUTA_MAESTROS.exists():

        with open(
            RUTA_MAESTROS,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                [],
                archivo,
                ensure_ascii=False,
                indent=4
            )


# =====================================
# CARGAR MAESTROS
# =====================================

def cargar_maestros():

    preparar_almacenamiento()

    print("\n========== CARGA DE MAESTROS ==========")
    print("Archivo utilizado:", RUTA_MAESTROS)

    try:

        with open(
            RUTA_MAESTROS,
            "r",
            encoding="utf-8"
        ) as archivo:

            datos = json.load(archivo)

        if not isinstance(datos, list):
            raise ValueError(
                "El archivo no contiene una lista de maestros."
            )

        print("Datos encontrados:", datos)
        print("Cantidad de maestros:", len(datos))
        print("=======================================\n")

        return datos

    except json.JSONDecodeError as error:

        raise ValueError(
            "El archivo maestros.json tiene un formato incorrecto."
        ) from error


# =====================================
# GUARDAR MAESTROS
# =====================================

def guardar_maestros(maestros):

    if not isinstance(maestros, list):
        raise ValueError(
            "Los datos de maestros deben estar en una lista."
        )

    preparar_almacenamiento()

    archivo_temporal = RUTA_MAESTROS.with_suffix(".tmp")

    try:

        with open(
            archivo_temporal,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                maestros,
                archivo,
                ensure_ascii=False,
                indent=4
            )

        archivo_temporal.replace(RUTA_MAESTROS)

    except Exception:

        if archivo_temporal.exists():
            archivo_temporal.unlink()

        raise


# =====================================
# GENERAR ID AUTOMÁTICO
# =====================================

def generar_id_maestro(maestros=None):

    if maestros is None:
        maestros = cargar_maestros()

    numeros = []

    for maestro in maestros:

        identificador = str(
            maestro.get("id", "")
        ).strip()

        if identificador.startswith("MST-"):

            try:

                numero = int(
                    identificador.split("-")[1]
                )

                numeros.append(numero)

            except (ValueError, IndexError):
                continue

    siguiente = max(numeros, default=0) + 1

    return f"MST-{siguiente:04d}"


# =====================================
# REGISTRAR NUEVO MAESTRO
# =====================================

def registrar_maestro(nombre, apellidos):

    nombre = nombre.strip()
    apellidos = apellidos.strip()

    if not nombre or not apellidos:

        raise ValueError(
            "Debes ingresar nombre y apellidos."
        )

    maestros = cargar_maestros()

    nuevo_maestro = {

        "id": generar_id_maestro(maestros),

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


# =====================================
# ACTUALIZAR MAESTRO
# =====================================

def actualizar_maestro(
    id_maestro,
    nombre,
    apellidos,
    activo
):

    nombre = nombre.strip()
    apellidos = apellidos.strip()

    if not nombre or not apellidos:

        raise ValueError(
            "Debes ingresar nombre y apellidos."
        )

    maestros = cargar_maestros()

    for maestro in maestros:

        if maestro.get("id") == id_maestro:

            maestro["nombre"] = nombre

            maestro["apellidos"] = apellidos

            maestro["activo"] = bool(activo)

            guardar_maestros(maestros)

            return maestro

    raise ValueError(
        "No se encontró el maestro seleccionado."
    )


# =====================================
# BUSCAR MAESTRO POR ID
# =====================================

def buscar_maestro(id_maestro):

    maestros = cargar_maestros()

    for maestro in maestros:

        if maestro.get("id") == id_maestro:
            return maestro

    return None
