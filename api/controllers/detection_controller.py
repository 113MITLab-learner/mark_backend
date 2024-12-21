# api/controllers/detection_controller.py

from django.http import JsonResponse
from rest_framework.decorators import api_view
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

_detection_on = True

def is_detection_on():
    global _detection_on
    return _detection_on

@api_view(['POST'])
def toggle_detection(request):
    global _detection_on
    action = request.data.get('action')
    if action == 'on':
        _detection_on = True
    elif action == 'off':
        _detection_on = False
    else:
        return JsonResponse({"error": "Invalid action"}, status=400)
    
    # 通知 WebSocket 消費者狀態更新
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "detection_group",
        {"type": "toggle.detection", "is_detection_on": _detection_on}
    )
    
    return JsonResponse({"is_detection_on": _detection_on})
