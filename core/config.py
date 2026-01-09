from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str

    # Razorpay
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str

    # Uber Direct
    UBER_DIRECT_CLIENT_ID: str
    UBER_DIRECT_CLIENT_SECRET: str
    UBER_DIRECT_CUSTOMER_ID: str
    UBER_DIRECT_AUTH_URL: str = "https://auth.uber.com/oauth/v2/token"
    UBER_DIRECT_API_BASE: str = "https://api.uber.com"

    # Firebase (Optional)
    FIREBASE_CREDENTIALS: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
