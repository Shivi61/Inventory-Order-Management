def _order(client, customer_id, product_id, qty):
    return client.post(
        "/api/v1/orders",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": qty}]},
    )


def test_order_reduces_stock_and_computes_total(client, product, customer):
    res = _order(client, customer["id"], product["id"], 3)
    assert res.status_code == 201
    assert float(res.json()["total_amount"]) == 28.5  # 3 * 9.5
    assert res.json()["status"] == "confirmed"

    remaining = client.get(f"/api/v1/products/{product['id']}").json()["quantity"]
    assert remaining == 2


def test_insufficient_stock_returns_400_message(client, product, customer):
    res = _order(client, customer["id"], product["id"], 99)
    assert res.status_code == 400
    assert res.json() == {"message": "Insufficient inventory"}


def test_cancel_restores_stock_and_keeps_record(client, product, customer):
    order = _order(client, customer["id"], product["id"], 4).json()
    assert client.delete(f"/api/v1/orders/{order['id']}").status_code == 204

    # Stock is back.
    assert client.get(f"/api/v1/products/{product['id']}").json()["quantity"] == 5
    # Order is preserved with a cancelled status.
    got = client.get(f"/api/v1/orders/{order['id']}").json()
    assert got["status"] == "cancelled"
    assert any(o["id"] == order["id"] for o in client.get("/api/v1/orders").json())


def test_status_transition(client, product, customer):
    order = _order(client, customer["id"], product["id"], 1).json()
    res = client.patch(f"/api/v1/orders/{order['id']}/status", json={"status": "completed"})
    assert res.status_code == 200
    assert res.json()["status"] == "completed"


def test_invalid_status_rejected(client, product, customer):
    order = _order(client, customer["id"], product["id"], 1).json()
    res = client.patch(f"/api/v1/orders/{order['id']}/status", json={"status": "shipped"})
    assert res.status_code == 400


def test_order_records_inventory_transactions(client, product, customer):
    order = _order(client, customer["id"], product["id"], 2).json()
    txns = client.get(f"/api/v1/inventory-transactions?product_id={product['id']}").json()
    order_txn = [t for t in txns if t["reason"] == "order"]
    assert order_txn and order_txn[0]["change"] == -2
