from rest_framework import serializers

from .models import Executor, CustomUser


class ExecutorSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Executor, который включает информацию о пользователе и специальности исполнителя."""
    class Meta:
        model = Executor
        fields = ['id', 'user', 'specialty', 'rating']


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели CustomUser, который включает поля для создания пользователя и опциональное поле для исполнителей."""
    specialty = serializers.CharField(max_length=100, required=False, allow_blank=True, write_only=True)
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'password', 'first_name', 'last_name', 'is_executor', 'specialty')
        extra_kwargs = { # Дополнительные настройки полей
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        """Создание нового пользователя с проверкой на исполнителя и специальность."""
        is_executor = validated_data.get('is_executor', False)
        specialty = validated_data.pop('specialty', '')
        if is_executor and not specialty:
            raise serializers.ValidationError("Для исполнителя необходимо указать специальность.")
        user = CustomUser.objects.create_user(**validated_data)

        if is_executor and specialty:
            Executor.objects.create(user=user, specialty=specialty)

        return user