from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# PUBLIC_INTERFACE
class Customer(Base):
    """Customer Master Table."""
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=True)
    phone = Column(String(32), nullable=True)
    address = Column(Text, nullable=True)
    gst_number = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    invoices = relationship("Invoice", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")

# PUBLIC_INTERFACE
class Invoice(Base):
    """Sales Invoice header."""
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), default='unpaid')  # unpaid, paid, partial
    total_amount = Column(Float, nullable=False)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")

# PUBLIC_INTERFACE
class InvoiceItem(Base):
    """Items under Invoice."""
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_name = Column(String(128), nullable=False)
    quantity = Column(Float, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, default=0)
    amount = Column(Float, nullable=False)
    invoice = relationship("Invoice", back_populates="items")

# PUBLIC_INTERFACE
class Payment(Base):
    """Payment/Receipt against invoice or customer."""
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    mode = Column(String(64), nullable=True)  # cash, card, online, cheque,...
    amount = Column(Float, nullable=False)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    invoice = relationship("Invoice", back_populates="payments")
    customer = relationship("Customer", back_populates="payments")

# PUBLIC_INTERFACE
class Reminder(Base):
    """Reminders for payment/notification purposes."""
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(32), default='pending')  # pending, sent, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
