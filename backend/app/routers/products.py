from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import inventory, models, schemas
from ..database import get_db

router = APIRouter(prefix="/products", tags=["products"])


def _get_active(db: Session, product_id: UUID) -> models.Product:
    product = db.get(models.Product, product_id)
    if product is None or product.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    if db.query(models.Product).filter_by(sku=payload.sku).first():
        raise HTTPException(status_code=409, detail="A product with this SKU already exists")

    product = models.Product(**payload.model_dump())
    db.add(product)
    db.flush()  # assign the id before recording the opening stock
    inventory.record_movement(db, product.id, product.quantity, inventory.PRODUCT_ADDED)
    db.commit()
    db.refresh(product)
    return product


@router.get("", response_model=schemas.ProductPage)
def list_products(
    db: Session = Depends(get_db),
    search: str | None = Query(None, description="Match against name or SKU"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    query = db.query(models.Product).filter(models.Product.deleted_at.is_(None))
    if search:
        like = f"%{search}%"
        query = query.filter(
            models.Product.name.ilike(like) | models.Product.sku.ilike(like)
        )

    total = query.count()
    items = (
        query.order_by(models.Product.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    return _get_active(db, product_id)


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: UUID, payload: schemas.ProductUpdate, db: Session = Depends(get_db)
):
    product = _get_active(db, product_id)
    data = payload.model_dump(exclude_unset=True)

    new_sku = data.get("sku")
    if new_sku and new_sku != product.sku:
        if db.query(models.Product).filter_by(sku=new_sku).first():
            raise HTTPException(status_code=409, detail="A product with this SKU already exists")

    # If the quantity is being adjusted, log the movement.
    if "quantity" in data and data["quantity"] != product.quantity:
        inventory.record_movement(
            db, product.id, data["quantity"] - product.quantity, inventory.STOCK_UPDATED
        )

    for field, value in data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    product = _get_active(db, product_id)
    product.deleted_at = datetime.utcnow()  # soft delete
    db.commit()
