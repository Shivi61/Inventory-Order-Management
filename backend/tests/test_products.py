def test_create_and_get_product(client):
    res = client.post(
        "/api/v1/products",
        json={"name": "Gadget", "sku": "G1", "price": 12, "quantity": 3},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["sku"] == "G1"
    assert "updated_at" in body

    got = client.get(f"/api/v1/products/{body['id']}")
    assert got.status_code == 200


def test_duplicate_sku_rejected(client, product):
    res = client.post(
        "/api/v1/products",
        json={"name": "Other", "sku": "W1", "price": 1, "quantity": 1},
    )
    assert res.status_code == 409


def test_price_must_be_positive(client):
    res = client.post(
        "/api/v1/products",
        json={"name": "Free", "sku": "F1", "price": 0, "quantity": 1},
    )
    assert res.status_code == 422


def test_negative_quantity_rejected(client):
    res = client.post(
        "/api/v1/products",
        json={"name": "Bad", "sku": "B1", "price": 1, "quantity": -1},
    )
    assert res.status_code == 422


def test_list_is_paginated(client):
    for i in range(3):
        client.post(
            "/api/v1/products",
            json={"name": f"P{i}", "sku": f"S{i}", "price": 1, "quantity": 1},
        )
    res = client.get("/api/v1/products?page=1&page_size=2")
    body = res.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["page"] == 1


def test_search_filters_by_name(client):
    client.post("/api/v1/products", json={"name": "Apple", "sku": "A1", "price": 1, "quantity": 1})
    client.post("/api/v1/products", json={"name": "Banana", "sku": "B1", "price": 1, "quantity": 1})
    res = client.get("/api/v1/products?search=appl")
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Apple"


def test_soft_delete_hides_product(client, product):
    assert client.delete(f"/api/v1/products/{product['id']}").status_code == 204
    assert client.get(f"/api/v1/products/{product['id']}").status_code == 404
    assert client.get("/api/v1/products").json()["total"] == 0


def test_quantity_change_records_transaction(client, product):
    client.put(f"/api/v1/products/{product['id']}", json={"quantity": 8})
    txns = client.get(f"/api/v1/inventory-transactions?product_id={product['id']}").json()
    reasons = {t["reason"] for t in txns}
    assert "initial" in reasons
    assert "adjustment" in reasons
