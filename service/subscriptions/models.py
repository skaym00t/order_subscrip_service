from django.utils import timezone

from django.conf import settings
from django.db import models

# Create your models here.
class Tariff(models.Model):
    """Модель тарифов."""
    TARIFF_TYPES = (
        ('basic', 'Базовый'),
        ('standard', 'Стандарт'),
        ('full', 'Полный'),
        ('premium', 'Премиум')
    )
    title = models.CharField(max_length=20, choices=TARIFF_TYPES, verbose_name='Тип тарифа')
    price_per_day = models.PositiveIntegerField(default=0, verbose_name='Стоимость тарифа(день)')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Статус тарифа')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'

class UserSubscription(models.Model):
    """Модель подписки пользователя."""
    SUBSCRIPTION_PERIOD = (
        (7, 'неделя'),
        (30, '30 дней'),
        (365, '365 дней')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name='Тариф'
    )
    subscription_period = models.PositiveIntegerField(choices=SUBSCRIPTION_PERIOD, verbose_name='Период подписки')
    start_date = models.DateTimeField(default=timezone.now, verbose_name='Дата начала')
    end_date = models.DateTimeField(default=timezone.now, verbose_name='Дата окончания')
    is_active = models.BooleanField(default=True, verbose_name='Статус подписки')

    def __str__(self):
        return f'{self.user.username} - {self.tariff.title}'

    def save(self, *args, **kwargs):
        """Переопределенный метод save для установки даты окончания подписки."""
        if not self.pk:
            self.end_date = self.start_date + timezone.timedelta(days=self.subscription_period)
        else:
            self.end_date = timezone.now() + timezone.timedelta(days=self.subscription_period)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Подписка пользователя'
        verbose_name_plural = 'Подписки пользователей'