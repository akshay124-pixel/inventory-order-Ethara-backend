from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderBase(BaseModel):
    customer_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderCreate(OrderBase):
    pass


class OrderResponse(OrderBase):
    id: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrderWithDetails(OrderResponse):
    customer_name: str
    customer_email: str
    product_name: str
    product_sku: str
    product_price: float
