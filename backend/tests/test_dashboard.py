def test_dashboard_uses_camel_case(client, product, customer):
    res = client.get("/api/v1/dashboard")
    assert res.status_code == 200
    body = res.json()
    assert body["totalProducts"] == 1
    assert body["totalCustomers"] == 1
    assert body["totalOrders"] == 0
    # The Widget fixture has quantity 5, which is below the default threshold.
    assert len(body["lowStockProducts"]) == 1
