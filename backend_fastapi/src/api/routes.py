from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from . import models, schemas
from .database import get_db

router = APIRouter()

# ---- Customers CRUD ----

# PUBLIC_INTERFACE
@router.post("/customers", response_model=schemas.CustomerDetail, summary="Create a new customer", tags=["Customers"])
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer."""
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# PUBLIC_INTERFACE
@router.get("/customers", response_model=List[schemas.CustomerDetail], summary="List all customers", tags=["Customers"])
def list_customers(db: Session = Depends(get_db)):
    """Get all customers."""
    return db.query(models.Customer).order_by(models.Customer.name).all()

# PUBLIC_INTERFACE
@router.get("/customers/{customer_id}", response_model=schemas.CustomerDetail, summary="Get customer details", tags=["Customers"])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# PUBLIC_INTERFACE
@router.put("/customers/{customer_id}", response_model=schemas.CustomerDetail, summary="Update customer", tags=["Customers"])
def update_customer(customer_id: int, customer: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for k, v in customer.dict().items():
        setattr(db_customer, k, v)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# PUBLIC_INTERFACE
@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete customer", tags=["Customers"])
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(db_customer)
    db.commit()
    return None

# ---- Invoices & Items CRUD ----

@router.post("/invoices", response_model=schemas.InvoiceDetail, summary="Create new invoice with items", tags=["Invoices"])
def create_invoice(invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    items_data = invoice.items
    db_invoice = models.Invoice(
        customer_id=invoice.customer_id,
        invoice_date=invoice.invoice_date or datetime.utcnow(),
        due_date=invoice.due_date,
        status=invoice.status or "unpaid",
        total_amount=invoice.total_amount,
        remark=invoice.remark,
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    # Add items
    for item in items_data:
        db_item = models.InvoiceItem(
            invoice_id=db_invoice.id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            amount=item.amount,
        )
        db.add(db_item)
    db.commit()
    db.refresh(db_invoice)  # get items refetched
    db_invoice.items = db.query(models.InvoiceItem).filter(models.InvoiceItem.invoice_id == db_invoice.id).all()
    return db_invoice

@router.get("/invoices", response_model=List[schemas.InvoiceDetail], summary="List all invoices", tags=["Invoices"])
def list_invoices(customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(models.Invoice)
    if customer_id:
        q = q.filter(models.Invoice.customer_id == customer_id)
    invoices = q.order_by(models.Invoice.invoice_date.desc()).all()
    # Fetch items per invoice to avoid lazy loading errors
    for inv in invoices:
        inv.items  # triggers fetch
    return invoices

@router.get("/invoices/{invoice_id}", response_model=schemas.InvoiceDetail, summary="Get invoice details", tags=["Invoices"])
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    inv.items  # triggers fetch
    return inv

@router.put("/invoices/{invoice_id}", response_model=schemas.InvoiceDetail, summary="Update invoice and items", tags=["Invoices"])
def update_invoice(invoice_id: int, invoice: schemas.InvoiceUpdate, db: Session = Depends(get_db)):
    db_invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    for k, v in invoice.dict(exclude_unset=True, exclude={"items"}).items():
        setattr(db_invoice, k, v)
    # Update items if specified
    if invoice.items is not None:
        db.query(models.InvoiceItem).filter(models.InvoiceItem.invoice_id == invoice_id).delete()
        for item in invoice.items:
            db_item = models.InvoiceItem(
                invoice_id=invoice_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                amount=item.amount,
            )
            db.add(db_item)
    db.commit()
    db.refresh(db_invoice)
    db_invoice.items = db.query(models.InvoiceItem).filter(models.InvoiceItem.invoice_id == db_invoice.id).all()
    return db_invoice

@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete invoice (and all items)", tags=["Invoices"])
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    db_invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.query(models.InvoiceItem).filter(models.InvoiceItem.invoice_id == invoice_id).delete()
    db.delete(db_invoice)
    db.commit()
    return None

# ---- Payments CRUD ----

@router.post("/payments", response_model=schemas.PaymentDetail, summary="Record a payment", tags=["Payments"])
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.get("/payments", response_model=List[schemas.PaymentDetail], summary="List all payments", tags=["Payments"])
def list_payments(customer_id: Optional[int] = None, invoice_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(models.Payment)
    if customer_id:
        q = q.filter(models.Payment.customer_id == customer_id)
    if invoice_id:
        q = q.filter(models.Payment.invoice_id == invoice_id)
    return q.order_by(models.Payment.payment_date.desc()).all()

@router.get("/payments/{payment_id}", response_model=schemas.PaymentDetail, summary="Get payment details", tags=["Payments"])
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    pay = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not pay:
        raise HTTPException(status_code=404, detail="Payment not found")
    return pay

@router.put("/payments/{payment_id}", response_model=schemas.PaymentDetail, summary="Update payment record", tags=["Payments"])
def update_payment(payment_id: int, payment: schemas.PaymentUpdate, db: Session = Depends(get_db)):
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    for k, v in payment.dict(exclude_unset=True).items():
        setattr(db_payment, k, v)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.delete("/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete payment", tags=["Payments"])
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    db.delete(db_payment)
    db.commit()
    return None

# ---- Reminders CRUD ----

@router.post("/reminders", response_model=schemas.ReminderDetail, summary="Create a reminder", tags=["Reminders"])
def create_reminder(reminder: schemas.ReminderCreate, db: Session = Depends(get_db)):
    db_rem = models.Reminder(**reminder.dict())
    db.add(db_rem)
    db.commit()
    db.refresh(db_rem)
    return db_rem

@router.get("/reminders", response_model=List[schemas.ReminderDetail], summary="List reminders", tags=["Reminders"])
def list_reminders(customer_id: Optional[int] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Reminder)
    if customer_id:
        q = q.filter(models.Reminder.customer_id == customer_id)
    if status:
        q = q.filter(models.Reminder.status == status)
    return q.order_by(models.Reminder.created_at.desc()).all()

@router.put("/reminders/{reminder_id}", response_model=schemas.ReminderDetail, summary="Update reminder", tags=["Reminders"])
def update_reminder(reminder_id: int, reminder: schemas.ReminderCreate, db: Session = Depends(get_db)):
    db_rem = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not db_rem:
        raise HTTPException(status_code=404, detail="Reminder not found")
    for k, v in reminder.dict(exclude_unset=True).items():
        setattr(db_rem, k, v)
    db.commit()
    db.refresh(db_rem)
    return db_rem

@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete reminder", tags=["Reminders"])
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    db_rem = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not db_rem:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(db_rem)
    db.commit()
    return None

# ---- Analytics, Balance Sheet, Exports ----
# These endpoints demonstrate patterns -- expand analytics logic as needed.

@router.get("/analytics/frequent-purchases", summary="Top purchased items per customer", tags=["Analytics"])
def frequent_purchases(customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    from sqlalchemy import func
    q = db.query(
        models.InvoiceItem.product_name,
        func.count(models.InvoiceItem.id).label("times"),
        func.sum(models.InvoiceItem.quantity).label("total_qty"),
    )
    if customer_id:
        q = q.join(models.Invoice, models.Invoice.id == models.InvoiceItem.invoice_id)
        q = q.filter(models.Invoice.customer_id == customer_id)
    q = q.group_by(models.InvoiceItem.product_name).order_by(func.sum(models.InvoiceItem.quantity).desc())
    return [{"product_name": r.product_name, "times": r.times, "total_qty": r.total_qty} for r in q.all()]

@router.get("/balance-sheet", summary="Get customer balances", tags=["Reporting"])
def customer_balance(db: Session = Depends(get_db)):
    from sqlalchemy import func
    # Compute total outstanding per customer (total invoice - total paid)
    customers = db.query(models.Customer).all()
    balances = []
    for c in customers:
        inv_total = db.query(func.sum(models.Invoice.total_amount)).filter(models.Invoice.customer_id == c.id).scalar() or 0
        paid_total = db.query(func.sum(models.Payment.amount)).filter(models.Payment.customer_id == c.id).scalar() or 0
        balances.append({
            "customer_id": c.id,
            "customer": c.name,
            "total_invoiced": inv_total,
            "total_paid": paid_total,
            "outstanding": inv_total - paid_total
        })
    return balances

@router.get("/exports/balance-sheet", summary="Export balance sheet as CSV", tags=["Exports"])
def export_balance_sheet(db: Session = Depends(get_db)):
    import csv
    from fastapi.responses import StreamingResponse
    from io import StringIO
    data = customer_balance(db)
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["customer_id", "customer", "total_invoiced", "total_paid", "outstanding"])
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=balance_sheet.csv"})

# Add more analytics, export, dashboard endpoints as needed.
