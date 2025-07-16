import os
import smtplib
from email.mime.text import MIMEText
from fastapi import HTTPException

# PUBLIC_INTERFACE
def send_email_reminder(recipient_email: str, subject: str, message: str) -> None:
    """
    Sends an email reminder to a customer via SMTP.

    Args:
        recipient_email (str): The recipient's email address.
        subject (str): The email subject line.
        message (str): The plain text email content.

    Raises:
        HTTPException: If SMTP config is incomplete or sending fails.
    Example:
        send_email_reminder("foo@bar.com", "Subject", "Body text")
    """
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or "noreply@example.com")

    if not smtp_host or not smtp_user or not smtp_pass:
        raise HTTPException(status_code=500, detail="SMTP configuration incomplete")

    msg = MIMEText(message, "plain")
    msg['Subject'] = subject
    msg['From'] = smtp_from
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, [recipient_email], msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# PUBLIC_INTERFACE
def send_whatsapp_reminder(recipient_phone: str, message: str) -> None:
    """
    Sends a WhatsApp reminder message to the customer via the WhatsApp Business API (stub only).
    
    Args:
        recipient_phone (str): WhatsApp phone number in E.164 format (e.g., +919988776655).
        message (str): Message to send.

    Raises:
        NotImplementedError: Always, as this is a stub.

    Note:
        This is a placeholder/stub for integration with Twilio, Meta API, or another WhatsApp provider.
        Production use should implement this using a real API call (adjust error handling as appropriate).
    Example:
        send_whatsapp_reminder("+911234567890", "Your reminder text")
    """
    # Example stub: uncomment and customize for production integration
    # import requests
    # requests.post("https://whatsapp.yourservice.com/send", json={...}, headers={...})

    raise NotImplementedError("WhatsApp integration not implemented. See README for info.")
