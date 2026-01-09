from typing import Optional
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from models.base_model import TimestampMixin


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"  # pending | confirmed | preparing | delivered | cancelled
    )

    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    payment_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="unpaid"  # unpaid | paid | failed | refunded
    )

    # Uber Direct Fields
    uber_quote_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uber_delivery_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uber_tracking_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    delivery_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, server_default="0.0")

   

    # Relationships
    user = relationship("User", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    payment = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan"
    )
