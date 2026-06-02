def test_unversioned_get_redirects(client):
    res = client.get("/products", follow_redirects=False)
    assert res.status_code == 307
    assert res.headers["location"] == "/api/v1/products"


def test_unversioned_get_redirect_followed(client):
    # TestClient follows redirects by default, so this should reach the API.
    res = client.get("/products")
    assert res.status_code == 200
    assert "items" in res.json()


def test_unversioned_post_keeps_body(client):
    # A 307 preserves the method and body, so the product is created.
    res = client.post(
        "/products",
        json={"name": "Redirected", "sku": "RD-1", "price": 5, "quantity": 2},
    )
    assert res.status_code == 201
    assert res.json()["sku"] == "RD-1"


def test_query_string_is_preserved(client):
    res = client.get("/products?search=nothing", follow_redirects=False)
    assert res.headers["location"] == "/api/v1/products?search=nothing"


def test_versioned_path_still_works(client):
    assert client.get("/api/v1/products").status_code == 200
