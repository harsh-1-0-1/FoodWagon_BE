from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from models.base_model import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True  # Nullable for Google-only users
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="user"  # user | admin | restaurant_owner | delivery
    )

    # Google/Firebase authentication fields
    firebase_uid: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True
    )

    auth_provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default="email"  # email | google
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # ---------------- PROPERTIES ---------------- #

    @property
    def default_address(self):
        """Returns the default address if it exists, else None."""
        for address in self.addresses:
            if address.is_default:
                return address
        return None

    # ---------------- RELATIONSHIPS ---------------- #

    # User → Orders (One-to-Many)
    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete"
    )

    # User → Addresses (One-to-Many)
    addresses = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # User → Cart (One-to-One)
    cart = relationship(
        "Cart",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # User → Audit Logs (One-to-Many)
    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete"
    )
