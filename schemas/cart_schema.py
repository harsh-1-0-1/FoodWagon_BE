from typing import List, Optional
from pydantic import BaseModel, Field, conint
from datetime import datetime


class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemResponse(CartItemBase):
    id: int
    price_at_time: float
    product_name: str
    product_image: Optional[str] = None
    subtotal: float

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse] = []
    total_price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
