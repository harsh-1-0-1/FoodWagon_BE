from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# =========================
# Base Schema (Shared)
# =========================
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)

    category_id: int
    restaurant_id: int

    description: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = True


# =========================
# Create Schema (POST)
# =========================
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)
    category_name: str = Field(..., min_length=1)
    restaurant_id: int
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = True


# =========================
# Update Schema (PATCH)
# =========================
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[float] = Field(None, gt=0)

    category_id: Optional[int] = None
    restaurant_id: Optional[int] = None

    description: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None


# =========================
# Response Schema (GET)
# =========================
class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
