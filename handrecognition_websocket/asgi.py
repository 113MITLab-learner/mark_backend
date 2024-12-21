import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application


# 設置 Django 設定模組
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'handrecognition_websocket.settings')

# 初始化 Django ASGI 應用
django_asgi_app = get_asgi_application()

import api.routing

# 定義 ASGI 應用
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    ),
})
