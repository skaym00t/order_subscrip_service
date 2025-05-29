from django.template.context_processors import request
from rest_framework import generics, viewsets, status
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from subscriptions.models import Tariff, UserSubscription
from subscriptions.serializers import TariffSerializer, UserSubscriptionSerializer


# Create your views here.

class TariffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tariff.objects.filter(is_active=True)
    serializer_class =  TariffSerializer
    permission_classes = [AllowAny]

class UserSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserSubscription.objects.all().select_related('tariff')
        return UserSubscription.objects.filter(
            user=user,
            is_active=True
        ).select_related('tariff').order_by('-start_date')

    def perform_create(self, serializer):
        """Устанавливаем текущего пользователя как владельца подписки"""
        serializer.save(user=self.request.user)

