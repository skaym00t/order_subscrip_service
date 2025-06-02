from rest_framework import serializers
from subscriptions.models import Tariff, UserSubscription

class TariffSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tariff."""
    class Meta:
        model = Tariff
        fields = ('title', 'price_per_day', 'description')

class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели UserSubscription."""
    tariff_detail = TariffSerializer(source='tariff', read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserSubscription
        fields = ('user','tariff','tariff_detail', 'subscription_period', 'start_date', 'end_date')
        read_only_fields = ('user', 'start_date', 'end_date')