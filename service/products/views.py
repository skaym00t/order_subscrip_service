from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
import requests
import logging
from .notification import NotificationOrders

logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().select_related('customer', 'executor')
        return Order.objects.filter(customer=user).select_related('customer', 'executor')

    def perform_create(self, serializer):
        order = serializer.save()
        logger.info(f"Создан заказ {order.id} для пользователя {self.request.user.id}")
        message_customer = NotificationOrders('notify-create', order, self.request.user)  # Создаем объект уведомления
        message_exec = NotificationOrders('notify-new-order', order)  # Уведомление исполнителям
        message_customer()  # Отправляем уведомление через Telegram API
        message_exec()  # Отправляем уведомление исполнителям

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отмена заказа (только для заказчика)"""
        order = self.get_object()
        if order.customer != request.user:
            return Response(
                {'error': 'Вы не можете отменить чужой заказ'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            order.status = 'canceled'
            order.save()

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            message = NotificationOrders('notify-cancel-order', order, request.user)
            message()  # Отправляем уведомление заказчику
            return Response({'status': 'Заказ отменен'})


class NewOrdersViewSet(viewsets.ReadOnlyModelViewSet):
    """Заказы доступные для взятия в работу (только для исполнителей и админа)"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.filter(status='new', executor__isnull=True)

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset().all().select_related('customer')
        elif not hasattr(self.request.user, 'executor_profile') and not self.request.user.is_staff:
            return Order.objects.none() # тут можно сделать редирект на заявку стать исполнителем(не реализовано)
        return super().get_queryset().exclude(
            customer=self.request.user
        ).select_related('customer')

    @action(detail=True, methods=['post']) # detail=True означает, что действие применяется к конкретному объекту
    def take(self, request, pk=None):
        """Взять заказ в работу"""
        if not hasattr(request.user, 'executor_profile'):
            return Response(
                {'error': 'Только исполнители могут брать заказы'},
                status=status.HTTP_403_FORBIDDEN
            )

        order = self.get_object() # Получаем заказ по pk (get_object() уже проверяет, что заказ существует)

        if order.executor is not None:
            return Response(
                {'error': 'Заказ уже взят в работу'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order.take_order(request.user.executor_profile) # Вызываем метод take_order
            logger.info(f"Заказ {order.id} взят в работу исполнителем {request.user.id}")

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            message_exec = NotificationOrders('notify-take-exec', order, request.user) # Создаем объект уведомления
            message_cust = NotificationOrders('notify-take-cust', order, order.customer)  # Уведомление заказчику
            message_exec()  # Отправляем уведомление через Telegram API
            message_cust()  # Отправляем уведомление заказчику
            return Response({'status': 'Заказ взят в работу'})


class OrdersInWorkViewSet(viewsets.ReadOnlyModelViewSet):
    """Заказы в работе (только для исполнителей и админа)"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.filter(status='pending', executor__isnull=False)

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset().all().select_related('customer')
        elif not hasattr(self.request.user, 'executor_profile') and not self.request.user.is_staff:
            return Order.objects.none() # тут можно сделать редирект на заявку стать исполнителем(не реализовано)
        return super().get_queryset().filter(
            executor=self.request.user
        ).select_related('customer')

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Эндпоинт для завершения заказа"""
        if not hasattr(request.user, 'executor_profile'): # Проверяем, что пользователь - исполнитель
            return Response(
                {'error': 'Только исполнители могут закрывать заказы'},
                status=status.HTTP_403_FORBIDDEN
            )

        order = self.get_object() # Получаем заказ по pk (get_object() уже проверяет, что заказ существует)

        if order.executor != request.user: # Проверяем, что заказ взят текущим исполнителем
            return Response(
                {'error': 'Вы не можете завершить чужой заказ'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            order.complete_order()
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            message = NotificationOrders('notify-complete-order', order, request.user)
            message()  # Отправляем уведомление заказчику
            return Response({'status': 'Заказ завершен'})
