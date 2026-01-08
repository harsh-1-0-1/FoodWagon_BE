from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from models.base_model import TimestampMixin


class Address(Base, TimestampMixin):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    street: Mapped[str] = mapped_column(String(255), nullable=False)

    city: Mapped[str] = mapped_column(String(100), nullable=False)

    state: Mapped[str] = mapped_column(String(100), nullable=False)

    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)

    country: Mapped[str] = mapped_column(String(100), nullable=False)

    is_default: Mapped[bool] = mapped_column(server_default="false", nullable=False)

    # Relationships
    user = relationship("User", back_populates="addresses")
