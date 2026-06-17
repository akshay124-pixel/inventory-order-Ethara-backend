from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.services import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    return ProductService.create_product(db, product)


@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all products with optional search"""
    return ProductService.get_all_products(db, skip, limit, search)


@router.get("/low-stock", response_model=List[ProductResponse])
def get_low_stock_products(
    threshold: int = Query(10, ge=0),
    db: Session = Depends(get_db)
):
    """Get products with low stock"""
    return ProductService.get_low_stock_products(db, threshold)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    return ProductService.get_product_by_id(db, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing product"""
    return ProductService.update_product(db, product_id, product)


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    return ProductService.delete_product(db, product_id)
