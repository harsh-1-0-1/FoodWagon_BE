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
from controllers.favorite_controller import router as favorite_router


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
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# Add custom origins from settings (e.g. production domain if set in .env)
if settings.CORS_ORIGINS and "*" not in settings.CORS_ORIGINS:
    origins.extend(settings.CORS_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Browsers require exact origin and allow_credentials=True.
    # The regex approach satisfies this while allowing dynamic subdomains (ngrok).
    allow_origin_regex=r".*" if settings.DEBUG else r"https?://.*\.ngrok-free\..*|https?://.*\.ngrok\.io|https?://localhost(:[0-9]+)?|https?://127\.0\.0\.1(:[0-9]+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional: Add a logger to see why requests might be failing
@app.middleware("http")
async def debug_logging_middleware(request: Request, call_next):
    if settings.DEBUG:
        if request.method == "OPTIONS":
             print(f"DEBUG: OPTIONS request | Origin: {request.headers.get('origin')} | Host: {request.headers.get('host')} | Path: {request.url.path}")
        
        try:
            response = await call_next(request)
            if response.status_code == 400:
                print(f"DEBUG: 400 Bad Request | Method: {request.method} | Path: {request.url.path} | Origin: {request.headers.get('origin')}")
            return response
        except Exception as e:
            print(f"DEBUG: Exception during {request.method} {request.url.path}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e
    return await call_next(request)

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
api_router.include_router(favorite_router)


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
