"""Estilo global para ventanas emergentes de ARKOS CHECADOR."""

ESTILO_DIALOGOS = """
    QMessageBox, QDialog, QInputDialog, QFileDialog {
        background-color: #F4F7FB;
        color: #1B2E43;
        font-family: "Segoe UI";
        font-size: 9pt;
    }

    QMessageBox {
        min-width: 290px;
        max-width: 380px;
    }

    QMessageBox QLabel {
        background: transparent;
        color: #20384F;
        font-size: 9pt;
        min-width: 205px;
        max-width: 285px;
    }

    QDialog QLabel {
        background: transparent;
        color: #20384F;
        font-size: 10pt;
    }

    QDialog QLabel#tituloDialogo {
        color: #0A2F50;
        font-size: 15pt;
        font-weight: 800;
    }

    QDialog QLineEdit,
    QDialog QComboBox,
    QDialog QSpinBox,
    QInputDialog QLineEdit,
    QFileDialog QLineEdit,
    QFileDialog QComboBox {
        background: #FFFFFF;
        color: #18334D;
        border: 1px solid #CFDCE8;
        border-radius: 8px;
        padding: 6px 9px;
        min-height: 21px;
        selection-background-color: #D5E8F7;
    }

    QDialog QLineEdit:focus,
    QDialog QComboBox:focus,
    QDialog QSpinBox:focus,
    QInputDialog QLineEdit:focus,
    QFileDialog QLineEdit:focus {
        border: 1px solid #2877B7;
        background: #FFFFFF;
    }

    QMessageBox QPushButton,
    QDialogButtonBox QPushButton,
    QDialog QPushButton,
    QFileDialog QPushButton {
        min-width: 74px;
        min-height: 26px;
        padding: 5px 12px;
        font-size: 9pt;
        border: 1px solid #D5E1EB;
        border-radius: 8px;
        background: #E9EFF4;
        color: #1B2E43;
        font-weight: 700;
    }

    QMessageBox QPushButton:hover,
    QDialogButtonBox QPushButton:hover,
    QDialog QPushButton:hover,
    QFileDialog QPushButton:hover {
        background: #DDE6ED;
        border-color: #B9C8D5;
        color: #142B40;
    }

    QMessageBox QPushButton:default,
    QDialogButtonBox QPushButton:default {
        background: #DCE5EC;
        color: #172B3D;
        border-color: #AEBECC;
        font-weight: 800;
    }

    QMessageBox QPushButton:default:hover,
    QDialogButtonBox QPushButton:default:hover {
        background: #CFDCE6;
        color: #10283C;
        border-color: #9EAFBE;
    }

    QMessageBox QPushButton:pressed,
    QDialogButtonBox QPushButton:pressed,
    QDialog QPushButton:pressed,
    QFileDialog QPushButton:pressed {
        background: #D2E1EE;
    }

    QMessageBox QPushButton:disabled,
    QDialogButtonBox QPushButton:disabled,
    QDialog QPushButton:disabled,
    QFileDialog QPushButton:disabled {
        background: #E7EDF3;
        color: #9AA9B7;
        border-color: #E0E7EE;
    }
"""



from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QMessageBox


class TraductorBotonesMensaje(QObject):
    """Traduce los botones estándar de los QMessageBox al español."""

    ETIQUETAS = {
        QMessageBox.Yes: "Sí",
        QMessageBox.No: "No",
        QMessageBox.Ok: "Aceptar",
        QMessageBox.Cancel: "Cancelar",
        QMessageBox.Close: "Cerrar",
        QMessageBox.Save: "Guardar",
        QMessageBox.SaveAll: "Guardar todo",
        QMessageBox.Open: "Abrir",
        QMessageBox.Discard: "Descartar",
        QMessageBox.Apply: "Aplicar",
        QMessageBox.Reset: "Restablecer",
        QMessageBox.RestoreDefaults: "Valores iniciales",
        QMessageBox.Help: "Ayuda",
        QMessageBox.Retry: "Reintentar",
        QMessageBox.Ignore: "Ignorar",
        QMessageBox.Abort: "Cancelar",
        QMessageBox.YesToAll: "Sí a todo",
        QMessageBox.NoToAll: "No a todo",
    }

    def eventFilter(self, objeto, evento):
        if evento.type() == QEvent.Show and isinstance(objeto, QMessageBox):
            for boton in objeto.buttons():
                estandar = objeto.standardButton(boton)
                etiqueta = self.ETIQUETAS.get(estandar)
                if etiqueta:
                    boton.setText(etiqueta)
        return super().eventFilter(objeto, evento)
