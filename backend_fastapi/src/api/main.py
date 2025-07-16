from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import (
    customers,
    invoices,
    payments,
    analytics,
    reminders,
)

app = FastAPI(
    title="Customer Management & Billing API",
    version="1.0.0",
    description="API backend for managing customers, invoices, payments, reporting, analytics, reminders, and data export."
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route
@app.get("/", tags=["Health"])
def health_check():
    """API health check endpoint"""
    return {"message": "Healthy"}

# Register routers
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])
