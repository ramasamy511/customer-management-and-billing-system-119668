from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from src.api import models
from src.api.database import get_db

router = APIRouter()

# PUBLIC_INTERFACE
@router.get("/", response_model=List[models.PaymentOut], summary="List payments", description="Get all payments with optional invoice filter.")
def list_payments(
    invoice_id: Optional[int] = Query(None, description="Filter by invoice ID"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Payment)
    if invoice_id:
        query = query.filter(models.Payment.invoice_id == invoice_id)
    payments = query.order_by(models.Payment.payment_date.desc()).all()
    return payments

# PUBLIC_INTERFACE
@router.post("/", response_model=models.PaymentOut, status_code=status.HTTP_201_CREATED, summary="Create payment for invoice")
def create_payment(
    payment: models.PaymentCreate,
    db: Session = Depends(get_db)
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == payment.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    # Validate payment date
    if payment.payment_date > datetime.date.today():
        raise HTTPException(status_code=400, detail="Payment date cannot be in the future")
    db_payment = models.Payment(**payment.dict(exclude_unset=True))
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

# PUBLIC_INTERFACE
@router.get("/{payment_id}", response_model=models.PaymentOut, summary="Get payment details")
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
