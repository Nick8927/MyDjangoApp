import time
import logging
from .models import CartItem
from django.db.models import Sum, F

logger = logging.getLogger(__name__)


class RequestLogMiddleware:
    """ пишем логи для медленных запросов и ошибок"""

    SLOW_REQUEST_THRESHOLD = 0.5  # секунды

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = round(time.time() - start_time, 3)

        if request.path.startswith("/static/"):
            return response

        user = (
            request.user.username
            if request.user.is_authenticated
            else "Anonymous"
        )

        log_message = (
            f"{request.method} {request.path} | "
            f"user={user} | {duration}s | "
            f"status={response.status_code}"
        )

        if response.status_code >= 400:
            logger.warning(log_message)

        elif duration > self.SLOW_REQUEST_THRESHOLD:
            logger.info(f"SLOW REQUEST: {log_message}")

        return response


class CartMiddleware:
    """ Прод. версия  middleware для корзины.
    Прокидывает агрегированное состояние корзины в request.cart
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.cart = {
            "items": [],
            "total_qty": 0,
            "total_price": 0,
            "has_items": False,
        }

        if request.user.is_authenticated:
            cart_items = (
                CartItem.objects
                .filter(user=request.user)
                .select_related("product")
            )

            if cart_items.exists():
                totals = cart_items.aggregate(
                    total_qty=Sum("quantity"),
                    total_price=Sum(F("quantity") * F("product__price"))
                )

                request.cart = {
                    "items": cart_items,
                    "total_qty": totals["total_qty"] or 0,
                    "total_price": totals["total_price"] or 0,
                    "has_items": True,
                }

        response = self.get_response(request)
        return response
