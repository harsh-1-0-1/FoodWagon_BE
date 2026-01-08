import asyncio
import sys
import os
import aiohttp

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_profile_flow():
    async with aiohttp.ClientSession() as session:
        # 1. Login
        print("🔑 Logging in...")
        async with session.post(f"{BASE_URL}/auth/login", json={"email": "payment_test@example.com", "password": "password123"}) as resp:
            data = await resp.json()
            if resp.status != 200:
                print(f"❌ Login failed: {data}")
                return
            token = data["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Logged in")

        # 2. Get Profile
        print("\n👤 Fetching Profile (/users/me)...")
        async with session.get(f"{BASE_URL}/users/me", headers=headers) as resp:
            data = await resp.json()
            if resp.status == 200:
                user = data["data"]
                print(f"✅ Profile Fetched!")
                print(f"   - Name: {user['name']}")
                print(f"   - Email: {user['email']}")
                print(f"   - Role: {user['role']}")
            else:
                print(f"❌ Fetch failed: {data}")

if __name__ == "__main__":
    asyncio.run(test_profile_flow())
