import time

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.middleware.sql_metrics import SQLRequestMetrics, sql_request_metrics


class RequestLoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        start = time.perf_counter()
        metrics = SQLRequestMetrics() if settings.DEBUG_SQL else None
        context_token = sql_request_metrics.set(metrics)
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            sql_request_metrics.reset(context_token)
            if metrics is None:
                logger.info(
                    "%s %s status=%s duration_ms=%.2f",
                    request.method,
                    request.url.path,
                    status_code,
                    duration_ms,
                )
            else:
                logger.info(
                    "%s %s status=%s query_count=%s db_time_ms=%.2f auth_time_ms=%.2f duration_ms=%.2f",
                    request.method,
                    request.url.path,
                    status_code,
                    metrics.query_count,
                    metrics.db_time_ms,
                    metrics.auth_time_ms,
                    duration_ms,
                )
