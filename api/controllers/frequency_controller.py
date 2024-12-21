# api/controllers/frequency_controller.py

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

current_frequency = 0.3  # 默認頻率

@csrf_exempt
def set_frequency(request):
    global current_frequency
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_frequency = data.get("frequency")
            if isinstance(new_frequency, (int, float)) and new_frequency > 0:
                current_frequency = new_frequency
                # 通知 WebSocket 更新頻率
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "frequency_group",
                    {
                        "type": "update_frequency",
                        "frequency": current_frequency,
                    },
                )
                return JsonResponse({"status": "success", "frequency": current_frequency})
            else:
                return JsonResponse({"status": "error", "message": "Invalid frequency value"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

def get_current_frequency():
    return current_frequency
