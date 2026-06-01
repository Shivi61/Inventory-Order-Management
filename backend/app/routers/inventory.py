from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/inventory-transactions", tags=["inventory"])


@router.get("", response_model=list[schemas.InventoryTransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    product_id: UUID | None = Query(None, description="Filter by product"),
):
    query = db.query(models.InventoryTransaction)
    if product_id:
        query = query.filter(models.InventoryTransaction.product_id == product_id)
    return query.order_by(models.InventoryTransaction.created_at.desc()).all()
