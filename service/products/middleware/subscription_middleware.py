from django.http import JsonResponse
from django.utils import timezone
from subscriptions.models import UserSubscription

class SubscriptionMiddleware:
    """Middleware для проверки наличия активной подписки у пользователя."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path.startswith('/general/orders/') or path.startswith('/general/new-orders/') or path.startswith('/general/orders-in-work/'):

            if request.user.is_staff:
                return self.get_response(request)

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

        return self.get_response(request)