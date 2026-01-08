from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from db.database import Base
from models.base_model import TimestampMixin


class InventoryHistory(Base, TimestampMixin):
    __tablename__ = "inventory_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # SET, INCREASE, DECREASE
    quantity: Mapped[int] = mapped_column(nullable=False)
    previous_stock: Mapped[int] = mapped_column(nullable=False)
    new_stock: Mapped[int] = mapped_column(nullable=False)
    performed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
