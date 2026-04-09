"""
CloudMart - Pydantic Models for Request/Response Validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Product(BaseModel):
    """Product model for the CloudMart catalog."""
    id: str
    name: str
    category: str
    price: float
    description: str
    image_url: Optional[str] = ""
    in_stock: bool = True


class CartItemRequest(BaseModel):
    """Request model for adding an item to the cart."""
    product_id: str
    quantity: int = Field(default=1, ge=1, le=99)


class CartItem(BaseModel):
    """Cart item stored in Cosmos DB."""
    id: str
    user_id: str
    product_id: str
    product_name: str
    price: float
    quantity: int
    subtotal: float


class OrderItem(BaseModel):
    """An item within an order."""
    product_id: str
    product_name: str
    price: float
    quantity: int
    subtotal: float


class Order(BaseModel):
    """Order model stored in Cosmos DB."""
    id: str
    user_id: str
    items: List[OrderItem]
    total: float
    status: str = "confirmed"
    created_at: str


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    database: str
    cosmos_endpoint: str
    timestamp: str
