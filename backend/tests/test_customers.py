def test_create_customer(client):
    res = client.post(
        "/api/v1/customers",
        json={"full_name": "Ann", "email": "ann@example.com"},
    )
    assert res.status_code == 201
    assert res.json()["email"] == "ann@example.com"


def test_duplicate_email_rejected(client, customer):
    res = client.post(
        "/api/v1/customers",
        json={"full_name": "Jo Two", "email": "jo@example.com"},
    )
    assert res.status_code == 409


def test_invalid_email_rejected(client):
    res = client.post(
        "/api/v1/customers",
        json={"full_name": "Bad", "email": "not-an-email"},
    )
    assert res.status_code == 422


def test_soft_delete_hides_customer(client, customer):
    assert client.delete(f"/api/v1/customers/{customer['id']}").status_code == 204
    assert client.get(f"/api/v1/customers/{customer['id']}").status_code == 404
    assert client.get("/api/v1/customers").json() == []
