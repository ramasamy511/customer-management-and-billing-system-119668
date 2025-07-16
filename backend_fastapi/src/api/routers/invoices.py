from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional

from src.api import models
from src.api.database import get_db

router = APIRouter()

# PUBLIC_INTERFACE
@router.get("/", response_model=List[models.InvoiceOut], summary="List invoices", description="Get all invoices. Can filter by customer or status.")
def list_invoices(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    status_: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Invoice)
    if customer_id:
        query = query.filter(models.Invoice.customer_id == customer_id)
    if status_:
        query = query.filter(models.Invoice.status == status_)
    results = query.order_by(models.Invoice.invoice_date.desc()).all()
    return results

# PUBLIC_INTERFACE
@router.get("/{invoice_id}", response_model=models.InvoiceOut, summary="Get invoice details with items/payments/reminders")
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


# PUBLIC_INTERFACE
@router.post("/", response_model=models.InvoiceOut, status_code=status.HTTP_201_CREATED, summary="Create invoice (with items)")
def create_invoice(
    invoice: models.InvoiceCreate,
    db: Session = Depends(get_db)
):
    db_invoice = models.Invoice(
        invoice_number=invoice.invoice_number,
        customer_id=invoice.customer_id,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        total_amount=invoice.total_amount,
        status=invoice.status or "unpaid"
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    # Add items
    for item in invoice.invoice_items:
        db_item = models.InvoiceItem(
            invoice_id=db_invoice.id,
            product_id=item.product_id,
            quantity=item.quantity,
            rate=item.rate,
            amount=item.amount,
        )
        db.add(db_item)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

# PUBLIC_INTERFACE
@router.put("/{invoice_id}", response_model=models.InvoiceOut, summary="Update invoice main details (not items)")
def update_invoice(
    invoice_id: int,
    body: models.InvoiceBase,
    db: Session = Depends(get_db)
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    for key, value in body.dict(exclude_unset=True).items():
        setattr(invoice, key, value)
    db.commit()
    db.refresh(invoice)
    return invoice

# PUBLIC_INTERFACE
@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete invoice and all items/payments/reminders")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(invoice)
    db.commit()
    return None

# PUBLIC_INTERFACE
@router.get("/export/", summary="Export invoices (PDF/Excel)", description="Export invoices as PDF or Excel. Returns as streaming content.")
def export_invoices(
    export_type: str = Query("pdf", enum=["pdf", "excel"], description="Export type"),
    db: Session = Depends(get_db)
):
    # Dummy content as placeholder for PDF/Excel export logic
    if export_type == "pdf":
        content = b"%PDF-1.4 Dummy PDF Content"
        media_type = "application/pdf"
        filename = "invoices.pdf"
    else:
        content = b"Dummy,Excel,Content\n1,2,3\n"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "invoices.xlsx"
    return Response(content, media_type=media_type, headers={"Content-Disposition": f"attachment;filename={filename}"})

# PUBLIC_INTERFACE
@router.get("/balancesheet/", summary="Balance sheet (filtered/report)", description="Retrieve balances with optional date/customer filters.")
def balance_sheet(
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Invoice)
    if from_date:
        query = query.filter(models.Invoice.invoice_date >= from_date)
    if to_date:
        query = query.filter(models.Invoice.invoice_date <= to_date)
    if customer_id:
        query = query.filter(models.Invoice.customer_id == customer_id)
    # Paid and outstanding amounts
    invoices = query.all()
    report = []
    for inv in invoices:
        total_paid = sum(p.amount for p in inv.payments)
        report.append({
            "invoice_id": inv.id,
            "customer": inv.customer.name,
            "invoice_date": inv.invoice_date,
            "due_date": inv.due_date,
            "total_amount": inv.total_amount,
            "paid_amount": total_paid,
            "outstanding": max(0.0, inv.total_amount - total_paid),
            "status": inv.status,
        })
    return report
