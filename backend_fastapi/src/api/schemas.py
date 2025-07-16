from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# --- Customer ---
# PUBLIC_INTERFACE
class CustomerBase(BaseModel):
    name: str = Field(..., description="Customer name")
    email: Optional[str] = Field(None, description="Email")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Address")
    gst_number: Optional[str] = Field(None, description="GST number")

# PUBLIC_INTERFACE
class CustomerCreate(CustomerBase):
    pass

# PUBLIC_INTERFACE
class CustomerUpdate(CustomerBase):
    pass

# PUBLIC_INTERFACE
class CustomerDetail(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# --- Invoice Items ---
# PUBLIC_INTERFACE
class InvoiceItemBase(BaseModel):
    product_name: str = Field(..., description="Product/Service Name")
    quantity: float = Field(..., description="Quantity")
    unit_price: float = Field(..., description="Unit Price")
    amount: float = Field(..., description="Total Line Amount")

# PUBLIC_INTERFACE
class InvoiceItemCreate(InvoiceItemBase):
    pass

# PUBLIC_INTERFACE
class InvoiceItemDetail(InvoiceItemBase):
    id: int

    class Config:
        orm_mode = True

# --- Invoice Header ---
# PUBLIC_INTERFACE
class InvoiceBase(BaseModel):
    customer_id: int
    invoice_date: Optional[datetime]
    due_date: Optional[datetime]
    status: Optional[str]
    total_amount: float = Field(..., description="Total Invoice Amount")
    remark: Optional[str]

# PUBLIC_INTERFACE
class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]

# PUBLIC_INTERFACE
class InvoiceUpdate(InvoiceBase):
    items: Optional[List[InvoiceItemCreate]]

# PUBLIC_INTERFACE
class InvoiceDetail(InvoiceBase):
    id: int
    items: List[InvoiceItemDetail]
    created_at: datetime

    class Config:
        orm_mode = True

# --- Payments ---
# PUBLIC_INTERFACE
class PaymentBase(BaseModel):
    customer_id: int
    invoice_id: Optional[int]
    payment_date: Optional[datetime]
    mode: Optional[str]
    amount: float
    remark: Optional[str]

# PUBLIC_INTERFACE
class PaymentCreate(PaymentBase):
    pass

# PUBLIC_INTERFACE
class PaymentUpdate(PaymentBase):
    pass

# PUBLIC_INTERFACE
class PaymentDetail(PaymentBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# --- Reminders ---
# PUBLIC_INTERFACE
class ReminderBase(BaseModel):
    customer_id: int
    invoice_id: Optional[int]
    message: str
    status: Optional[str]
    sent_at: Optional[datetime]

# PUBLIC_INTERFACE
class ReminderCreate(ReminderBase):
    pass

# PUBLIC_INTERFACE
class ReminderDetail(ReminderBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# --- Analytics / Exports ---
# Define analytics and export response schemas as needed.
# For quick demo/API: analytics and export endpoints can return a list of dict or minimal typed data.
