

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().select_related('customer', 'executor')

        # Для обычных пользователей - только их заказы
        return Order.objects.filter(customer=user).select_related('customer', 'executor')

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

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
            return Response({'status': 'Заказ отменен'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
            order.take_order(request.user.executor_profile)
            return Response({'status': 'Заказ взят в работу'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



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
            return Response({'status': 'Заказ завершен'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)