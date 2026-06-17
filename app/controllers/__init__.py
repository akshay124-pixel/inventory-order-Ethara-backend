from .product_controller import router as product_router
from .customer_controller import router as customer_router
from .order_controller import router as order_router

__all__ = ["product_router", "customer_router", "order_router"]
