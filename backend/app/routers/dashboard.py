from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import LOW_STOCK_THRESHOLD
from ..database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=schemas.DashboardSummary)
def summary(db: Session = Depends(get_db)):
    active_products = db.query(models.Product).filter(models.Product.deleted_at.is_(None))
    low_stock = (
        active_products.filter(models.Product.quantity <= LOW_STOCK_THRESHOLD)
        .order_by(models.Product.quantity)
        .all()
    )
    return {
        "total_products": active_products.count(),
        "total_customers": db.query(models.Customer)
        .filter(models.Customer.deleted_at.is_(None))
        .count(),
        "total_orders": db.query(models.Order).count(),
        "low_stock_products": len(low_stock),
        "low_stock_items": low_stock,
    }
