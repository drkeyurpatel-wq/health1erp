import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_sms(phone: str, message: str) -> bool:
    """Send SMS via Twilio."""
    if not settings.TWILIO_ACCOUNT_SID:
        logger.warning("Twilio not configured, skipping SMS")
        return False
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=settings.TWILIO_PHONE_NUMBER, to=phone)
        return True
    except Exception as e:
        logger.error(f"SMS failed: {e}")
        return False


async def send_email(to: str, subject: str, body: str, html: Optional[str] = None) -> bool:
    """Send email via SMTP."""
    if not settings.SMTP_USER:
        logger.warning("SMTP not configured, skipping email")
        return False
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to
        msg.attach(MIMEText(body, "plain"))
        if html:
            msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False


async def send_push_notification(device_token: str, title: str, body: str) -> bool:
    """Send push notification via Firebase."""
    try:
        import firebase_admin
        from firebase_admin import messaging

        if not firebase_admin._apps:
            return False

        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=device_token,
        )
        messaging.send(message)
        return True
    except Exception as e:
        logger.error(f"Push notification failed: {e}")
        return False


# --- Notification Templates ---

TEMPLATES = {
    "appointment_reminder": {
        "sms": "Reminder: You have an appointment at {hospital} on {date} at {time} with {doctor}.",
        "email_subject": "Appointment Reminder - {hospital}",
    },
    "discharge_notification": {
        "sms": "Patient {patient} has been discharged from {hospital}. Please follow the discharge instructions.",
        "email_subject": "Discharge Notification - {patient}",
    },
    "bill_generated": {
        "sms": "Bill #{bill_number} of Rs.{amount} generated at {hospital}. Please make payment by {due_date}.",
        "email_subject": "Bill Generated - {bill_number}",
    },
    "lab_results_ready": {
        "sms": "Your lab results are ready. Please visit {hospital} or check the patient portal.",
        "email_subject": "Lab Results Ready",
    },
}
