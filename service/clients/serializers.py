from rest_framework import serializers

from .models import Executor, CustomUser


class ExecutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Executor
        fields = ['id', 'user', 'specialty', 'rating']


class CustomUserSerializer(serializers.ModelSerializer):
    specialty = serializers.CharField(max_length=100, required=False, allow_blank=True, write_only=True) # опциональное
    # поле для исполнителей (specialty - это специальность исполнителя, например, "Веб-разработчик")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'password', 'first_name', 'last_name', 'is_executor', 'specialty')
        extra_kwargs = { # Дополнительные настройки полей
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        is_executor = validated_data.get('is_executor', False) # Извлекаем значение поля is_executor
        specialty = validated_data.pop('specialty', '') # Извлекаем значение поля specialty (если оно есть)
        if is_executor and not specialty:
            raise serializers.ValidationError("Для исполнителя необходимо указать специальность.")
        user = CustomUser.objects.create_user(**validated_data)

        if is_executor and specialty: # Если пользователь является исполнителем и указана специальность
            Executor.objects.create(user=user, specialty=specialty) # Создаем объект исполнителя

        return user # Возвращаем созданного пользователя