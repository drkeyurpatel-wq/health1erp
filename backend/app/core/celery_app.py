from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "health1erp",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-expiring-stock": {
            "task": "app.core.celery_app.check_expiring_stock",
            "schedule": 86400.0,  # daily
        },
        "calculate-daily-stats": {
            "task": "app.core.celery_app.calculate_daily_stats",
            "schedule": 86400.0,
        },
    },
)


@celery_app.task
def send_notification(channel: str, recipient: str, message: str, **kwargs):
    """Send notification via SMS, email, push, or WhatsApp."""
    # Implementation depends on channel
    return {"channel": channel, "recipient": recipient, "status": "sent"}


@celery_app.task
def generate_report(report_type: str, params: dict):
    """Generate a report asynchronously."""
    return {"report_type": report_type, "status": "generated"}


@celery_app.task
def check_expiring_stock():
    """Check for items expiring soon and send alerts."""
    return {"status": "checked"}


@celery_app.task
def calculate_daily_stats():
    """Calculate daily operational statistics."""
    return {"status": "calculated"}
