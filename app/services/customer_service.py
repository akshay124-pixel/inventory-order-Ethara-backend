from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Customer
from app.schemas import CustomerCreate, CustomerUpdate
from fastapi import HTTPException, status
from typing import List, Optional


class CustomerService:
    
    @staticmethod
    def create_customer(db: Session, customer_data: CustomerCreate) -> Customer:
        """Create a new customer"""
        try:
            customer = Customer(**customer_data.model_dump())
            db.add(customer)
            db.commit()
            db.refresh(customer)
            return customer
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with email '{customer_data.email}' already exists"
            )
    
    @staticmethod
    def get_all_customers(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Customer]:
        """Get all customers with optional search"""
        query = db.query(Customer)
        
        if search:
            query = query.filter(
                (Customer.name.ilike(f"%{search}%")) | 
                (Customer.email.ilike(f"%{search}%"))
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Customer:
        """Get customer by ID"""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        return customer
    
    @staticmethod
    def update_customer(db: Session, customer_id: int, customer_data: CustomerUpdate) -> Customer:
        """Update an existing customer"""
        customer = CustomerService.get_customer_by_id(db, customer_id)
        
        update_data = customer_data.model_dump(exclude_unset=True)
        
        try:
            for field, value in update_data.items():
                setattr(customer, field, value)
            
            db.commit()
            db.refresh(customer)
            return customer
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with email '{customer_data.email}' already exists"
            )
    
    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> dict:
        """Delete a customer"""
        customer = CustomerService.get_customer_by_id(db, customer_id)
        try:
            db.delete(customer)
            db.commit()
            return {"message": "Customer deleted successfully"}
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete customer because they have one or more active orders."
            )
