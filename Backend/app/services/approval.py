# app/services/approval.py

"""
Transaction Approval Service

Handles intelligent approval workflow:
- Auto-approve small transactions
- Request approval for large transactions
- Check user's approval settings
"""

from typing import Dict, Any, Optional
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..db import User, ApprovalRequest
from ..models.approval import TransactionApprovalSettings, ApprovalStatus


def get_approval_settings(user: User) -> TransactionApprovalSettings:
    """Get user's approval settings"""
    settings_dict = user.approval_settings or {}
    return TransactionApprovalSettings(**settings_dict)


def should_require_approval(
    user: User,
    action: str,
    amount: Decimal
) -> bool:
    """
    Check if transaction requires manual approval.
    
    Returns True if approval needed, False if can auto-approve.
    """
    settings = get_approval_settings(user)
    
    # Check action-specific rules
    if action in ["withdraw", "withdrawal"] and settings.require_approval_for_withdrawals:
        return True
    
    if action in ["swap", "trade"] and settings.require_approval_for_trades:
        return True
    
    if action in ["stake", "lend", "liquidity", "farm"] and settings.require_approval_for_defi:
        return True
    
    # Check amount threshold
    if float(amount) >= settings.auto_approve_threshold:
        return True
    
    # Default: auto-approve small amounts
    return False


def _sanitize_for_json(data: Any) -> Any:
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(data, Decimal):
        return float(data)
    if isinstance(data, dict):
        return {k: _sanitize_for_json(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_sanitize_for_json(v) for v in data]
    return data


def create_approval_request(
    db: Session,
    user: User,
    action: str,
    amount: Decimal,
    asset: str = "QUBIC",
    destination: Optional[str] = None,
    description: str = "",
    estimated_fees: Optional[Decimal] = None,
    risk_level: str = "low",
    task_id: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> ApprovalRequest:
    """
    Create a new approval request.
    
    Returns the approval request that must be approved by user.
    """
    settings = get_approval_settings(user)
    
    approval_id = str(uuid4())
    now = datetime.utcnow()
    expires_at = now + timedelta(hours=settings.approval_timeout_hours)
    
    # Sanitize meta for JSON serialization
    sanitized_meta = _sanitize_for_json(meta or {})
    
    request = ApprovalRequest(
        id=approval_id,
        user_id=user.id,
        task_id=task_id,
        action=action,
        amount=amount,
        asset=asset,
        destination=destination,
        description=description or f"{action.title()}: {amount} {asset}",
        estimated_fees=estimated_fees,
        risk_level=risk_level,
        status=ApprovalStatus.PENDING.value,
        created_at=now,
        expires_at=expires_at,
        meta=sanitized_meta
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)
    
    # TODO: Send notification to user
    # send_notification(user, f"Approval needed: {description}")
    
    return request


def auto_approve_transaction(
    db: Session,
    user: User,
    action: str,
    amount: Decimal,
    description: str = "",
    task_id: Optional[str] = None
) -> str:
    """
    Auto-approve a transaction (below threshold).
    
    Returns approval_id for audit trail.
    """
    settings = get_approval_settings(user)
    
    approval_id = str(uuid4())
    now = datetime.utcnow()
    
    request = ApprovalRequest(
        id=approval_id,
        user_id=user.id,
        task_id=task_id,
        action=action,
        amount=amount,
        asset="QUBIC",
        description=description or f"{action.title()}: {amount} QUBIC",
        status=ApprovalStatus.AUTO_APPROVED.value,
        created_at=now,
        expires_at=now,  # Already approved
        approved_at=now
    )
    
    db.add(request)
    db.commit()
    
    # Notify if user wants notifications
    if settings.notify_on_auto_approve:
        # TODO: Send notification
        pass
    
    return approval_id


def approve_request(
    db: Session,
    approval_id: str,
    note: Optional[str] = None
) -> bool:
    """
    Approve a pending request.
    
    Returns True if successful, False if request not found or already processed.
    """
    request = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == approval_id,
        ApprovalRequest.status == ApprovalStatus.PENDING.value
    ).first()
    
    if not request:
        return False
    
    # Check if expired
    if datetime.utcnow() > request.expires_at:
        request.status = ApprovalStatus.EXPIRED.value
        db.commit()
        return False
    
    # Approve
    request.status = ApprovalStatus.APPROVED.value
    request.approved_at = datetime.utcnow()
    request.decision_note = note
    
    db.commit()
    
    return True


def reject_request(
    db: Session,
    approval_id: str,
    note: Optional[str] = None
) -> bool:
    """
    Reject a pending request.
    
    Returns True if successful.
    """
    request = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == approval_id,
        ApprovalRequest.status == ApprovalStatus.PENDING.value
    ).first()
    
    if not request:
        return False
    
    # Reject
    request.status = ApprovalStatus.REJECTED.value
    request.rejected_at = datetime.utcnow()
    request.decision_note = note
    
    db.commit()
    
    return True


def get_pending_approvals(
    db: Session,
    user: User,
    limit: int = 50
) -> list[ApprovalRequest]:
    """Get user's pending approval requests"""
    return db.query(ApprovalRequest).filter(
        ApprovalRequest.user_id == user.id,
        ApprovalRequest.status == ApprovalStatus.PENDING.value,
        ApprovalRequest.expires_at > datetime.utcnow()
    ).order_by(ApprovalRequest.created_at.desc()).limit(limit).all()


def get_approval_history(
    db: Session,
    user: User,
    limit: int = 50,
    offset: int = 0
) -> list[ApprovalRequest]:
    """Get user's approval history"""
    return db.query(ApprovalRequest).filter(
        ApprovalRequest.user_id == user.id
    ).order_by(ApprovalRequest.created_at.desc()).limit(limit).offset(offset).all()


def check_approval_status(
    db: Session,
    approval_id: str
) -> Optional[str]:
    """
    Check if an approval is ready to execute.
    
    Returns status: 'approved', 'pending', 'rejected', 'expired', or None
    """
    request = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == approval_id
    ).first()
    
    if not request:
        return None
    
    # Check expiry
    if request.status == ApprovalStatus.PENDING.value:
        if datetime.utcnow() > request.expires_at:
            request.status = ApprovalStatus.EXPIRED.value
            db.commit()
            return "expired"
    
    return request.status
