from django.http import JsonResponse
from django.utils import timezone
from subscriptions.models import UserSubscription

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response # функция "дать ответ"
        # (пустит запрос дальше, если вызвать get_response(request))

    def __call__(self, request):
        # Проверяем, относится ли запрос к эндпоинтам заказов
        path = request.path # получаем url запроса
        if path.startswith('/general/orders/') or path.startswith('/general/new-orders/') or path.startswith('/general/orders-in-work/'):
            # Пропускаем, если пользователь не аутентифицирован
            if not request.user.is_authenticated:
                return self.get_response(request)

            # Пропускаем, если пользователь - администратор
            if request.user.is_staff:
                return self.get_response(request)

            # Проверяем наличие активной подписки
            has_active_subscription = UserSubscription.objects.filter(
                user=request.user,
                is_active=True,
                end_date__gt=timezone.now()
            ).exists()

            if not has_active_subscription:
                return JsonResponse(
                    {'error': 'Для доступа к заказам требуется активная подписка'},
                    status=403
                )

        # Пропускаем запросы к другим эндпоинтам (тарифы, подписки, админка)
        return self.get_response(request)