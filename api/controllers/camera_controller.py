# api/controllers/camera_controller.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.base import ContentFile
from django.conf import settings
from ..models import Photo
import cv2
import time
from .image_processing import fetch_image_from_esp32_cam, process_image_with_mediapipe
from .image_controller import is_image_display_on
from .detection_controller import is_detection_on

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def take_photo(request):
    try:
        if not is_image_display_on():
            return Response({"error": "影像顯示已關閉，無法拍照"}, status=400)
        
        # 獲取影像
        image = fetch_image_from_esp32_cam()
        if image is None:
            return Response({"error": "無法從攝像頭獲取影像"}, status=500)
        
        if is_detection_on():
            # 使用 Mediapipe 處理影像
            image = process_image_with_mediapipe(image)
        
        # 將處理後的影像編碼為 JPEG
        ret, buffer = cv2.imencode('.jpg', image)
        if not ret:
            return Response({"error": "影像編碼失敗"}, status=500)
        
        img_bytes = buffer.tobytes()
        
        # 保存圖片到 Photo 模型
        img_name = f"photo_{request.user.id}_{int(time.time())}.jpg"
        img_data = ContentFile(img_bytes, name=img_name)
        photo = Photo.objects.create(user=request.user, image=img_data)
        
        return Response({
            "message": "Photo taken and saved successfully",
            "image_url": request.build_absolute_uri(photo.image.url)
        }, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
