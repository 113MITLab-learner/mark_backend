# api/models.py
from django.db import models
from django.contrib.auth.models import User
import os

AVAILABLE_LABELS = [
    "thumb_up",
    "finger_count_1",
    "finger_count_2",
    "finger_count_3",
    "finger_count_4",
    "finger_count_5",
    "ok_sign",
    "peace_sign",
    "fist",
    "palm",
    "pointing",
    "love_sign",
    "other",
]

def user_photo_path(instance, filename):
    return f'photos/user_{instance.user.id}/{filename}'

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_photo_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_image = models.ImageField(upload_to=user_photo_path, null=True, blank=True)
    label = models.CharField(max_length=255, blank=True, null=True)  # 使用逗號分隔的標籤字串

    def __str__(self):
        return f"{self.user.username} - {self.uploaded_at}"

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        if self.processed_image:
            if os.path.isfile(self.processed_image.path):
                os.remove(self.processed_image.path)
        super().delete(*args, **kwargs)
