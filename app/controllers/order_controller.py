from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import OrderCreate, OrderWithDetails
from app.services import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderWithDetails, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    created_order = OrderService.create_order(db, order)
    return OrderService.get_order_by_id(db, created_order.id)


@router.get("/", response_model=List[OrderWithDetails])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all orders with details"""
    return OrderService.get_all_orders(db, skip, limit)


@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    return OrderService.get_dashboard_stats(db)


@router.get("/{order_id}", response_model=OrderWithDetails)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID with details"""
    return OrderService.get_order_by_id(db, order_id)
