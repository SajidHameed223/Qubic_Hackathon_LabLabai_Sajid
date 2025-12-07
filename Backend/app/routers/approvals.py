# app/routers/approvals.py

"""
Transaction Approval API

Allows users to:
- View pending approvals
- Approve/reject transactions
- Configure approval settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from ..db import get_db, User
from ..core.deps import get_current_user
from ..services import approval as approval_service
from ..models.approval import (
    ApprovalRequest as ApprovalRequestModel,
    ApprovalDecision,
    ApprovalSummary,
    TransactionApprovalSettings,
    ApprovalStatus
)

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/pending", response_model=ApprovalSummary)
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all pending approval requests.
    
    These are transactions waiting for your approval.
    """
    requests = approval_service.get_pending_approvals(db, current_user)
    
    # Calculate total amount pending
    total_amount = sum(float(req.amount) for req in requests)
    
    return ApprovalSummary(
        pending_count=len(requests),
        total_amount_pending=total_amount,
        requests=[
            ApprovalRequestModel(
                id=req.id,
                user_id=req.user_id,
                task_id=req.task_id or "",
                action=req.action,
                amount=float(req.amount),
                asset=req.asset,
                destination=req.destination,
                description=req.description,
                estimated_fees=float(req.estimated_fees) if req.estimated_fees else None,
                risk_level=req.risk_level,
                status=ApprovalStatus(req.status),
                created_at=req.created_at.isoformat(),
                expires_at=req.expires_at.isoformat(),
                approved_at=req.approved_at.isoformat() if req.approved_at else None,
                meta=req.meta
            )
            for req in requests
        ]
    )


@router.post("/approve/{approval_id}")
def approve_transaction(
    approval_id: str,
    decision: Optional[ApprovalDecision] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve a pending transaction.
    
    After approval, the agent will execute the transaction.
    """
    note = decision.note if decision else None
    
    success = approval_service.approve_request(db, approval_id, note)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found, already processed, or expired"
        )
    
    return {
        "ok": True,
        "message": "Transaction approved",
        "approval_id": approval_id,
        "status": "approved",
        "note": "The agent will execute this transaction shortly"
    }


@router.post("/reject/{approval_id}")
def reject_transaction(
    approval_id: str,
    decision: Optional[ApprovalDecision] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reject a pending transaction.
    
    The transaction will NOT be executed.
    """
    note = decision.note if decision else None
    
    success = approval_service.reject_request(db, approval_id, note)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found or already processed"
        )
    
    return {
        "ok": True,
        "message": "Transaction rejected",
        "approval_id": approval_id,
        "status": "rejected"
    }


@router.get("/history")
def get_approval_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get your approval history.
    
    Shows all past approvals, rejections, and auto-approvals.
    """
    requests = approval_service.get_approval_history(db, current_user, limit, offset)
    
    return {
        "total": len(requests),
        "approvals": [
            {
                "id": req.id,
                "action": req.action,
                "amount": float(req.amount),
                "asset": req.asset,
                "description": req.description,
                "status": req.status,
                "created_at": req.created_at.isoformat(),
                "approved_at": req.approved_at.isoformat() if req.approved_at else None,
                "rejected_at": req.rejected_at.isoformat() if req.rejected_at else None,
                "decision_note": req.decision_note
            }
            for req in requests
        ]
    }


@router.get("/settings", response_model=TransactionApprovalSettings)
def get_approval_settings(
    current_user: User = Depends(get_current_user)
):
    """
    Get your approval settings.
    
    These control when you're asked for approval vs. auto-approval.
    """
    return approval_service.get_approval_settings(current_user)


@router.put("/settings", response_model=TransactionApprovalSettings)
def update_approval_settings(
    settings: TransactionApprovalSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update your approval settings.
    
    Example:
    ```json
    {
      "auto_approve_threshold": 100.0,
      "require_approval_for_withdrawals": true,
      "require_approval_for_trades": false,
      "require_approval_for_defi": false
    }
    ```
    
    Transactions below the threshold are auto-approved.
    Specific actions can always require approval.
    """
    current_user.approval_settings = settings.model_dump()
    db.commit()
    
    return settings


@router.get("/check/{approval_id}")
def check_approval_status(
    approval_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check the status of an approval request.
    
    Useful for polling while waiting for approval.
    """
    status_str = approval_service.check_approval_status(db, approval_id)
    
    if not status_str:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )
    
    return {
        "approval_id": approval_id,
        "status": status_str,
        "can_execute": status_str in ["approved", "auto_approved"]
    }
