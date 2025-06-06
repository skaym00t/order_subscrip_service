"""
URL configuration for service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from clients.views import CustomUserViewSet
from products.views import OrderViewSet, NewOrdersViewSet, OrdersInWorkViewSet
from subscriptions.views import TariffViewSet, UserSubscriptionViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register(r'subscriptions', UserSubscriptionViewSet, basename='usersubscription')
router.register(r'tariffs', TariffViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'new-orders', NewOrdersViewSet, basename='new-order')
router.register(r'orders-in-work', OrdersInWorkViewSet, basename='order-in-work')
router.register(r'users', CustomUserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('general/auth/', include('rest_framework.urls')),
    path('general/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('general/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('general/', include(router.urls)),
]