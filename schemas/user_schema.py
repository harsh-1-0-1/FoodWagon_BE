from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic import ConfigDict
from schemas.address_schema import AddressResponse


# -----------------------------
# Create User (Register)
# -----------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None


# -----------------------------
# Update User Profile
# -----------------------------
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None


# -----------------------------
# Read User (Response)
# -----------------------------
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    phone_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    default_address: Optional[AddressResponse] = None

    model_config = ConfigDict(from_attributes=True)
