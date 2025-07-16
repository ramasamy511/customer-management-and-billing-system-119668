import datetime

def seed_invoice_for_reminder(client):
    from tests.test_invoices import seed_customer
    cust_id = seed_customer(client)
    from src.api.models import Product
    from src.api.database import get_db
    db = list(client.app.dependency_overrides[get_db]())[0]
    db.add(Product(name="RemindProd", price=123.0))
    db.commit()
    invoice_payload = {
        "invoice_number": "REM001",
        "customer_id": cust_id,
        "invoice_date": datetime.date.today().isoformat(),
        "due_date": (datetime.date.today() + datetime.timedelta(days=3)).isoformat(),
        "total_amount": 100.0,
        "status": "unpaid",
        "invoice_items": [
            {
                "product_id": 1,
                "quantity": 1,
                "rate": 100.0,
                "amount": 100.0,
            }
        ]
    }
    inv_resp = client.post("/invoices/", json=invoice_payload)
    return inv_resp.json()["id"], cust_id

def test_list_reminders_empty(client):
    r = client.get("/reminders/")
    assert r.status_code == 200
    assert r.json() == []

def test_send_reminder_email(client, monkeypatch):
    inv_id, cust_id = seed_invoice_for_reminder(client)
    # patch integrations.send_email_reminder to avoid SMTP attempt
    import src.api.integrations as integrations
    monkeypatch.setattr(integrations, "send_email_reminder", lambda a, b, c: None)
    payload = {
        "invoice_id": inv_id,
        "channel": "email"
    }
    r = client.post("/reminders/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["status"] in ("sent", "failed")

def test_send_reminder_unsupported(client):
    inv_id, _ = seed_invoice_for_reminder(client)
    payload = {
        "invoice_id": inv_id,
        "channel": "sms"
    }
    r = client.post("/reminders/", json=payload)
    assert r.status_code == 422
