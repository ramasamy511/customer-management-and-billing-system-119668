import os
import smtplib
from email.mime.text import MIMEText
from fastapi import HTTPException

# PUBLIC_INTERFACE
def send_email_reminder(recipient_email: str, subject: str, message: str) -> None:
    """
    Sends an email reminder through SMTP.

    Args:
        recipient_email (str): The recipient's email address.
        subject (str): The email subject.
        message (str): The email body/content.

    Raises:
        HTTPException: If there is an error sending email.
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
    Sends a WhatsApp reminder using a 3rd party API or stub.

    Args:
        recipient_phone (str): The recipient's WhatsApp phone number (E.164 format recommended).
        message (str): The message body.

    Raises:
        NotImplementedError: This function is a stub for WhatsApp integration.
    """
    # In production: integrate with Twilio, Meta API, etc.
    # For now, this is a stub to show interface.
    # Log/output can be added for demonstration.
    # Example: requests.post("https://api.whatsapp.service/send", ...)
    raise NotImplementedError("WhatsApp integration not implemented. (Stub)")
