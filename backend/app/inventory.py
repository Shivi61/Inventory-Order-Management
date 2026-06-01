from . import models

# Human-readable transaction types recorded in the inventory history.
PRODUCT_ADDED = "Product Added"
STOCK_UPDATED = "Stock Updated"
ORDER_CREATED = "Order Created"
ORDER_CANCELLED = "Order Cancelled"


def record_movement(db, product_id, quantity_changed, transaction_type, order_id=None):
    """Add an inventory transaction row. The caller commits."""
    if quantity_changed == 0:
        return
    db.add(
        models.InventoryTransaction(
            product_id=product_id,
            order_id=order_id,
            quantity_changed=quantity_changed,
            transaction_type=transaction_type,
        )
    )
