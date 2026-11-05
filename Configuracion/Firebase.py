from pathlib import Path
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore


# ==========================================================
# CONFIGURACIÓN DE FIREBASE
# ==========================================================

RUTA_CREDENCIALES = (
    Path(__file__).resolve().parent
    / "firebase-credentials.json"
)


# ==========================================================
# VERIFICAR CREDENCIALES
# ==========================================================

if not RUTA_CREDENCIALES.exists():
    raise FileNotFoundError(
        "No se encontró el archivo de credenciales de Firebase.\n"
        f"Ruta esperada: {RUTA_CREDENCIALES}"
    )


# ==========================================================
# INICIALIZAR FIREBASE
# ==========================================================

if not firebase_admin._apps:

    credenciales = credentials.Certificate(
        str(RUTA_CREDENCIALES)
    )

    firebase_admin.initialize_app(credenciales)


# ==========================================================
# CONEXIÓN CON CLOUD FIRESTORE
# ==========================================================

db = firestore.client()


# ==========================================================
# VERIFICAR CONEXIÓN
# ==========================================================

print("\n======================================")
print(" FIREBASE INICIALIZADO CORRECTAMENTE")
print(" CLOUD FIRESTORE DISPONIBLE")
print("======================================")

print("PROYECTO FIREBASE:", db.project)
print("BASE DE DATOS: (default)")
print("COLECCIÓN DE HORARIOS: tblHorarios")

print("======================================\n")