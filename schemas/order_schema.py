from typing import List, Optional
from pydantic import BaseModel, condecimal
from datetime import datetime


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price_at_time: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    product_name: str

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    restaurant_id: int


class OrderCreate(OrderBase):
    # Items are usually not passed directly for cart-checkout flow,
    # but strictly for manual order creation if needed.
    # For cart checkout, we just need address_id or similar.
    # But sticking to simple flow first.
    pass


class OrderResponse(OrderBase):
    id: int
    user_id: int
    status: str
    total_amount: float
    payment_status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderUpdateStatus(BaseModel):
    status: str
