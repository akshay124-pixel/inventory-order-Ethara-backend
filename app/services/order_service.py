from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models import Order, Product, Customer
from app.schemas import OrderCreate
from fastapi import HTTPException, status
from typing import List


class OrderService:
    
    @staticmethod
    def create_order(db: Session, order_data: OrderCreate) -> Order:
        """Create a new order with stock validation and automatic stock reduction"""
        
        # Validate customer exists
        customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {order_data.customer_id} not found"
            )
        
        # Validate product exists
        product = db.query(Product).filter(Product.id == order_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {order_data.product_id} not found"
            )
        
        # Validate stock availability
        if product.stock_quantity < order_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {product.stock_quantity}, Requested: {order_data.quantity}"
            )
        
        # Calculate total amount
        total_amount = product.price * order_data.quantity
        
        # Create order
        order = Order(
            customer_id=order_data.customer_id,
            product_id=order_data.product_id,
            quantity=order_data.quantity,
            total_amount=total_amount,
            status="completed"
        )
        
        # Reduce stock
        product.stock_quantity -= order_data.quantity
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all orders with customer and product details"""
        orders = db.query(
            Order.id,
            Order.customer_id,
            Order.product_id,
            Order.quantity,
            Order.total_amount,
            Order.status,
            Order.created_at,
            Order.updated_at,
            Customer.name.label("customer_name"),
            Customer.email.label("customer_email"),
            Product.name.label("product_name"),
            Product.sku.label("product_sku"),
            Product.price.label("product_price")
        ).join(Customer, Order.customer_id == Customer.id)\
         .join(Product, Order.product_id == Product.id)\
         .order_by(desc(Order.created_at))\
         .offset(skip).limit(limit).all()
        
        return [
            {
                "id": order.id,
                "customer_id": order.customer_id,
                "product_id": order.product_id,
                "quantity": order.quantity,
                "total_amount": order.total_amount,
                "status": order.status,
                "created_at": order.created_at,
                "updated_at": order.updated_at,
                "customer_name": order.customer_name,
                "customer_email": order.customer_email,
                "product_name": order.product_name,
                "product_sku": order.product_sku,
                "product_price": order.product_price
            }
            for order in orders
        ]
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> dict:
        """Get order by ID with details"""
        order = db.query(
            Order.id,
            Order.customer_id,
            Order.product_id,
            Order.quantity,
            Order.total_amount,
            Order.status,
            Order.created_at,
            Order.updated_at,
            Customer.name.label("customer_name"),
            Customer.email.label("customer_email"),
            Product.name.label("product_name"),
            Product.sku.label("product_sku"),
            Product.price.label("product_price")
        ).join(Customer, Order.customer_id == Customer.id)\
         .join(Product, Order.product_id == Product.id)\
         .filter(Order.id == order_id).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
        
        return {
            "id": order.id,
            "customer_id": order.customer_id,
            "product_id": order.product_id,
            "quantity": order.quantity,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "product_name": order.product_name,
            "product_sku": order.product_sku,
            "product_price": order.product_price
        }
    
    @staticmethod
    def get_dashboard_stats(db: Session) -> dict:
        """Get dashboard statistics"""
        total_products = db.query(Product).count()
        total_customers = db.query(Customer).count()
        total_orders = db.query(Order).count()
        low_stock_count = db.query(Product).filter(Product.stock_quantity <= 10).count()
        
        total_revenue = db.query(Order).with_entities(
            func.sum(Order.total_amount)
        ).scalar() or 0.0
        
        return {
            "total_products": total_products,
            "total_customers": total_customers,
            "total_orders": total_orders,
            "low_stock_count": low_stock_count,
            "total_revenue": float(total_revenue)
        }
