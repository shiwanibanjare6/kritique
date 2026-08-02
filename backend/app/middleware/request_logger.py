import time

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class RequestLoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        start = time.time()

        response = await call_next(request)

        process_time = round(time.time() - start, 4)

        logger.info(

            f"{request.method} "

            f"{request.url.path} "

            f"{response.status_code} "

            f"{process_time}s"

        )

        return response