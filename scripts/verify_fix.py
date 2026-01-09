import asyncio
import os
import sys

sys.path.append(os.getcwd())

from db.database import AsyncSessionLocal
from sqlalchemy import select, delete
from models.user_model import User
from repositories import user_repository
from utils.security import hash_password

async def verify_serialization():
    async with AsyncSessionLocal() as db:
        print("Testing User Serialization...")
        email = "serialization_test@example.com"
        
        # Cleanup
        await db.execute(delete(User).where(User.email == email))
        await db.commit()
        
        # Test Create
        user_in = User(
            name="Serial Tester",
            email=email,
            hashed_password=hash_password("password123"),
            role="user"
        )
        user = await user_repository.create(db, user_in)
        
        # Check property access (this triggered the error before)
        try:
            print(f"User created: {user.email}")
            print(f"Default Address: {user.default_address}")
            print("✅ Serialization check passed")
        except Exception as e:
            print(f"❌ Serialization check failed: {str(e)}")

        # Cleanup
        await db.execute(delete(User).where(User.email == email))
        await db.commit()

if __name__ == "__main__":
    asyncio.run(verify_serialization())
