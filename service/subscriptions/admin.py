from django.contrib import admin

from subscriptions.models import Tariff, UserSubscription


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    """Админка для тарифов."""
    list_display = ('title', 'price_per_day', 'description', 'is_active')
    list_display_links = ('title',)

    class Meta:
        model = Tariff


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """Админка для подписок пользователей."""
    list_display = ('user', 'tariff', 'start_date', 'end_date', 'is_active')
    list_display_links = ('tariff',)

    class Meta:
        model = UserSubscription

