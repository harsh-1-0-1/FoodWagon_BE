from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.payment_model import Payment


async def create_payment(
    db: AsyncSession,
    order_id: int,
    amount: float,
    transaction_id: str,
    payment_method: str = "rzp", # Initial placeholder
    status: str = "pending"
) -> Payment:
    payment = Payment(
        order_id=order_id,
        amount=amount,
        transaction_id=transaction_id,
        payment_method=payment_method,
        status=status
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def get_payment_by_order_id(db: AsyncSession, order_id: int) -> Payment | None:
    result = await db.execute(select(Payment).where(Payment.order_id == order_id))
    return result.scalars().first()


async def get_payment_by_transaction_id(db: AsyncSession, transaction_id: str) -> Payment | None:
    result = await db.execute(select(Payment).where(Payment.transaction_id == transaction_id))
    return result.scalars().first()


async def update_payment_status(
    db: AsyncSession, 
    payment: Payment, 
    status: str,
    payment_method: str | None = None
) -> Payment:
    payment.status = status
    if payment_method:
        payment.payment_method = payment_method
    
    await db.commit()
    await db.refresh(payment)
    return payment
