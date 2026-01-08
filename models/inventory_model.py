from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from models.base_model import TimestampMixin


class ProductInventory(Base, TimestampMixin):
    __tablename__ = "product_inventories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    available_quantity: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )

    reserved_quantity: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )

    # Relationship
    product = relationship("Product", back_populates="inventory")
