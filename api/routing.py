# api/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/handrecognition/', consumers.HandRecognitionConsumer.as_asgi()),
]
