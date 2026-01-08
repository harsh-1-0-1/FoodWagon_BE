"""
Payment Controller

Handles payment sessions and verification.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.user_model import User
from schemas.payment_schema import PaymentCreate, PaymentSessionResponse, PaymentVerify, PaymentResponse
from schemas.response_schema import APIResponse, success_response
from utils.role_dependencies import require_authenticated
from services.payment_services import create_payment_session_service, verify_payment_service


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post(
    "/create-session",
    response_model=APIResponse[PaymentSessionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_payment_session(
    payment_data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Initiate a payment session.
    - Creates Razorpay Order
    - Creates local Payment record
    - Returns details for frontend SDK
    """
    session = await create_payment_session_service(db, current_user, payment_data)
    return success_response(
        message="Payment session created",
        data=session,
    )


@router.post(
    "/verify",
    response_model=APIResponse[PaymentResponse],
)
async def verify_payment(
    verification_data: PaymentVerify,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Verify Razorpay payment signature.
    - Validates signature
    - Updates Payment status
    - Updates Order status
    """
    result = await verify_payment_service(db, current_user, verification_data)
    return success_response(
        message="Payment verified successfully",
        data=result,
    )
