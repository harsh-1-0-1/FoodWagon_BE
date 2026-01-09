from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware

from controllers.auth_controllers import router as auth_router
from controllers.user_controllers import router as user_router
from controllers.product_controllers import router as product_router
from controllers.restaurant_controllers import router as restaurant_router
from controllers.category_controller import router as category_router
from controllers.inventory_controller import router as inventory_router
from controllers.cart_controller import router as cart_router
from controllers.order_controller import router as order_router
from controllers.payment_controller import router as payment_router
from controllers.address_controller import router as address_router
from controllers.delivery_controller import router as delivery_router


from schemas.response_schema import APIResponse
import utils.firebase  # IMPORTANT
import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Food Ordering Backend",
    lifespan=lifespan
)

# DEV / NGROK SAFE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user_router)
api_router.include_router(auth_router)
api_router.include_router(product_router)   
api_router.include_router(restaurant_router)
api_router.include_router(category_router)
api_router.include_router(inventory_router)
api_router.include_router(cart_router)
api_router.include_router(order_router)
api_router.include_router(payment_router)
api_router.include_router(address_router)
api_router.include_router(delivery_router)


app.include_router(api_router)


# ==============================
# Global Exception Handler
# ==============================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Global handler for HTTPException errors.
    Converts them to APIResponse format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            message="Request failed",
            status_code=exc.status_code,
            data=None,
            error=exc.detail,
        ).model_dump(),
    )
