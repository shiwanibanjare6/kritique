from celery import Celery
from app.config import REDIS_URL

celery_app = Celery("ai_pr_reviewer", broker=REDIS_URL, backend=REDIS_URL)
