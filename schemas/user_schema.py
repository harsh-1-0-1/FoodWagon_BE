from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic import ConfigDict


# -----------------------------
# Create User (Register)
# -----------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


# -----------------------------
# Update User Profile
# -----------------------------
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


# -----------------------------
# Read User (Response)
# -----------------------------
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
