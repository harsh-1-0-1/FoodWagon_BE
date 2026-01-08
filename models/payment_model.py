from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from models.base_model import TimestampMixin


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    payment_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # credit_card | debit_card | upi | cash | wallet

    transaction_id: Mapped[str | None] = mapped_column(String(255), index=True)

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )  # pending | completed | failed | refunded

    # Relationships
    order = relationship("Order", back_populates="payment")
