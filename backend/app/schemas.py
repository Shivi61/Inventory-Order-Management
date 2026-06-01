from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel


# ---- Product ----
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    sku: str = Field(..., min_length=1, max_length=60)
    price: Decimal = Field(..., gt=0)
    quantity: int = Field(..., ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    sku: Optional[str] = Field(None, min_length=1, max_length=60)
    price: Optional[Decimal] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)


class ProductOut(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductPage(BaseModel):
    """Paginated list of products."""

    items: List[ProductOut]
    total: int
    page: int
    page_size: int


# ---- Customer ----
class CustomerCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)


class CustomerOut(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---- Order ----
class OrderItemIn(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_id: UUID
    items: List[OrderItemIn] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: str


class OrderItemOut(BaseModel):
    product_id: UUID
    product_name: Optional[str] = None
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    id: UUID
    customer_id: UUID
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemOut]

    model_config = ConfigDict(from_attributes=True)


# ---- Inventory transactions ----
class InventoryTransactionOut(BaseModel):
    id: UUID
    product_id: UUID
    order_id: Optional[UUID]
    quantity_changed: int
    transaction_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---- Dashboard (camelCase to match the spec) ----
class DashboardSummary(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    total_products: int
    total_customers: int
    total_orders: int
    # Count of low-stock products (matches the documented dashboard contract).
    low_stock_products: int
    # The actual low-stock products, used to render the dashboard table.
    low_stock_items: List[ProductOut]
