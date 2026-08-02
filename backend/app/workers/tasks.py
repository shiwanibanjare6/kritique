from app.workers.celery_worker import celery_app

@celery_app.task
def process_review(payload: dict) -> dict:
    return {"status": "processed", "payload": payload}
