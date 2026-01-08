from pydantic import BaseModel


class CartItemBase(BaseModel):
    quantity: int


class CartItemCreate(CartItemBase):
    cart_id: str
    product_id: str


class CartItemResponse(CartItemBase):
    id: str
    cart_id: str
    product_id: str

    class Config:
        from_attributes = True
