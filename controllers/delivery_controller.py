from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.user_model import User
from schemas.response_schema import APIResponse, success_response
from utils.role_dependencies import require_authenticated
from utils.delivery_utils import uber_client
from repositories import order_repository

router = APIRouter(prefix="/delivery", tags=["Delivery"])

@router.get("/{order_id}/status", response_model=APIResponse[dict])
async def get_order_delivery_status(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Get the real-time Uber Direct status for an order.
    """
    order = await order_repository.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    if not order.uber_delivery_id:
        return success_response(
            message="No Uber delivery active for this order",
            data={
                "status": "local_processing", 
                "local_status": order.status,
                "tracking_url": None
            }
        )

    try:
        status_data = await uber_client.get_delivery_status(order.uber_delivery_id)
        return success_response(
            message="Delivery status fetched successfully",
            data={
                "uber_api": status_data,
                "tracking_url": order.uber_tracking_url
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Uber API Error: {str(e)}")
