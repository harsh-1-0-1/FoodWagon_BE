from pydantic import BaseModel, EmailStr


# ==============================
# PASSWORD LOGIN
# ==============================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ==============================
# GOOGLE LOGIN
# ==============================

class GoogleAuthRequest(BaseModel):
    token: str


# ==============================
# TOKEN RESPONSES
# ==============================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict


# ==============================
# REFRESH TOKEN
# ==============================

class RefreshRequest(BaseModel):
    refresh_token: str
