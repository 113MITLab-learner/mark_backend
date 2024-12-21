# api/urls.py

from django.urls import path
from . import views
from .controllers.user_controller import user_profile

urlpatterns = [
    path('set_frequency/', views.set_frequency_view, name='set_frequency'),
    path('toggle_image_display/', views.image_toggle_view, name='toggle_image_display'),
    path('toggle_detection/', views.detection_toggle_view, name='toggle_detection'),
    path('take-photo/', views.camera_take_photo_view, name='take_photo'),
    path('user-photos/', views.get_user_photos_view, name='get_user_photos'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('user-profile/', user_profile, name='user_profile'),
        path('batch_label_photos/', views.batch_label_photos_view, name='batch_label_photos'),
    path('batch_delete_photos/', views.batch_delete_photos_view, name='batch_delete_photos'),
]
