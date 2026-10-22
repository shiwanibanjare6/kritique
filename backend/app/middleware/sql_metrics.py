from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class SQLRequestMetrics:
    query_count: int = 0
    db_time_ms: float = 0.0
    auth_time_ms: float = 0.0


sql_request_metrics: ContextVar[SQLRequestMetrics | None] = ContextVar(
    "sql_request_metrics", default=None
)
