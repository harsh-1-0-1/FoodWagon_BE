from typing import Optional
from pydantic import BaseModel, Field

class AddressBase(BaseModel):
    street: str = Field(min_length=5, max_length=255)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    postal_code: str = Field(min_length=4, max_length=20)
    country: str = Field(min_length=2, max_length=100)
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    street: Optional[str] = Field(None, min_length=5, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=4, max_length=20)
    country: Optional[str] = Field(None, min_length=2, max_length=100)
    is_default: Optional[bool] = None

class AddressResponse(AddressBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True
