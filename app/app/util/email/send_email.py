import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config.config import settings


def send_email(
    sender_name, sender_email, password, recipient_name, recipient_address, subject, body
):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = f"{recipient_name} <{recipient_address}>"
    msg.attach(MIMEText(body, "html"))
    with smtplib.SMTP_SSL(
        settings.MAIL_SERVER, settings.MAIL_PORT, context=ssl.create_default_context()
    ) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_address, msg.as_string())
