from pydantic import BaseModel


class OrderItemBase(BaseModel):
    quantity: int
    price_at_time: float


class OrderItemCreate(OrderItemBase):
    order_id: str
    product_id: str


class OrderItemResponse(OrderItemBase):
    id: str
    order_id: str
    product_id: str

    class Config:
        from_attributes = True
