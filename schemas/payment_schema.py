from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class PaymentCreate(BaseModel):
    order_id: int


class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    payment_method: str
    transaction_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentSessionResponse(BaseModel):
    order_id: str
    amount: float
    currency: str
    key_id: str
