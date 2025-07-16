from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.api import models
from src.api.database import get_db

router = APIRouter()

# PUBLIC_INTERFACE
@router.get("/", response_model=List[models.CustomerOut], summary="List customers", description="Get all customers (with optional search).")
def list_customers(
    q: Optional[str] = Query(None, description="Search by name/email/phone"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Customer)
    if q:
        q_filter = "%{}%".format(q)
        query = query.filter(
            (models.Customer.name.ilike(q_filter)) |
            (models.Customer.email.ilike(q_filter)) |
            (models.Customer.phone.ilike(q_filter))
        )
    results = query.order_by(models.Customer.created_at.desc()).all()
    return results

# PUBLIC_INTERFACE
@router.post("/", response_model=models.CustomerOut, status_code=status.HTTP_201_CREATED, summary="Create customer")
def create_customer(
    customer: models.CustomerCreate,
    db: Session = Depends(get_db)
):
    if db.query(models.Customer).filter(models.Customer.email == customer.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    db_obj = models.Customer(**customer.dict(exclude_unset=True))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# PUBLIC_INTERFACE
@router.get("/{customer_id}", response_model=models.CustomerOut, summary="Get customer details")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# PUBLIC_INTERFACE
@router.put("/{customer_id}", response_model=models.CustomerOut, summary="Update customer details")
def update_customer(
    customer_id: int,
    data: models.CustomerCreate,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer

# PUBLIC_INTERFACE
@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete customer")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
    return None
