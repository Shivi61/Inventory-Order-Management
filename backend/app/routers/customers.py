from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


def _get_active(db: Session, customer_id: UUID) -> models.Customer:
    customer = db.get(models.Customer, customer_id)
    if customer is None or customer.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("", response_model=schemas.CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    if db.query(models.Customer).filter_by(email=payload.email).first():
        raise HTTPException(status_code=409, detail="A customer with this email already exists")

    customer = models.Customer(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("", response_model=list[schemas.CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    return (
        db.query(models.Customer)
        .filter(models.Customer.deleted_at.is_(None))
        .order_by(models.Customer.created_at.desc())
        .all()
    )


@router.get("/{customer_id}", response_model=schemas.CustomerOut)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    return _get_active(db, customer_id)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: UUID, db: Session = Depends(get_db)):
    customer = _get_active(db, customer_id)
    customer.deleted_at = datetime.utcnow()  # soft delete
    db.commit()
