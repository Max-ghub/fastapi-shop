from celery import Celery

import app.models  # noqa: F401
from app.core.config import settings

celery_app = Celery(
    "shop",
    broker=settings.celery_broker_dsn,
    backend=settings.celery_result_dsn,
    include=[
        "app.tasks.orders",
    ],
)

celery_app.conf.update(task_default_queue="order.process")
