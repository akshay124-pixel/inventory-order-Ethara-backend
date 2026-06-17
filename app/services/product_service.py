from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate
from fastapi import HTTPException, status
from typing import List, Optional


class ProductService:
    
    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> Product:
        """Create a new product"""
        try:
            product = Product(**product_data.model_dump())
            db.add(product)
            db.commit()
            db.refresh(product)
            return product
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_data.sku}' already exists"
            )
    
    @staticmethod
    def get_all_products(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Product]:
        """Get all products with optional search"""
        query = db.query(Product)
        
        if search:
            query = query.filter(
                (Product.name.ilike(f"%{search}%")) | 
                (Product.sku.ilike(f"%{search}%"))
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Product:
        """Get product by ID"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        return product
    
    @staticmethod
    def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Product:
        """Update an existing product"""
        product = ProductService.get_product_by_id(db, product_id)
        
        update_data = product_data.model_dump(exclude_unset=True)
        
        try:
            for field, value in update_data.items():
                setattr(product, field, value)
            
            db.commit()
            db.refresh(product)
            return product
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_data.sku}' already exists"
            )
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> dict:
        """Delete a product"""
        product = ProductService.get_product_by_id(db, product_id)
        try:
            db.delete(product)
            db.commit()
            return {"message": "Product deleted successfully"}
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete product because it is referenced in one or more active orders."
            )
    
    @staticmethod
    def get_low_stock_products(db: Session, threshold: int = 10) -> List[Product]:
        """Get products with low stock"""
        return db.query(Product).filter(Product.stock_quantity <= threshold).all()
