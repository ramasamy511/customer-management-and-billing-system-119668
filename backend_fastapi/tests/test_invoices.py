import datetime


def seed_customer(client):
    resp = client.post(
        "/customers/", 
        json={
            "name": "Invoice Customer",
            "email": "invcust@example.com",
            "phone": "8888888888",
            "address": "",
            "gstin": "",
            "is_active": True,
        }
    )
    return resp.json()["id"]


def test_create_invoice_and_get(client):
    # Seed customer
    cust_id = seed_customer(client)

    # Invoice payload with 1 item
    invoice_payload = {
        "invoice_number": "INV001",
        "customer_id": cust_id,
        "invoice_date": datetime.date.today().isoformat(),
        "due_date": (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
        "total_amount": 1000.0,
        "status": "unpaid",
        "invoice_items": [
            {
                "product_id": 1,
                "quantity": 2,
                "rate": 500.0,
                "amount": 1000.0,
            }
        ]
    }

    # Pre-seed a product
    from src.api.models import Product
    from src.api.database import get_db
    product_resp = client.app.dependency_overrides[get_db]
    db = list(product_resp())[0]
    db.add(Product(name="Test Product", price=500.0))
    db.commit()

    r = client.post("/invoices/", json=invoice_payload)
    assert r.status_code == 201
    data = r.json()
    assert data["invoice_number"] == "INV001"

    # Get invoice
    resp = client.get(f"/invoices/{data['id']}")
    assert resp.status_code == 200
    assert resp.json()["invoice_number"] == "INV001"

