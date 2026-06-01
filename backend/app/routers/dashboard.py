import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Products at or below this quantity are flagged as low stock.
LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "10"))


@router.get("/summary", response_model=schemas.DashboardSummary)
def summary(db: Session = Depends(get_db)):
    low_stock = (
        db.query(models.Product)
        .filter(models.Product.quantity <= LOW_STOCK_THRESHOLD)
        .order_by(models.Product.quantity)
        .all()
    )
    return {
        "total_products": db.query(models.Product).count(),
        "total_customers": db.query(models.Customer).count(),
        "total_orders": db.query(models.Order).count(),
        "low_stock_products": low_stock,
    }
