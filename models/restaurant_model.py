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

    # Address fields for delivery
    street: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str | None] = mapped_column(String(100))
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]

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

