# api/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .controllers.frequency_controller import set_frequency
from .controllers.image_controller import toggle_image_display
from .controllers.detection_controller import toggle_detection
from .controllers.camera_controller import take_photo
from .controllers.photo_controller import get_user_photos, batch_label_photos, batch_delete_photos

@csrf_exempt
def set_frequency_view(request):
    return set_frequency(request)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        if username and password and email:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            return Response({"message": "User created successfully"}, status=201)
        return Response({"message": "Invalid data"}, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({"message": "Invalid credentials"}, status=401)

# 直接將控制器函數映射為視圖
image_toggle_view = toggle_image_display
detection_toggle_view = toggle_detection
camera_take_photo_view = take_photo
get_user_photos_view = get_user_photos
batch_label_photos_view = batch_label_photos
batch_delete_photos_view = batch_delete_photos