import telebot
from os import environ

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from clients.models import CustomUser
from .models import Order
from .serializers import OrderSerializer

import logging


logger = logging.getLogger(__name__)

bot = telebot.TeleBot(environ.get("TELEGRAM_BOT_TOKEN"))

class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с заказами."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().select_related('customer', 'executor')
        return Order.objects.filter(customer=user).select_related('customer', 'executor')

    def perform_create(self, serializer):
        """Создание нового заказа."""
        order = serializer.save()
        logger.info(f"Создан заказ {order.id} для пользователя {self.request.user.id}")
        if self.request.user.chat_id:
            bot.send_message(self.request.user.chat_id, f"Создан новый заказ: {order.title}!")
        exec_list = CustomUser.objects.filter(is_executor=True, chat_id__isnull=False).values_list('chat_id', flat=True)
        for exec_chat_id in exec_list:
            bot.send_message(
                exec_chat_id,
                f'''Создан новый заказ!\n
                {order.title}\n
                Заказчик: {self.request.user.username}\n
                Телефон: {self.request.user.phone}\n
                Описание заказа: {order.description}\n
                Предложенная цена: {order.price}'''
            )

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
            if self.request.user.chat_id:
                bot.send_message(self.request.user.chat_id, f"Заказ {order.title} отменен!")
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

    @action(detail=True, methods=['post'])
    def take(self, request, pk=None):
        """Взять заказ в работу"""
        if not hasattr(request.user, 'executor_profile'):
            return Response(
                {'error': 'Только исполнители могут брать заказы'},
                status=status.HTTP_403_FORBIDDEN
            )

        order = self.get_object()

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
            if self.request.user.chat_id:
                bot.send_message(self.request.user.chat_id, f"Вы взяли в работу заказ: {order.title}. Телефон заказчика {order.customer.phone}!")
            if order.customer.chat_id:
                bot.send_message(
                    order.customer.chat_id,
                    f"Заказ {order.title} взят в работу исполнителем {self.request.user.username}, телефон исполнителя {self.request.user.phone}!"
                )
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
            if self.request.user.chat_id:
                bot.send_message(self.request.user.chat_id, f"Вы завершили заказ: {order.title}!")
            if order.customer.chat_id:
                bot.send_message(
                    order.customer.chat_id,
                    f"Заказ {order.title} выполнен исполнителем {self.request.user.username}, телефон исполнителя {self.request.user.phone}!"
                )
            return Response({'status': 'Заказ завершен'})
