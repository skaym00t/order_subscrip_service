from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

class NotificationOrders:
    def __init__(self, url_bot, order, user=None):
        self.url = f"{settings.DJANGO_URL}/{url_bot}/"
        self.message = {
            "user_id": user.id if user else None,
            "customer_id": order.customer.id if order.customer else None,
            "customer_name": order.customer.username if order.customer else None,
            "customer_phone": order.customer.phone if order.customer else None,
            "executor_id": order.executor.id if order.executor else None,
            "executor_name": order.executor.username if order.executor else None,
            "executor_phone": order.executor.phone if order.executor else None,
            "order_id": order.id,
            "order_title": order.title,
            "order_description": order.description,
            "order_price": float(order.price) if order.price else None,
            "order_status": order.status
        }
        logger.debug(f"Формирование уведомления: url={self.url}, message={self.message}")

    def __call__(self, *args, **kwargs):
        """Отправка уведомления через Telegram API"""
        try:
            response = requests.post(self.url, json=self.message, timeout=5)
            response.raise_for_status()
            logger.info(f"Уведомление успешно отправлено: {self.url}, response={response.json()}")
        except requests.RequestException as e:
            logger.error(f"Ошибка отправки уведомления: {e}, response={response.text if 'response' in locals() else 'No response'}")
            # Не выбрасываем исключение, чтобы не прерывать создание заказа
            return {"status": "failed", "error": str(e)}
        return response.json()