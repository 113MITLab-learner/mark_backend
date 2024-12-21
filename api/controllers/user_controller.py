# api/controllers/user_controller.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    if request.method == 'GET':
        return Response({
            "username": user.username,
            "email": user.email,
            # 其他需要的字段
        })
    
    elif request.method == 'PUT':
        data = request.data
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            try:
                validate_password(data['password'], user)
                user.set_password(data['password'])
            except ValidationError as e:
                return Response({"error": e.messages}, status=400)
        user.save()
        return Response({"message": "Profile updated successfully"})
