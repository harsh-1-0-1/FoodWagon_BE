from sqlalchemy import String, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from models.base_model import TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    description: Mapped[str | None] = mapped_column(String)

    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    image_url: Mapped[str | None] = mapped_column(String)

    is_available: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relationships
    category = relationship(
        "Category",
        back_populates="products"
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="products"
    )

    inventory = relationship(
        "ProductInventory",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan"
    )

    order_items = relationship(
        "OrderItem",
        back_populates="product"
    )
