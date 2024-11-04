import cv2
import mediapipe as mp
import asyncio
import websockets
import json

# Configuración de MediaPipe para detección de manos
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_drawing = mp.solutions.drawing_utils

# Función para contar los dedos levantados
def contar_dedos(hand_landmarks):
    dedos_arriba = 0
    dedos = {'thumb': 4, 'index': 8, 'middle': 12, 'ring': 16, 'pinky': 20}
    tip_ids = [dedos['thumb'], dedos['index'], dedos['middle'], dedos['ring'], dedos['pinky']]
    dip_ids = [3, 6, 10, 14, 18]

    # Pulgar
    if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[dip_ids[0]].x:
        dedos_arriba += 1

    # Otros dedos
    for tip_id, dip_id in zip(tip_ids[1:], dip_ids[1:]):
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[dip_id].y:
            dedos_arriba += 1

    return dedos_arriba

async def enviar_dedos(websocket):
    detener = False
    async for message in websocket:
        if message == "start":
            detener = False
            cap = cv2.VideoCapture(0)
            print("Prueba iniciada.")
            while cap.isOpened() and not detener:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                resultado = hands.process(frame_rgb)
                dedos_levantados = 0

                if resultado.multi_hand_landmarks:
                    for hand_landmarks in resultado.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        dedos_levantados = contar_dedos(hand_landmarks)

                # Enviar el número de dedos detectados al cliente
                data = json.dumps({"dedos": dedos_levantados})
                await websocket.send(data)
                await asyncio.sleep(0.1)  # Intervalo para enviar los datos

            cap.release()
            print("Prueba detenida.")
        elif message == "stop":
            detener = True

async def main():
    async with websockets.serve(enviar_dedos, "localhost", 4001):
        print("Servidor WebSocket iniciado en ws://localhost:4001")
        await asyncio.Future()  # Mantener el servidor corriendo

asyncio.run(main())