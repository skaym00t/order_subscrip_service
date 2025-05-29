from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CustomUser
from .serializers import CustomUserSerializer


class CustomUserViewSet(viewsets.GenericViewSet): # Используем GenericViewSet для создания пользовательского API
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['post'], permission_classes=[]) # permission_classes=[] не требует аутентификации
    def register(self, request): # Создаем пользовательский метод для регистрации пользователей
        serializer = self.get_serializer(data=request.data) # Получаем сериализатор из класса
        serializer.is_valid(raise_exception=True) # Проверяем валидность данных, если не валидны, то будет выброшено исключение
        user = serializer.save() # (save вызывает метод create из сериализатора)
        return Response({
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'is_executor': hasattr(user, 'executor_profile')
        }, status=status.HTTP_201_CREATED)
