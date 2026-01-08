import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.database import DATABASE_URL
from models.user_model import User
from models.restaurant_model import Restaurant
from models.category_model import Category
from models.product_model import Product
from utils.security import hash_password

# Setup DB
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def seed_data():
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding data...")

        # 1. Create Test User
        # Check if exists
        # Simplified for brevity, just try create
        test_user = User(
            name="Razorpay Tester",
            email="payment_test@example.com",
            hashed_password=hash_password("password123"),
            role="user",
            is_verified=True
        )
        db.add(test_user)
        try:
            await db.commit()
            await db.refresh(test_user)
            print(f"✅ User created: {test_user.email} / password123 (ID: {test_user.id})")
        except Exception:
            await db.rollback()
            print("⚠️ User already exists or failed")
            # Fetch existing to continue
            from sqlalchemy import select
            res = await db.execute(select(User).where(User.email == "payment_test@example.com"))
            test_user = res.scalars().first()

        # 2. Create Restaurant
        restaurant = Restaurant(
            name="Razorpay Test Foods",
            description="Best test food in town",
            is_active=True
        )
        # Owner ID omitted as not in model definition currently
        # Address omitted as not in model definition currently
        
        db.add(restaurant)
        try:
            await db.commit()
            await db.refresh(restaurant)
            print(f"✅ Restaurant created: {restaurant.name} (ID: {restaurant.id})")
        except Exception:
             await db.rollback()
             print("⚠️ Restaurant likely exists")
             from sqlalchemy import select
             res = await db.execute(select(Restaurant).where(Restaurant.name == "Razorpay Test Foods"))
             restaurant = res.scalars().first()

        # 3. Create Category
        category = Category(
            name="Test Curries",
            restaurant_id=restaurant.id,
            is_active=True,
            stock=100
        )
        db.add(category)
        try:
            await db.commit()
            await db.refresh(category)
            print(f"✅ Category created: {category.name} (ID: {category.id})")
        except Exception:
            await db.rollback()
            print("⚠️ Category likely exists")
            from sqlalchemy import select
            res = await db.execute(select(Category).where(Category.name == "Test Curries"))
            category = res.scalars().first()

        # 4. Create Product
        product = Product(
            name="Butter Chicken Test",
            description="Delicious verification chicken",
            price=500.00,
            is_available=True,
            restaurant_id=restaurant.id,
            category_id=category.id
        )
        db.add(product)
        try:
            await db.commit()
            await db.refresh(product)
            print(f"✅ Product created: {product.name} (ID: {product.id})")
        except Exception:
            await db.rollback()
            print("⚠️ Product likely exists")
            
        print("\n🎉 Seeding Complete!")
        print(f"👉 Login with: {test_user.email} / password123")
        print(f"👉 Product ID to buy: {product.id} if successful")

if __name__ == "__main__":
    asyncio.run(seed_data())
