import os

from celery import Celery

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
app = Celery("turboprivate", broker=broker_url)
