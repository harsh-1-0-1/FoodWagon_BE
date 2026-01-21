from pydantic import BaseModel
from typing import List, Optional
from schemas.product_schema import ProductResponse


class FavoriteBase(BaseModel):
    product_id: int


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(FavoriteBase):
    id: int
    user_id: int
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True
