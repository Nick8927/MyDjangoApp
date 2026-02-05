import time
import logging

logger = logging.getLogger(__name__)


class RequestLogMiddleware:
    """
    Логируем каждый запрос:
    - путь
    - метод
    - пользователя
    - время обработки
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = round(time.time() - start_time, 3)

        user = request.user if request.user.is_authenticated else "Anonymous"

        logger.info(
            f"{request.method} {request.path} | "
            f"user={user} | {duration}s | status={response.status_code}"
        )

        return response
