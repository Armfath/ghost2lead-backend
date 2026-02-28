from pathlib import Path

from asgiref.sync import async_to_sync
from celery import Celery
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import configs

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / configs.TEMPLATE_DIR

mail_conf = ConnectionConfig(
    MAIL_USERNAME=configs.MAIL_USERNAME,
    MAIL_PASSWORD=configs.MAIL_PASSWORD,
    MAIL_FROM=configs.MAIL_FROM,
    MAIL_FROM_NAME=configs.MAIL_FROM_NAME,
    MAIL_PORT=configs.MAIL_PORT,
    MAIL_SERVER=configs.MAIL_SERVER,
    MAIL_STARTTLS=configs.MAIL_STARTTLS,
    MAIL_SSL_TLS=configs.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=TEMPLATE_DIR,
)

fastmail = FastMail(mail_conf)
send_message = async_to_sync(fastmail.send_message)

celery_app = Celery(
    "ghost2lead_tasks",
    broker=configs.redis_url(configs.REDIS_DB_CELERY),
    backend=configs.redis_url(configs.REDIS_DB_CELERY),
    broker_connection_retry_on_startup=True,
)


@celery_app.task
def send_otp_email(recipient: str, otp: str) -> None:
    """Send OTP code to recipient via email (background task)."""
    try:
        expiry_minutes = configs.OTP_TTL_SECONDS // 60
        message = MessageSchema(
            subject=f"Your {configs.APP_NAME} verification code",
            recipients=[recipient],
            template_body={"otp": otp, "expiry_minutes": expiry_minutes},
            subtype=MessageType.html,
        )
        send_message(message, template_name="otp_email.html")
    except Exception:
        raise
