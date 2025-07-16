from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import router as api_router

tags_metadata = [
    {"name": "Customers", "description": "Manage customer master records."},
    {"name": "Invoices", "description": "Manage sales invoices and line items."},
    {"name": "Payments", "description": "Record payments."},
    {"name": "Reminders", "description": "Send and track reminders."},
    {"name": "Analytics", "description": "View analytics and dashboards."},
    {"name": "Exports", "description": "Export data in various formats."},
    {"name": "Reporting", "description": "View balance sheet and reports."},
]

app = FastAPI(
    title="Customer Management and Billing System API",
    description="API for managing customers, invoices, billing, payments, analytics, and reminders.",
    version="1.0.0",
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Create tables if not present
    Base.metadata.create_all(bind=engine)

app.include_router(api_router)

@app.get("/", tags=["Health"])
def health_check():
    """Health Check endpoint."""
    return {"message": "Healthy"}
