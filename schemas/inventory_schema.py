from pydantic import BaseModel, Field
from datetime import datetime


class StockUpdate(BaseModel):
    amount: int = Field(..., gt=0, description="Amount to increase or decrease")


class StockSet(BaseModel):
    stock: int = Field(..., ge=0, description="Absolute stock value")


class InventoryHistoryResponse(BaseModel):
    id: int
    category_id: int
    action: str
    quantity: int
    previous_stock: int
    new_stock: int
    performed_by: int
    created_at: datetime

    class Config:
        from_attributes = True
