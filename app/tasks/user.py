from app.core.celery import celery_app
from app.crud.user import remove_expired_activation_tokens
from app.core.database import SessionLocal

@celery_app.task
def remove_expired_tokens_task():
    db = SessionLocal()
    try:
        remove_expired_activation_tokens(db)
    finally:
        db.close()
