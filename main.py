from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware

from controllers.auth_controllers import router as auth_router
from controllers.user_controllers import router as user_router
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

app.include_router(api_router)
