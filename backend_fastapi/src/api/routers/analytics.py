from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api import models
from src.api.database import get_db

router = APIRouter()

# PUBLIC_INTERFACE
@router.get("/frequent", summary="Frequent purchase analytics per customer", description="Returns list of customers with frequent purchases and stats.")
def frequent_purchases(
    limit: int = Query(10, description="Number of customers"),
    db: Session = Depends(get_db)
):
    # Simple aggregation: most invoices per customer
    raw = (
        db.query(
            models.Customer.id,
            models.Customer.name,
            models.Customer.email,
            models.Customer.phone,
            db.func.count(models.Invoice.id).label("num_invoices"),
        )
        .join(models.Invoice, models.Customer.id == models.Invoice.customer_id)
        .group_by(models.Customer.id)
        .order_by(db.func.count(models.Invoice.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r[0],
            "name": r[1],
            "email": r[2],
            "phone": r[3],
            "num_invoices": r[4],
        }
        for r in raw
    ]

# PUBLIC_INTERFACE
@router.get("/dashboard", summary="Dashboard stats", description="Get outstanding customers, best buyer, and top products.")
def get_dashboard(
    db: Session = Depends(get_db)
):
    # Outstanding customers (by total outstanding)
    outstanding_raw = (
        db.query(
            models.Customer.id,
            models.Customer.name,
            db.func.sum(models.Invoice.total_amount).label("total_invoiced"),
            db.func.coalesce(db.func.sum(models.Payment.amount), 0).label("total_paid")
        )
        .join(models.Invoice, models.Customer.id == models.Invoice.customer_id)
        .outerjoin(models.Payment, models.Invoice.id == models.Payment.invoice_id)
        .group_by(models.Customer.id)
        .all()
    )
    outstanding = [
        {
            "customer_id": r[0],
            "name": r[1],
            "total_invoiced": float(r[2] or 0),
            "total_paid": float(r[3] or 0),
            "outstanding": max(0.0, float(r[2] or 0) - float(r[3] or 0)),
        }
        for r in outstanding_raw if (r[2] or 0) - (r[3] or 0) > 0
    ]
    # Best buyer (max paid)
    best_buyer_raw = sorted(outstanding_raw, key=lambda x: float(x[3] or 0), reverse=True)
    best_buyer = {
        "id": best_buyer_raw[0][0],
        "name": best_buyer_raw[0][1],
        "total_paid": float(best_buyer_raw[0][3] or 0)
    } if best_buyer_raw else {}

    # Top product by sales amount
    top_products_raw = (
        db.query(
            models.Product.id,
            models.Product.name,
            db.func.sum(models.InvoiceItem.amount).label("sales_amt")
        )
        .join(models.InvoiceItem, models.Product.id == models.InvoiceItem.product_id)
        .group_by(models.Product.id)
        .order_by(db.func.sum(models.InvoiceItem.amount).desc())
        .limit(5)
        .all()
    )
    top_products = [{"id": r[0], "name": r[1], "sales_amount": float(r[2] or 0)} for r in top_products_raw]
    return {
        "outstanding_customers": outstanding,
        "best_buyer": best_buyer,
        "top_products": top_products,
    }
