# app/models/approval.py

"""
Transaction Approval Models

Allows users to set thresholds for automatic vs. manual approval.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ApprovalStatus(str, Enum):
    """Status of approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"
    EXPIRED = "expired"


class TransactionApprovalSettings(BaseModel):
    """User's approval preferences"""
    
    # Auto-approve amount threshold
    auto_approve_threshold: float = Field(
        default=100.0,
        description="Transactions below this amount are auto-approved (in QUBIC)"
    )
    
    # Require approval for specific actions
    require_approval_for_withdrawals: bool = Field(
        default=True,
        description="Always require approval for withdrawals (even small)"
    )
    
    require_approval_for_trades: bool = Field(
        default=False,
        description="Require approval for all trades"
    )
    
    require_approval_for_defi: bool = Field(
        default=False,
        description="Require approval for DeFi operations (lending, staking, etc.)"
    )
    
    # Notification settings
    notify_on_auto_approve: bool = Field(
        default=True,
        description="Send notification when transaction is auto-approved"
    )
    
    # Expiry for pending approvals
    approval_timeout_hours: int = Field(
        default=24,
        description="Hours before pending approval expires"
    )
    
    # --- SMART VAULT SETTINGS ---
    daily_spend_limit: float = Field(
        default=5000.0,
        description="Maximum total daily spending limit (Smart Vault)"
    )
    
    max_transaction_limit: float = Field(
        default=10000.0,
        description="Maximum single transaction limit (Smart Vault)"
    )
    
    whitelisted_addresses: List[str] = Field(
        default=[],
        description="List of allowed destination addresses (Smart Vault)"
    )
    
    is_paused: bool = Field(
        default=False,
        description="Emergency shutdown: Pause all agent transactions"
    )


class ApprovalRequest(BaseModel):
    """Request for user approval"""
    id: str
    user_id: str
    task_id: str
    
    # Transaction details
    action: str  # "send_qu", "stake", "swap", etc.
    amount: float
    asset: str
    destination: Optional[str] = None
    
    # Additional context
    description: str
    estimated_fees: Optional[float] = None
    risk_level: str = "low"  # low, medium, high
    
    # Status
    status: ApprovalStatus
    created_at: str
    expires_at: str
    approved_at: Optional[str] = None
    
    # Metadata
    meta: Optional[dict] = None


class ApprovalDecision(BaseModel):
    """User's decision on approval request"""
    approval_id: str
    decision: str  # "approve" or "reject"
    note: Optional[str] = None  # User's reason


class ApprovalSummary(BaseModel):
    """Summary of pending approvals"""
    pending_count: int
    total_amount_pending: float
    requests: List[ApprovalRequest]


# --- SQLAlchemy Models ---
from sqlalchemy import Column, String, DateTime, Numeric, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class ApprovalRequestRecord(Base):
    """Transaction approval requests (DB Table)"""
    __tablename__ = "approval_requests"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String, nullable=True, index=True)
    
    # Transaction details
    action = Column(String, nullable=False)  # "send_qu", "stake", "swap", etc.
    amount = Column(Numeric(precision=20, scale=8), nullable=False)
    asset = Column(String, default="QUBIC")
    destination = Column(String, nullable=True)
    
    # Additional context
    description = Column(Text, nullable=False)
    estimated_fees = Column(Numeric(precision=20, scale=8), nullable=True)
    risk_level = Column(String, default="low")  # low, medium, high
    
    # Status
    status = Column(String, default="pending", index=True)  # pending, approved, rejected, auto_approved, expired
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    
    # Metadata
    meta = Column(JSON, nullable=True)
    decision_note = Column(Text, nullable=True)  # User's reason for approval/rejection
    
    # Relationship
    user = relationship("User", back_populates="approval_requests")
