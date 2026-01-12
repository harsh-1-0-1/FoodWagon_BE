from typing import List
from pydantic import BaseModel


class OrderItemBase(BaseModel):
    quantity: int
    price_at_time: float


class OrderItemCreate(OrderItemBase):
    order_id: int
    product_id: int


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    product_id: int
    image_urls: List[str]

    class Config:
        from_attributes = True
