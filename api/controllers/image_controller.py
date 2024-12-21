# api/controllers/image_controller.py

from django.http import JsonResponse
from rest_framework.decorators import api_view
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# 使用全局變數來保存狀態
_image_display_on = True

def is_image_display_on():
    global _image_display_on
    return _image_display_on

@api_view(['POST'])
def toggle_image_display(request):
    global _image_display_on
    action = request.data.get('action')
    if action == 'on':
        _image_display_on = True
    elif action == 'off':
        _image_display_on = False
    else:
        return JsonResponse({"error": "Invalid action"}, status=400)
    
    # 通知 WebSocket 消費者狀態更新
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "image_display_group",
        {"type": "toggle.image_display", "is_display_on": _image_display_on}
    )
    
    return JsonResponse({"is_display_on": _image_display_on})
