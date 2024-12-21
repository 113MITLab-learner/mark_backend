# api/controllers/image_processing.py

import requests
import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def fetch_image_from_esp32_cam(img_url='http://172.20.10.2/'):
    """
    從 ESP32-CAM 獲取影像。
    """
    try:
        resp = requests.get(img_url, timeout=5)
        img_arr = np.asarray(bytearray(resp.content), dtype=np.uint8)
        image = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        if image is None:
            print('影像解碼失敗')
            return None
        return image
    except Exception as e:
        print(f'獲取影像時出現錯誤: {e}')
        return None

def process_image_with_mediapipe(image):
    """
    使用 Mediapipe 處理影像，返回處理後的影像。
    """
    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5
    ) as hands:
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    return image
