from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import json

from utils.delivery_utils import uber_client
from models.order_model import Order
from models.restaurant_model import Restaurant
from models.address_model import Address
from repositories import order_repository
from utils.logger_utils import get_logger

logger = get_logger(__name__)

async def get_uber_quote_service(db: AsyncSession, restaurant: Restaurant, user_address: Address):
    """
    Get a delivery quote from Uber Direct.
    """
    try:
        # Format addresses for Uber
        # Uber can accept a string or highly structured JSON
        pickup_address = {
            "street_address": [restaurant.street or ""],
            "city": restaurant.city or "",
            "state": restaurant.state or "",
            "zip_code": restaurant.postal_code or "",
            "country": restaurant.country or "IN",
        }
        
        dropoff_address = {
            "street_address": [user_address.street],
            "city": user_address.city,
            "state": user_address.state,
            "zip_code": user_address.postal_code,
            "country": user_address.country,
        }

        quote = await uber_client.create_quote(
            pickup_address=json.dumps(pickup_address),
            dropoff_address=json.dumps(dropoff_address)
        )
        
        # Uber returns fee in cents/paise (depending on currency)
        # We store it as float (e.g. 5.58)
        fee = quote.get("fee", 0) / 100.0
        
        return {
            "quote_id": quote.get("id"),
            "fee": fee,
            "estimated_duration": quote.get("duration")
        }
    except Exception as e:
        logger.error(f"Uber Quote Service Error: {str(e)}")
        # For MVP, we might want to return a fallback or re-raise
        # Here we re-raise as it's critical for checkout if we charge for it
        raise HTTPException(status_code=502, detail="Unable to fetch delivery quote")

async def dispatch_uber_delivery_service(db: AsyncSession, order: Order):
    """
    Trigger Uber Direct delivery for a paid order.
    """
    if not order.uber_quote_id:
        logger.warning(f"Order {order.id} has no uber_quote_id, skipping dispatch")
        return

    try:
        # We need restaurant and address info again for the dispatch call
        # In a real app, we might store the formatted addresses or re-fetch
        # Fetching relation if not loaded
        restaurant = order.restaurant
        
        # Getting user's default address (simplification for MVP)
        # In a better version, the order would link to a specific address_id
        from repositories.user_repository import get_by_id
        user = await get_by_id(db, order.user_id)
        # Find the default address
        user_address = next((a for a in user.addresses if a.is_default), user.addresses[0] if user.addresses else None)
        
        if not user_address:
            raise ValueError("No delivery address found for user")

        from utils.phone_utils import format_phone_uber

        pickup = {
            "pickup_name": restaurant.name,
            "pickup_phone_number": format_phone_uber(restaurant.phone_number),
            "pickup_address": json.dumps({
                "street_address": [restaurant.street or ""],
                "city": restaurant.city or "",
                "state": restaurant.state or "",
                "zip_code": restaurant.postal_code or "",
                "country": restaurant.country or "IN",
            })
        }
        
        dropoff = {
            "dropoff_name": user.name,
            "dropoff_phone_number": format_phone_uber(user.phone_number),
            "dropoff_address": json.dumps({
                "street_address": [user_address.street],
                "city": user_address.city,
                "state": user_address.state,
                "zip_code": user_address.postal_code,
                "country": user_address.country,
            })
        }

        # Manifest items from order
        manifest_items = []
        for item in order.items:
            manifest_items.append({
                "name": item.product.name,
                "quantity": item.quantity
            })

        delivery = await uber_client.create_delivery(
            quote_id=order.uber_quote_id,
            pickup=pickup,
            dropoff=dropoff,
            manifest_items=manifest_items
        )
        
        # Update order with delivery info
        order.uber_delivery_id = delivery.get("id")
        order.uber_tracking_url = delivery.get("tracking_url")
        order.status = "preparing" # Move status forward
        await db.commit()
        
        logger.info(f"Uber Delivery dispatched for order {order.id} | delivery_id={order.uber_delivery_id}")
        return delivery

    except Exception as e:
        logger.error(f"Uber Dispatch Service Error: {str(e)}")
        # Don't fail the verification process, just log it. 
        # Manual retry might be needed.
