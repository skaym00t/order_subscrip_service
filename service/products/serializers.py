from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order."""
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    can_cancel = serializers.SerializerMethodField()

    def get_can_cancel(self, obj):
        """Проверка возможности отмены заказа."""
        request = self.context.get('request')
        return request and obj.customer == request.user and obj.status == 'new'

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_username', 'executor', 'title',
            'description', 'status', 'price', 'created_at', 'updated_at', 'can_cancel'
        ]
        read_only_fields = [
            'customer_username', 'executor', 'status', 'created_at', 'updated_at', 'can_cancel'
        ]

    def validate_price(self, value):
        """Проверка, что цена положительная."""
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть положительной")
        return value