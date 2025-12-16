import datetime
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config.config import settings

def load_template(template_path: str, **kwargs) -> str:
    """Load and render an email template with placeholders."""
    template_path = Path(template_path)
    template = template_path.read_text()
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template

def render_text_content(template: str, **kwargs) -> str:
    """Render a plain text email template with placeholders."""
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template

def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str,
) -> None:
    """Send a multipart email."""
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_account = settings.SMTP_ACCOUNT
    smtp_password = settings.SMTP_PASSWORD

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{smtp_user} <{smtp_account}>"
    msg["To"] = to_email

    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_account, smtp_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_reset_email(to_email: str, subject: str, access_token: str, refresh_token: str) -> None:
    """Send a password reset email."""
    html_content = load_template(
        "app/templates/password_reset_template.html",
        base_url=settings.BASE_URL,
        token=access_token,
        refresh_token=refresh_token,
        year=datetime.datetime.now().year,
    )
    text_content = render_text_content(
        """Hi,
        We received a request to reset your password. Go to the link below to proceed:
        "{base_url}/password?access_token={token}&refresh_token={refresh_token}"
        If you didn't request this, please ignore this email or contact support.
        {year} Zwaar Developers. All rights reserved.""",
        base_url=settings.BASE_URL,
        token=access_token,
        refresh_token=refresh_token,
        year=datetime.datetime.now().year,
    )
    send_email(to_email, subject, html_content, text_content)

def send_delete_account(
    to_email: str,
    subject: str,
    access_token: str,
    refresh_token: str,
    origin: str,
) -> None:
    """Send an account deletion email."""
    html_content = load_template(
        "app/templates/delete_account_email.html",
        base_url=settings.BASE_URL,
        token=access_token,
        refresh_token=refresh_token,
        year=datetime.datetime.now().year,
    )
    html_content = html_content.replace("{origin}", str(origin))
    text_content = render_text_content(
        """Hi,
        We received a request to delete your account. Go to the link below to proceed:
        "{base_url}/deletion?access_token={token}&refresh_token={refresh_token}&origin={origin}"
        If you didn't request this, please ignore this email or contact support.
        {year} Zwaar Developers. All rights reserved.""",
        base_url=settings.BASE_URL,
        token=access_token,
        refresh_token=refresh_token,
        origin=origin,
        year=datetime.datetime.now().year,
    )
    send_email(to_email, subject, html_content, text_content)
