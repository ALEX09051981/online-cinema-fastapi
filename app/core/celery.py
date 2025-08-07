from celery import Celery
from app.core.config import settings

celery_app = Celery("online-cinema", broker=settings.CELERY_BROKER_URL)
