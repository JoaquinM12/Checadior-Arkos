
import cv2

from Controladores.ControlReconocimiento import reconocer_imagen


camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camara.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

contador = 0
resultado = {
    "reconocido": False,
    "mensaje": "Buscando rostro..."
}

print("Cámara iniciada. Presiona Q para salir.")

while True:

    correcto, frame = camara.read()

    if not correcto:
        print("No se pudo obtener imagen de la cámara.")
        break

    contador += 1

    # Procesar cada 15 cuadros para reducir carga.
    if contador % 15 == 0:

        resultado = reconocer_imagen(frame)

    # Mostrar resultado.
    if resultado.get("reconocido"):

        texto = resultado["nombre"]
        color = (0, 255, 0)

    else:

        texto = resultado.get(
            "mensaje",
            "Buscando rostro..."
        )
        color = (0, 0, 255)

    cv2.putText(
        frame,
        texto[:55],
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2
    )

    cv2.imshow(
        "ARKOS - Reconocimiento Facial",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camara.release()
cv2.destroyAllWindows()
