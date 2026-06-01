"""Populate the database with some sample data.

Run it after migrations:

    python -m app.seed              # local
    docker compose exec backend python -m app.seed

It is safe to run more than once: if products already exist it does nothing.
"""
from . import inventory, models
from .database import SessionLocal

PRODUCTS = [
    {"name": "Wireless Mouse", "sku": "WM-001", "price": 19.99, "quantity": 150},
    {"name": "Mechanical Keyboard", "sku": "KB-100", "price": 79.50, "quantity": 40},
    {"name": "USB-C Cable", "sku": "UC-220", "price": 9.99, "quantity": 8},
    {"name": '27" Monitor', "sku": "MON-27", "price": 229.00, "quantity": 12},
    {"name": "Laptop Stand", "sku": "LS-330", "price": 34.95, "quantity": 5},
    {"name": "1080p Webcam", "sku": "WC-108", "price": 49.00, "quantity": 60},
]

CUSTOMERS = [
    {"full_name": "Aarav Sharma", "email": "aarav@example.com", "phone": "+91 90000 11111"},
    {"full_name": "Priya Patel", "email": "priya@example.com", "phone": "+91 90000 22222"},
    {"full_name": "Liam Johnson", "email": "liam@example.com", "phone": "+1 415 555 0101"},
]

# Each order: customer index, then (product index, quantity) pairs.
ORDERS = [
    (0, [(0, 2), (1, 1)]),
    (1, [(3, 1), (5, 2)]),
]


def run():
    db = SessionLocal()
    try:
        if db.query(models.Product).count() > 0:
            print("Database already has products, skipping seed.")
            return

        products = []
        for data in PRODUCTS:
            p = models.Product(**data)
            db.add(p)
            db.flush()
            inventory.record_movement(db, p.id, p.quantity, inventory.PRODUCT_ADDED)
            products.append(p)

        customers = []
        for data in CUSTOMERS:
            c = models.Customer(**data)
            db.add(c)
            customers.append(c)
        db.flush()

        for customer_idx, items in ORDERS:
            order = models.Order(customer_id=customers[customer_idx].id, status="confirmed")
            total = 0
            for product_idx, qty in items:
                product = products[product_idx]
                product.quantity -= qty
                total += product.price * qty
                order.items.append(
                    models.OrderItem(product_id=product.id, quantity=qty, unit_price=product.price)
                )
            order.total_amount = total
            db.add(order)
            db.flush()
            for product_idx, qty in items:
                inventory.record_movement(
                    db, products[product_idx].id, -qty, inventory.ORDER_CREATED, order_id=order.id
                )

        db.commit()
        print(
            f"Seeded {len(products)} products, {len(customers)} customers, "
            f"{len(ORDERS)} orders."
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
