import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from .database import Base
from .db_types import GUID


def _uuid():
    return uuid.uuid4()


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="quantity_non_negative"),
        CheckConstraint("price > 0", name="price_positive"),
    )

    id = Column(GUID(), primary_key=True, default=_uuid)
    name = Column(String(150), nullable=False, index=True)
    sku = Column(String(60), nullable=False, unique=True, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(GUID(), primary_key=True, default=_uuid)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    phone = Column(String(30))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)


# Allowed order states.
ORDER_STATUSES = ("pending", "confirmed", "completed", "cancelled")


class Order(Base):
    __tablename__ = "orders"

    id = Column(GUID(), primary_key=True, default=_uuid)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer")
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(GUID(), primary_key=True, default=_uuid)
    order_id = Column(GUID(), ForeignKey("orders.id"), nullable=False)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    # Price captured when the order was placed, so later price changes don't
    # rewrite history.
    unit_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class InventoryTransaction(Base):
    """A record of every stock movement, for auditing/history."""

    __tablename__ = "inventory_transactions"

    id = Column(GUID(), primary_key=True, default=_uuid)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=False)
    order_id = Column(GUID(), ForeignKey("orders.id"), nullable=True)
    # Positive when stock goes up, negative when it goes down.
    change = Column(Integer, nullable=False)
    # initial | adjustment | order | cancellation
    reason = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")
