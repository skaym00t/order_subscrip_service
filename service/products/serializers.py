from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    can_cancel = serializers.SerializerMethodField()

    def get_can_cancel(self, obj):
        request = self.context.get('request')
        return request and obj.customer == request.user and obj.status == 'new'

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'executor', 'title',
            'description', 'status', 'price',
            'created_at', 'updated_at', 'can_cancel'
        ]
        read_only_fields = [
            'executor', 'status',
            'created_at', 'updated_at'
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть положительной")
        return value

# class TakeOrderSerializer(serializers.Serializer):
#     """Сериализатор для взятия заказа в работу"""
#     executor_id = serializers.IntegerField()
#
#     def validate_executor_id(self, value):
#         try:
#             Executor.objects.get(id=value)
#         except Executor.DoesNotExist:
#             raise serializers.ValidationError("Исполнитель не найден")
#         return value