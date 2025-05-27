from django.template.context_processors import request
from rest_framework import generics, viewsets, status
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response

from subscriptions.models import Tariff, UserSubscription
from subscriptions.serializers import TariffSerializer, UserSubscriptionSerializer


# Create your views here.

class TariffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tariff.objects.filter(is_active=True)
    serializer_class =  TariffSerializer

class UserSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return UserSubscription.objects.none()
        return UserSubscription.objects.filter(
            user=user,
            is_active=True
        ).select_related('tariff').order_by('-start_date')

