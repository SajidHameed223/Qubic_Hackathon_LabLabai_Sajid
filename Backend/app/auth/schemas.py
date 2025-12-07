from pydantic import BaseModel, EmailStr
from datetime import datetime

# ---------- Request Schemas ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- Response Schemas ----------

class UserPublic(BaseModel):
    id: str
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True   # allows ORM -> Pydantic conversion


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"