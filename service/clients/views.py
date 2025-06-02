from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CustomUser
from .serializers import CustomUserSerializer


class CustomUserViewSet(viewsets.GenericViewSet):
    """ViewSet для регистрации новых пользователей."""
    queryset = CustomUser.objects.none()
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        """Регистрация нового пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'is_executor': hasattr(user, 'executor_profile')
        }, status=status.HTTP_201_CREATED)
