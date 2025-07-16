from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.api import models
from src.api.database import get_db

router = APIRouter()

# PUBLIC_INTERFACE
@router.get("/", response_model=List[models.ReminderOut], summary="List reminders", description="Get all reminders for all or specific invoice.")
def list_reminders(
    invoice_id: Optional[int] = Query(None, description="Filter by invoice ID"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Reminder)
    if invoice_id:
        query = query.filter(models.Reminder.invoice_id == invoice_id)
    reminders = query.order_by(models.Reminder.sent_on.desc()).all()
    return reminders

# PUBLIC_INTERFACE
@router.post("/", response_model=models.ReminderOut, status_code=status.HTTP_201_CREATED, summary="Send reminder (record status)")
def send_reminder(
    reminder: models.ReminderCreate,
    db: Session = Depends(get_db)
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == reminder.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    # (Stub: actual logic to send a reminder on real channels not implemented)
    db_reminder = models.Reminder(
        invoice_id=reminder.invoice_id,
        channel=reminder.channel,
        status=models.ReminderStatusEnum.sent,
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

# PUBLIC_INTERFACE
@router.get("/{reminder_id}", response_model=models.ReminderOut, summary="Get reminder details")
def get_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder
