# app/models/user.py

"""
User-related Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model (includes password)"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response model (no password)"""
    id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data stored in JWT token"""
    user_id: Optional[str] = None
    email: Optional[str] = None


# --- SQLAlchemy Models ---
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User preferences for personalized advice
    preferences = Column(JSON, nullable=True, default={})
    
    # Approval settings for transactions
    approval_settings = Column(JSON, nullable=True, default={
        "auto_approve_threshold": 100.0,
        "require_approval_for_withdrawals": True,
        "require_approval_for_trades": False,
        "require_approval_for_defi": False,
        "notify_on_auto_approve": True,
        "approval_timeout_hours": 24
    })
    
    # Relationships
    tasks = relationship("TaskRecord", back_populates="user", cascade="all, delete-orphan")
    wallet_accounts = relationship("WalletAccount", back_populates="user", cascade="all, delete-orphan")
    approval_requests = relationship("ApprovalRequestRecord", back_populates="user", cascade="all, delete-orphan")
