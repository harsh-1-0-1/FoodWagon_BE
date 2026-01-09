# 🍔 Food Wagon Backend

Food Wagon is a robust, asynchronous backend API for a multi-vendor food delivery platform. Built with **FastAPI** and **PostgreSQL**, it features a comprehensive set of modules for managing users, restaurants, orders, and payments.

## 🚀 Features

-   **Authentication & Users**:
    -   JWT-based Authentication (Login/Register).
    -   **Refresh Token Rotation**: Issue new access tokens with rolling refresh tokens.
    -   **Profile API**: Fetch authenticated user details instantly.
    -   Role-Based Access Control (Admin, Restaurant Owner, User).
    -   **Address Management**: Full CRUD with smart default enforcement.
-   **Restaurant Management**:
    -   Manage Restaurants, Categories, and Products.
    -   Filtering and Search.
-   **Inventory System**:
    -   Real-time stock tracking.
    -   Concurrency handling with Row Locking.
-   **Shopping Experience**:
    -   Persistent Cart management.
    -   Order placement with stock validation.
-   **Payments**:
    -   **Razorpay** Integration.
    -   Secure signature verification.
    -   Automated order status updates.
-   **Delivery**:
    -   **Uber Direct** Integration for last-mile delivery.
    -   Real-time quote generation and automated dispatch.
    -   Public tracking URL management.
-   **Architecture**:
    -   Layered design (Controllers -> Services -> Repositories).
    -   Fully Asynchronous (AsyncIO + SQLAlchemy Async).

## 🛠️ Tech Stack

-   **Framework**: FastAPI (Python 3.12+)
-   **Database**: PostgreSQL
-   **ORM**: SQLAlchemy (Async)
-   **Migrations**: Alembic
-   **Validation**: Pydantic v2
-   **Authentication**: PyJWT (OAuth2 schema)
-   **Payment Gateway**: Razorpay
-   **Server**: Uvicorn

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/food-wagon-be.git
cd food-wagon-be
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:

```ini
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/food_db

# Security
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Payments (Razorpay)
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=your_secret...

# Delivery (Uber Direct)
UBER_DIRECT_CLIENT_ID=your_client_id
UBER_DIRECT_CLIENT_SECRET=your_client_secret
UBER_DIRECT_CUSTOMER_ID=your_customer_id
UBER_DIRECT_AUTH_URL=https://auth.uber.com/oauth/v2/token
UBER_DIRECT_API_BASE=https://api.uber.com

# Optional
FIREBASE_CREDENTIALS_PATH=path/to/firebase.json
```

### 5. Run Database Migrations
Initialize the database schema:
```bash
alembic upgrade head
```

## 🏃‍♂️ Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

### 📚 API Documentation
FastAPI automatically generates interactive documentation:
-   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
-   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 📄 Module Documentation
Detailed technical guides can be found in the `docs/` directory:
- [**Uber Direct Integration**](docs/uber_direct_integration.md)
- [**Delivery Workflow**](docs/delivery_workflow.md)
- [**Postman Testing Guide**](docs/postman_testing.md)

## 📂 Project Structure

```
├── alembic/                # Database migrations
├── controllers/            # API Route Handlers
├── models/                 # SQLAlchemy Database Models
├── repositories/           # Database Access Layer (CRUD)
├── schemas/                # Pydantic Schemas (Request/Response)
├── services/               # Business Logic Layer
├── utils/                  # Helper functions (JWT, Logger, etc.)
├── scripts/                # Utility scripts (Seeding, Testing)
├── main.py                 # Application Entry Point
└── requirements.txt        # Python Dependencies
```

## 🧪 Testing

### Manual Testing
-   **Payment Flow**: Open `payment_test.html` in your browser to test the full checkout and payment cycle.
-   **Delivery Flow**: Refer to the [Postman Testing Guide](docs/postman_testing.md) for a step-by-step manual test of the Uber Direct integration.
-   **Scripts**: Use `scripts/seed_test_data.py` to populate the DB with test users and products.

### Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md) for a high-level system diagram.
