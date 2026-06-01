import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    # Each test gets a fresh in-memory SQLite database.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def product(client):
    res = client.post(
        "/api/v1/products",
        json={"name": "Widget", "sku": "W1", "price": 9.5, "quantity": 5},
    )
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def customer(client):
    res = client.post(
        "/api/v1/customers",
        json={"full_name": "Jo", "email": "jo@example.com", "phone": "123"},
    )
    assert res.status_code == 201
    return res.json()
