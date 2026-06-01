from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .. import inventory, models, schemas
from ..database import get_db

router = APIRouter(prefix="/orders", tags=["orders"])


def _serialize(order: models.Order) -> dict:
    """Build the response shape, including the product name on each line."""
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else None,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in order.items
        ],
    }


def _cancel(db: Session, order: models.Order) -> None:
    """Mark an order cancelled and return its items to stock (once)."""
    if order.status == "cancelled":
        return
    for item in order.items:
        product = db.get(models.Product, item.product_id)
        if product is not None:
            product.quantity += item.quantity
            inventory.record_movement(
                db, product.id, item.quantity, inventory.ORDER_CANCELLED, order_id=order.id
            )
    order.status = "cancelled"


@router.post("", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: schemas.OrderCreate, db: Session = Depends(get_db)):
    customer = db.get(models.Customer, payload.customer_id)
    if customer is None or customer.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Merge duplicate product lines so quantities are checked together.
    requested: dict[UUID, int] = {}
    for item in payload.items:
        requested[item.product_id] = requested.get(item.product_id, 0) + item.quantity

    order = models.Order(customer_id=customer.id, total_amount=0, status="confirmed")
    total = 0

    for product_id, qty in requested.items():
        product = db.get(models.Product, product_id)
        if product is None or product.deleted_at is not None:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        if product.quantity < qty:
            # Spec-defined error shape for insufficient stock.
            return JSONResponse(status_code=400, content={"message": "Insufficient inventory"})

        product.quantity -= qty
        total += product.price * qty
        order.items.append(
            models.OrderItem(product_id=product.id, quantity=qty, unit_price=product.price)
        )

    order.total_amount = total
    db.add(order)
    db.flush()  # need the order id before logging stock movements
    for product_id, qty in requested.items():
        inventory.record_movement(db, product_id, -qty, inventory.ORDER_CREATED, order_id=order.id)

    db.commit()
    db.refresh(order)
    return _serialize(order)


@router.get("", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return [_serialize(o) for o in orders]


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: UUID, db: Session = Depends(get_db)):
    order = db.get(models.Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize(order)


@router.patch("/{order_id}/status", response_model=schemas.OrderOut)
def update_status(
    order_id: UUID, payload: schemas.OrderStatusUpdate, db: Session = Depends(get_db)
):
    order = db.get(models.Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if payload.status not in models.ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid order status")

    if payload.status == "cancelled":
        _cancel(db, order)
    else:
        order.status = payload.status

    db.commit()
    db.refresh(order)
    return _serialize(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(order_id: UUID, db: Session = Depends(get_db)):
    # "Deleting" an order cancels it: the record is kept for history and the
    # reserved stock is returned.
    order = db.get(models.Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    _cancel(db, order)
    db.commit()
