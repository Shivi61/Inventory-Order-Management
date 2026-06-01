"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-06-01

"""
import sqlalchemy as sa
from alembic import op

from app.db_types import GUID

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "products",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("sku", sa.String(length=60), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("quantity >= 0", name="quantity_non_negative"),
        sa.CheckConstraint("price > 0", name="price_positive"),
    )
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)
    op.create_index("ix_products_name", "products", ["name"])

    op.create_table(
        "customers",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_customers_email", "customers", ["email"], unique=True)

    op.create_table(
        "orders",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("customer_id", GUID(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "order_items",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("order_id", GUID(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("product_id", GUID(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
    )

    op.create_table(
        "inventory_transactions",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("product_id", GUID(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("order_id", GUID(), sa.ForeignKey("orders.id"), nullable=True),
        sa.Column("change", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table("inventory_transactions")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_index("ix_customers_email", table_name="customers")
    op.drop_table("customers")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_index("ix_products_sku", table_name="products")
    op.drop_table("products")
