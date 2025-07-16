from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Enum, Boolean, func
from sqlalchemy.orm import relationship
from src.api.database import Base
from pydantic import BaseModel, Field
from typing import Optional, List
import enum
import datetime

# --- SQLAlchemy ORM MODELS ---

class PaymentModeEnum(enum.Enum):
    cash = "cash"
    card = "card"
    bank_transfer = "bank_transfer"
    cheque = "cheque"
    upi = "upi"
    other = "other"

class ReminderStatusEnum(enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"

# Customer Table
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    address = Column(Text, nullable=True)
    gstin = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    invoices = relationship("Invoice", back_populates="customer", cascade="all, delete")


# Product Table
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    hsn_sac = Column(String(20), nullable=True)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)

    invoice_items = relationship("InvoiceItem", back_populates="product")


# Invoice Table
class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), default="unpaid")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="invoices")
    invoice_items = relationship("InvoiceItem", back_populates="invoice")
    payments = relationship("Payment", back_populates="invoice")
    reminders = relationship("Reminder", back_populates="invoice")


# InvoiceItem Table
class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="invoice_items")
    product = relationship("Product", back_populates="invoice_items")


# Payment Table
class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    mode = Column(Enum(PaymentModeEnum), nullable=False)
    reference = Column(String(100), nullable=True)

    invoice = relationship("Invoice", back_populates="payments")


# Reminder Table
class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    sent_on = Column(DateTime, default=func.now())
    status = Column(Enum(ReminderStatusEnum), default=ReminderStatusEnum.pending)
    channel = Column(String(30), nullable=False)  # e.g., email, whatsapp, sms

    invoice = relationship("Invoice", back_populates="reminders")


# Analytics Table (for simple aggregation data/statistics)
class Analytics(Base):
    __tablename__ = "analytics"
    id = Column(Integer, primary_key=True, index=True)
    metric = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    collected_on = Column(Date, default=datetime.date.today)


# --- Pydantic MODELS for API ---

# Customer models
# PUBLIC_INTERFACE
class CustomerBase(BaseModel):
    name: str = Field(..., description="Customer name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Physical address")
    gstin: Optional[str] = Field(None, description="GSTIN (if applicable)")
    is_active: Optional[bool] = Field(True, description="Is the customer currently active?")

# PUBLIC_INTERFACE
class CustomerCreate(CustomerBase):
    pass

# PUBLIC_INTERFACE
class CustomerOut(CustomerBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

# Product models
# PUBLIC_INTERFACE
class ProductBase(BaseModel):
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    hsn_sac: Optional[str] = Field(None, description="HSN/SAC code")
    price: float = Field(..., description="Unit price")
    is_active: Optional[bool] = Field(True, description="Is the product enabled?")

# PUBLIC_INTERFACE
class ProductCreate(ProductBase):
    pass

# PUBLIC_INTERFACE
class ProductOut(ProductBase):
    id: int

    class Config:
        orm_mode = True

# Invoice/InvoiceItem models
# PUBLIC_INTERFACE
class InvoiceItemBase(BaseModel):
    product_id: int
    quantity: float
    rate: float
    amount: float

# PUBLIC_INTERFACE
class InvoiceItemCreate(InvoiceItemBase):
    pass

# PUBLIC_INTERFACE
class InvoiceItemOut(InvoiceItemBase):
    id: int

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class InvoiceBase(BaseModel):
    invoice_number: str
    customer_id: int
    invoice_date: datetime.date
    due_date: datetime.date
    total_amount: float
    status: Optional[str] = "unpaid"

# PUBLIC_INTERFACE
class InvoiceCreate(InvoiceBase):
    invoice_items: List[InvoiceItemCreate]

# PUBLIC_INTERFACE
class InvoiceOut(InvoiceBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    invoice_items: List[InvoiceItemOut] = []
    payments: List['PaymentOut'] = []
    reminders: List['ReminderOut'] = []

    class Config:
        orm_mode = True

# Payment models
# PUBLIC_INTERFACE
class PaymentBase(BaseModel):
    invoice_id: int
    payment_date: datetime.date
    amount: float
    mode: PaymentModeEnum
    reference: Optional[str] = None

# PUBLIC_INTERFACE
class PaymentCreate(PaymentBase):
    pass

# PUBLIC_INTERFACE
class PaymentOut(PaymentBase):
    id: int

    class Config:
        orm_mode = True

# Reminder models
# PUBLIC_INTERFACE
class ReminderBase(BaseModel):
    invoice_id: int
    channel: str
    status: ReminderStatusEnum = ReminderStatusEnum.pending
    sent_on: Optional[datetime.datetime] = None

# PUBLIC_INTERFACE
class ReminderCreate(ReminderBase):
    pass

# PUBLIC_INTERFACE
class ReminderOut(ReminderBase):
    id: int

    class Config:
        orm_mode = True

# Analytics models
# PUBLIC_INTERFACE
class AnalyticsBase(BaseModel):
    metric: str
    value: float
    collected_on: Optional[datetime.date] = None

# PUBLIC_INTERFACE
class AnalyticsCreate(AnalyticsBase):
    pass

# PUBLIC_INTERFACE
class AnalyticsOut(AnalyticsBase):
    id: int

    class Config:
        orm_mode = True

# For self-referencing of nested response models
InvoiceOut.update_forward_refs()
