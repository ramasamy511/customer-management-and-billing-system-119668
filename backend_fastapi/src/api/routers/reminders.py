from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.api import models
from src.api.database import get_db
from src.api import integrations

router = APIRouter()

# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=List[models.ReminderOut],
    summary="List reminders",
    description="Get all reminders for all or specific invoice.",
    tags=["Reminders"]
)
def list_reminders(
    invoice_id: Optional[int] = Query(None, description="Filter by invoice ID"),
    db: Session = Depends(get_db)
):
    """
    List all reminders or filter by invoice.

    Args:
        invoice_id (Optional[int]): Filter by invoice ID.

    Returns:
        List[ReminderOut]: List of reminders matching filter.
    """
    query = db.query(models.Reminder)
    if invoice_id:
        query = query.filter(models.Reminder.invoice_id == invoice_id)
    reminders = query.order_by(models.Reminder.sent_on.desc()).all()
    return reminders

# PUBLIC_INTERFACE
@router.post(
    "/",
    response_model=models.ReminderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Send reminder (trigger and record status)",
    description="Triggers a reminder via Email or WhatsApp based on channel and records the attempt and status.",
    tags=["Reminders"]
)
def send_reminder(
    reminder: models.ReminderCreate,
    db: Session = Depends(get_db)
):
    """
    Send a payment reminder to the customer via the specified channel ("email" or "whatsapp").
    Records the attempt and the status.
    - For email: sends via SMTP if customer.email exists.
    - For WhatsApp: (stub) intended for later WhatsApp Business API integration.

    Args:
        reminder (ReminderCreate): Reminder details (must specify channel).

    Returns:
        ReminderOut: The status of the sent reminder attempt.

    Raises:
        HTTPException: If customer info is insufficient or integration fails.
    """
    invoice = db.query(models.Invoice).filter(models.Invoice.id == reminder.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    customer = db.query(models.Customer).filter(models.Customer.id == invoice.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found for invoice")

    channel = reminder.channel.lower()
    status_enum = models.ReminderStatusEnum.sent

    if channel == "email":
        if not customer.email:
            raise HTTPException(status_code=400, detail="Customer does not have an email address.")
        subject = f"Payment Reminder for Invoice #{invoice.invoice_number}"
        msg = (
            f"Dear {customer.name},\n\n"
            f"This is a reminder that invoice #{invoice.invoice_number} (amount: ₹{invoice.total_amount:.2f}) "
            f"is due on {invoice.due_date.isoformat()}.\n\nPlease make the payment at your earliest convenience.\n\nThank you!"
        )
        try:
            integrations.send_email_reminder(customer.email, subject, msg)
        except HTTPException:
            status_enum = models.ReminderStatusEnum.failed
        # reminder_message removed (lint fix)
    elif channel == "whatsapp":
        if not customer.phone:
            raise HTTPException(status_code=400, detail="Customer does not have a phone number.")
        msg = (
            f"Reminder: Invoice #{invoice.invoice_number} for ₹{invoice.total_amount:.2f} "
            f"is due on {invoice.due_date.isoformat()} for {customer.name}."
        )
        try:
            integrations.send_whatsapp_reminder(customer.phone, msg)
        except NotImplementedError:
            status_enum = models.ReminderStatusEnum.failed
        except Exception:
            status_enum = models.ReminderStatusEnum.failed
    else:
        raise HTTPException(status_code=422, detail="Unsupported reminder channel. Use 'email' or 'whatsapp'.")

    db_reminder = models.Reminder(
        invoice_id=reminder.invoice_id,
        channel=channel,
        status=status_enum,
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    # For demo: Attach message in the returned model if needed (skipped for DB model)
    return db_reminder

# PUBLIC_INTERFACE
@router.get(
    "/{reminder_id}",
    response_model=models.ReminderOut,
    summary="Get reminder details",
    tags=["Reminders"]
)
def get_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    """
    Returns reminder details for a given reminder ID.

    Args:
        reminder_id (int): Reminder unique identifier.

    Returns:
        ReminderOut: Reminder details.
    """
    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder
