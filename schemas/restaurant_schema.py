from datetime import datetime
from pydantic import BaseModel


class RestaurantBase(BaseModel):
    name: str
    description: str | None = None
    is_active: bool = True
    rating: float | None = None


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    rating: float | None = None


class RestaurantResponse(RestaurantBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
