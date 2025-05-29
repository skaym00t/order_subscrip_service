from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Номер телефона должен быть в формате: '+999999999'. До 15 цифр.")],
        blank=True,
        null=True,
        unique=True,
        verbose_name='Номер телефона'
    )
    telegram_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


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