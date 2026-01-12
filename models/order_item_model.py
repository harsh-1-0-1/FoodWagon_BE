from sqlalchemy import Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    quantity: Mapped[int] = mapped_column(
        nullable=False
    )

    price_at_time: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    # Relationships
    order = relationship("Order", back_populates="items")

    product = relationship(
        "Product",
        back_populates="order_items"
    )

    @property
    def product_name(self) -> str:
        return self.product.name if self.product else "Unknown Product"

    @property
    def image_urls(self) -> list[str]:
        if self.product and self.product.image_url:
            return [self.product.image_url]
        return []
