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
from core.config import settings
import utils.firebase  # IMPORTANT
import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Food Ordering Backend",
    lifespan=lifespan
)

# Secure CORS Configuration
# Standard local origins
origins = [
    "http://localhost",
    "http://localhost:5173",  # Vite
    "http://localhost:3000",  # React/Next
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Add custom origins from settings (e.g. production domain if set in .env)
if settings.CORS_ORIGINS and "*" not in settings.CORS_ORIGINS:
    origins.extend(settings.CORS_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Always allow ngrok subdomains via regex for convenience and security
    allow_origin_regex=r"https://.*\.ngrok-free\.app|https://.*\.ngrok\.io",
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
