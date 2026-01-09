import httpx
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from core.config import settings
from utils.logger_utils import get_logger

logger = get_logger(__name__)

class UberDirectClient:
    def __init__(self):
        self.client_id = settings.UBER_DIRECT_CLIENT_ID
        self.client_secret = settings.UBER_DIRECT_CLIENT_SECRET
        self.customer_id = settings.UBER_DIRECT_CUSTOMER_ID

        self.auth_url = settings.UBER_DIRECT_AUTH_URL
        self.api_base = settings.UBER_DIRECT_API_BASE

        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    # ------------------------
    # AUTH
    # ------------------------
    async def _get_access_token(self) -> str:
        if self._token and self._token_expiry and datetime.now(timezone.utc) < self._token_expiry:
            return self._token

        logger.info("Fetching new Uber Direct access token")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.auth_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                    "scope": "eats.deliveries",
                },
            )
            if response.status_code != 200:
                logger.error(f"Failed to fetch Uber token: {response.text}")
                response.raise_for_status()
            
            data = response.json()

        self._token = data["access_token"]
        # Expire slightly early to be safe
        expires_in = data.get("expires_in", 3600)
        self._token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)
        return self._token

    async def _auth_headers(self) -> Dict[str, str]:
        token = await self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    # ------------------------
    # CREATE QUOTE
    # ------------------------
    async def create_quote(
        self,
        pickup_address: Any, # Can be string or dict depending on Uber region/API version
        dropoff_address: Any,
    ) -> Dict[str, Any]:
        """
        Evaluate deliverability and cost between two addresses.
        """
        url = f"{self.api_base}/v1/customers/{self.customer_id}/delivery_quotes"

        payload = {
            "pickup_address": pickup_address,
            "dropoff_address": dropoff_address,
        }

        logger.info(f"Requesting Uber Direct quote")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=await self._auth_headers(),
                json=payload,
            )
            if response.status_code != 200:
                logger.error(f"Uber Quote Error: {response.text}")
                response.raise_for_status()
            return response.json()

    # ------------------------
    # CREATE DELIVERY
    # ------------------------
    async def create_delivery(
        self,
        quote_id: str,
        pickup: Dict[str, Any],
        dropoff: Dict[str, Any],
        manifest_items: list[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Dispatch a delivery using a quote ID.
        """
        url = f"{self.api_base}/v1/customers/{self.customer_id}/deliveries"

        payload = {
            "quote_id": quote_id,
            **pickup,
            **dropoff,
            "manifest_items": manifest_items,
        }

        logger.info(f"Creating Uber Direct delivery | quote_id={quote_id}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=await self._auth_headers(),
                json=payload,
            )
            if response.status_code != 200:
                logger.error(f"Uber Delivery Error: {response.text}")
                response.raise_for_status()
            return response.json()

    async def get_delivery_status(self, delivery_id: str) -> Dict[str, Any]:
        """
        Fetch current status of a delivery.
        """
        url = f"{self.api_base}/v1/customers/{self.customer_id}/deliveries/{delivery_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=await self._auth_headers(),
            )
            response.raise_for_status()
            return response.json()

# Singleton instance
uber_client = UberDirectClient()
