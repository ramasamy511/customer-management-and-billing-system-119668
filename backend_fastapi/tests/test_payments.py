import datetime

def seed_invoice(client):
    from tests.test_invoices import seed_customer
    cust_id = seed_customer(client)
    # Seed a product
    from src.api.models import Product
    from src.api.database import get_db
    db = list(client.app.dependency_overrides[get_db]())[0]
    db.add(Product(name="PayProd", price=400.0))
    db.commit()
    # Create invoice
    invoice_payload = {
        "invoice_number": "PAYINV001",
        "customer_id": cust_id,
        "invoice_date": datetime.date.today().isoformat(),
        "due_date": (datetime.date.today() + datetime.timedelta(days=15)).isoformat(),
        "total_amount": 400.0,
        "status": "unpaid",
        "invoice_items": [
            {
                "product_id": 1,
                "quantity": 1,
                "rate": 400.0,
                "amount": 400.0,
            }
        ]
    }
    inv_resp = client.post("/invoices/", json=invoice_payload)
    return inv_resp.json()["id"]

def test_create_payment(client):
    inv_id = seed_invoice(client)
    payment_payload = {
        "invoice_id": inv_id,
        "payment_date": datetime.date.today().isoformat(),
        "amount": 400.0,
        "mode": "cash",
        "reference": "abc123"
    }
    r = client.post("/payments/", json=payment_payload)
    assert r.status_code == 201
    data = r.json()
    assert data["amount"] == 400.0

def test_reject_future_payment_date(client):
    inv_id = seed_invoice(client)
    future_date = (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
    payment_payload = {
        "invoice_id": inv_id,
        "payment_date": future_date,
        "amount": 111.0,
        "mode": "upi",
        "reference": None
    }
    r = client.post("/payments/", json=payment_payload)
    assert r.status_code == 400
