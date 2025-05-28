

from django.core.validators import MinValueValidator
from django.db import models

from django.conf import settings


class Executor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='executor_profile'
    )
    specialty = models.CharField(max_length=100)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} ({self.specialty})"


class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('pending', 'В обработке'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен')
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_orders',
        verbose_name='Заказчик')
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executor_orders',
        verbose_name='Исполнитель'
    )
    title = models.CharField(max_length=256, verbose_name='Название заказа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус заказа')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма',
        validators=[MinValueValidator(0.01)]
    )
    description = models.TextField(verbose_name='Описание заказа')

    def take_order(self, executor):
        """Метод для взятия заказа в работу"""
        if self.status != 'new':
            raise ValueError("Заказ уже взят в работу или завершен")

        self.executor = executor.user
        self.status = 'pending'
        self.save()

    def complete_order(self):
        """Метод для завершения заказа"""
        if self.status != 'pending':
            raise ValueError("Заказ не в работе")

        self.status = 'completed'
        self.save()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} - {self.title}"
