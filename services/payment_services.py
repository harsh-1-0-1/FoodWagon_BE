"""
Payment Services - Business Logic

Handles Razorpay integration, payment verification, and order status updates.
"""

import os
import razorpay
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models.user_model import User
from repositories import payment_repository, order_repository
from schemas.payment_schema import PaymentCreate, PaymentVerify, PaymentSessionResponse, PaymentResponse
from services.delivery_services import dispatch_uber_delivery_service
from core.config import settings
from utils.logger_utils import get_logger

logger = get_logger(__name__)

# Initialize Razorpay Client
RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET

try:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
except Exception as e:
    logger.error("Failed to initialize Razorpay client: %s", str(e))
    razorpay_client = None


async def create_payment_session_service(
    db: AsyncSession,
    user: User,
    payment_data: PaymentCreate
) -> PaymentSessionResponse:
    logger.info("Initiating payment session | user_id=%s order_id=%s", user.id, payment_data.order_id)

    order = await order_repository.get_order_by_id(db, payment_data.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")

    # Create Razorpay Order
    # Amount is in paise (Multiply by 100)
    amount_in_paise = int(order.total_amount * 100)
    
    razorpay_order_data = {
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": f"order_{order.id}",
        "notes": {
            "user_id": str(user.id),
            "order_id": str(order.id)
        }
    }
    
    try:
        # Sync call (Razorpay lib is sync), might block slightly but acceptable for this scale
        # Ideally run in threadpool for high concurrency
        rzp_order = razorpay_client.order.create(data=razorpay_order_data)
    except Exception as e:
        logger.error("Razorpay order creation failed: %s", str(e))
        raise HTTPException(status_code=502, detail="Payment gateway error")
    
    rzp_order_id = rzp_order["id"]
    
    # Check if a payment record already exists?
    # If users retry, we might update existing or create new.
    # Simple approach: Create new payment record or update existing if uniqueness on order_id
    # Payment model has unique order_id. So we fetch and update or create.
    
    existing_payment = await payment_repository.get_payment_by_order_id(db, order.id)
    if existing_payment:
        # Update transaction ID (rzp_order_id)
        existing_payment.transaction_id = rzp_order_id
        await db.commit()
    else:
        await payment_repository.create_payment(
            db, 
            order_id=order.id, 
            amount=order.total_amount,
            transaction_id=rzp_order_id,
            status="pending"
        )
        
    return PaymentSessionResponse(
        order_id=rzp_order_id,
        amount=order.total_amount,
        currency="INR",
        key_id=RAZORPAY_KEY_ID
    )


async def verify_payment_service(
    db: AsyncSession,
    user: User,
    verification_data: PaymentVerify
) -> PaymentResponse:
    logger.info("Verifying payment | rzp_order_id=%s", verification_data.razorpay_order_id)
    
    # 1. Verify Signature
    try:
        params_dict = {
            'razorpay_order_id': verification_data.razorpay_order_id,
            'razorpay_payment_id': verification_data.razorpay_payment_id,
            'razorpay_signature': verification_data.razorpay_signature
        }
        razorpay_client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        logger.warning("Signature verification failed | rzp_order_id=%s", verification_data.razorpay_order_id)
        raise HTTPException(status_code=400, detail="Payment signature verification failed")
    except Exception as e:
        logger.error("Payment verification error: %s", str(e))
        raise HTTPException(status_code=400, detail="Invalid payment details")

    # 2. Update Payment & Order Status
    payment = await payment_repository.get_payment_by_transaction_id(db, verification_data.razorpay_order_id)
    if not payment:
         raise HTTPException(status_code=404, detail="Payment record not found")
         
    # Update Payment
    updated_payment = await payment_repository.update_payment_status(
        db, payment, status="completed", payment_method="razorpay" # Explicitly setting method
    )
    
    # Update Order
    order = await order_repository.get_order_by_id(db, payment.order_id)
    if order:
        order.payment_status = "paid"
        order.status = "confirmed" # Auto-confirm on payment
        await db.commit()
        await db.refresh(order) # Refresh to ensure attributes are available for dispatch
        
        # 3. Dispatch to Uber Direct
        logger.info(f"Triggering Uber Direct dispatch for order {order.id}")
        try:
            await dispatch_uber_delivery_service(db, order)
            logger.info(f"Uber Direct dispatch completed for order {order.id}")
        except Exception as e:
            logger.error(f"Post-payment delivery dispatch failed for order {order.id}: {str(e)}")
            # We don't fail the verification since payment is already confirmed
    
    logger.info("Payment verified and order updated | order_id=%s", payment.order_id)
    
    return PaymentResponse.model_validate(updated_payment)
