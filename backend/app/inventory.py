from . import models


def record_movement(db, product_id, change, reason, order_id=None):
    """Add an inventory transaction row. The caller commits."""
    if change == 0:
        return
    db.add(
        models.InventoryTransaction(
            product_id=product_id,
            order_id=order_id,
            change=change,
            reason=reason,
        )
    )
