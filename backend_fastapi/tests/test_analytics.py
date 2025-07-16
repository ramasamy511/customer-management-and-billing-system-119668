def test_frequent_purchases_basic(client):
    r = client.get("/analytics/frequent")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_dashboard_empty(client):
    r = client.get("/analytics/dashboard")
    assert r.status_code == 200
    result = r.json()
    assert "outstanding_customers" in result
    assert "best_buyer" in result
    assert "top_products" in result
