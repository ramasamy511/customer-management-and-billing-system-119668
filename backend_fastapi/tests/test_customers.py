

def make_customer_payload(name="Alice", email="alice@example.com", phone="1234567890"):
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "address": "Street 123",
        "gstin": None,
        "is_active": True,
    }


def test_create_and_get_customer(client):
    # Create a customer
    payload = make_customer_payload()
    response = client.post("/customers/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["email"] == "alice@example.com"

    # Get the customer by ID
    cid = data["id"]
    get_resp = client.get(f"/customers/{cid}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Alice"


def test_duplicate_email_is_rejected(client):
    # Create customer
    payload = make_customer_payload(email="dup@example.com")
    r1 = client.post("/customers/", json=payload)
    assert r1.status_code == 201

    # Attempt to create again
    r2 = client.post("/customers/", json=payload)
    assert r2.status_code == 409


def test_update_and_delete_customer(client):
    payload = make_customer_payload(name="ToUpdate", email="up@d.com")
    r = client.post("/customers/", json=payload)
    cid = r.json()["id"]

    # Update
    up_payload = make_customer_payload(name="Updated Name", email="up@d.com")
    up_resp = client.put(f"/customers/{cid}", json=up_payload)
    assert up_resp.status_code == 200
    assert up_resp.json()["name"] == "Updated Name"

    # Delete
    del_resp = client.delete(f"/customers/{cid}")
    assert del_resp.status_code == 204

    # Ensure deleted
    get_resp = client.get(f"/customers/{cid}")
    assert get_resp.status_code == 404
