# api/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import base64
import cv2
import numpy as np
import mediapipe as mp
import requests
from .controllers.image_controller import is_image_display_on  # 假設有這個變數
from .controllers.detection_controller import is_detection_on  # 假設有這個變數
from .controllers.frequency_controller import get_current_frequency
from .controllers.image_processing import fetch_image_from_esp32_cam, process_image_with_mediapipe

class HandRecognitionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.is_display_on = True
        self.is_detection_on = True
        print("WebSocket 已連接")  # 調試訊息
        await self.accept()
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5
        )
        self.is_running = True
        self.sleep_time = get_current_frequency()  # 使用控制器獲取當前頻率

        # 加入頻率組以接收頻率更新
        await self.channel_layer.group_add("frequency_group", self.channel_name)
        await self.channel_layer.group_add("detection_group", self.channel_name)
        await self.channel_layer.group_add("image_display_group", self.channel_name)

        # 啟動背景任務來持續抓取並處理圖像
        self.task = asyncio.create_task(self.send_processed_images())
        await self.accept()

    async def disconnect(self, close_code):
        print(f"WebSocket 已斷開，代碼: {close_code}")  # 調試訊息
        self.is_running = False
        self.task.cancel()
        self.hands.close()

        # 從頻率組中移除
        await self.channel_layer.group_discard("frequency_group", self.channel_name)

    async def update_frequency(self, event):
        """
        接收頻率更新的事件。
        """
        new_frequency = event.get("frequency", 0.3)
        print(f"頻率更新為: {new_frequency} 秒")
        self.sleep_time = new_frequency

    async def toggle_image_display(self, event):
        """
        接收影像顯示開關的事件。
        """
        self.is_display_on = event.get("is_display_on", True)
        print(f"影像顯示狀態更新為: {self.is_display_on}")

    async def toggle_detection(self, event):
        """
        接收 Mediapipe 偵測開關的事件。
        """
        self.is_detection_on = event.get("is_detection_on", True)
        print(f"Mediapipe 偵測狀態更新為: {self.is_detection_on}")

    async def send_processed_images(self):
        while self.is_running:
            try:
                if self.is_display_on:
                    # 獲取影像
                    image = fetch_image_from_esp32_cam()
                    if image is not None:
                        if self.is_detection_on:
                            # 使用 Mediapipe 處理影像
                            image = process_image_with_mediapipe(image)
                        # 編碼並發送影像
                        ret, buffer = cv2.imencode('.jpg', image)
                        img_base64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
                        await self.send(text_data=json.dumps({'image': img_base64}))
                    else:
                        await self.send(text_data=json.dumps({'image': None, 'message': '無法獲取影像'}))
                else:
                    await self.send(text_data=json.dumps({'image': None, 'message': '影像顯示已關閉'}))
                await asyncio.sleep(self.sleep_time)
            except Exception as e:
                print(f'處理影像時出現錯誤: {e}')
                await asyncio.sleep(self.sleep_time)
