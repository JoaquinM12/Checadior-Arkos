
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget
)

from Vistas.VisLogin import VisLogin
from Vistas.VisInicio import VisInicio


class ArkosChecador(QMainWindow):

    def __init__(self):
        super().__init__()

        # =====================================
        # CONFIGURACIÓN DE LA VENTANA
        # =====================================

        self.setWindowTitle("ARKOS CHECADOR")
        self.resize(1250, 780)
        self.setMinimumSize(1050, 650)

        # =====================================
        # CONTENEDOR PRINCIPAL
        # =====================================

        self.contenedor = QStackedWidget()
        self.setCentralWidget(self.contenedor)

        # =====================================
        # CREAR PANTALLAS
        # =====================================

        self.login = VisLogin()
        self.inicio = VisInicio()

        self.contenedor.addWidget(self.login)
        self.contenedor.addWidget(self.inicio)

        # =====================================
        # CONEXIONES
        # =====================================

        self.login.login_exitoso.connect(
            self.mostrar_inicio
        )

        self.inicio.cerrar_sesion_solicitado.connect(
            self.mostrar_login
        )

        # Mostrar login al iniciar
        self.mostrar_login()

    # =====================================
    # MOSTRAR LOGIN
    # =====================================

    def mostrar_login(self):

        # Regresar a Inicio dentro del menú
        self.inicio.paginas.setCurrentIndex(0)

        self.contenedor.setCurrentWidget(
            self.login
        )

        self.login.txt_password.clear()
        self.login.txt_usuario.setFocus()

    # =====================================
    # MOSTRAR PANEL PRINCIPAL
    # =====================================

    def mostrar_inicio(self):

        self.contenedor.setCurrentWidget(
            self.inicio
        )


# =========================================
# EJECUTAR APLICACIÓN
# =========================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    ventana = ArkosChecador()
    ventana.show()

    sys.exit(app.exec())
