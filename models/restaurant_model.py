from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from models.base_model import TimestampMixin


class Restaurant(Base, TimestampMixin):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[str | None] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default="true",
        nullable=False,
    )

    rating: Mapped[float | None]

    # Relationships
    orders = relationship(
        "Order",
        back_populates="restaurant",
        cascade="all, delete"
    )

    categories = relationship(
        "Category",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

    products = relationship(
        "Product",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

