# app/routers/wallet.py

"""
Virtual Wallet API Router

Provides endpoints for managing custodial virtual wallets:
- Deposit QU to virtual balance
- Withdraw QU to external address
- Check balance and history
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from uuid import uuid4

from ..db import get_db, User
from ..core.deps import get_current_user
from ..services import wallet
from ..config import settings


router = APIRouter(prefix="/wallet", tags=["wallet"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class DepositInitResponse(BaseModel):
    """Response for deposit initialization"""
    deposit_id: str
    agent_address: str
    instructions: str
    min_amount: float
    estimated_confirmations: int


class DepositConfirmRequest(BaseModel):
    """Request to confirm a deposit"""
    tx_hash: str
    amount: Optional[float] = None  # User can provide expected amount


class BalanceResponse(BaseModel):
    """Balance response"""
    asset: str
    available: float
    reserved: float
    total: float


class WithdrawRequest(BaseModel):
    """Withdrawal request"""
    amount: float
    destination: str
    asset: str = "QUBIC"


class LedgerEntry(BaseModel):
    """Ledger entry response"""
    id: str
    kind: str
    amount: float
    asset: str
    description: str
    tx_id: Optional[str]
    created_at: str
    meta: Optional[dict]


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/deposit/init", response_model=DepositInitResponse)
def init_deposit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initialize a deposit.
    
    Returns the agent's wallet address where user should send QU.
    After sending, user calls /deposit/confirm with the tx hash.
    """
    
    # Get or create user's virtual wallet
    user_wallet = wallet.get_or_create_wallet(db, current_user)
    
    # Generate deposit ID for tracking
    deposit_id = str(uuid4())
    
    agent_address = settings.qubic_wallet_identity or "NOT_CONFIGURED"
    
    return DepositInitResponse(
        deposit_id=deposit_id,
        agent_address=agent_address,
        instructions=f"Send QUBIC to {agent_address} then submit the transaction hash via /wallet/deposit/confirm",
        min_amount=1.0,  # Minimum 1 QUBIC
        estimated_confirmations=3  # ~3 minutes on Qubic
    )


@router.post("/deposit/confirm")
def confirm_deposit(
    request: DepositConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Confirm a deposit by submitting the transaction hash.
    
    The system will verify the transaction and credit your virtual balance.
    
    Note: Currently simulated. In production, this would:
    1. Query Qubic RPC for the transaction
    2. Verify it's to the agent's address
    3. Verify the amount
    4. Credit the user's virtual balance
    """
    
    # Get user's wallet
    user_wallet = wallet.get_or_create_wallet(db, current_user)
    
    # TODO: In production, verify the transaction via RPC
    # For now, we'll simulate with the user-provided amount
    if not request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount is required for simulated deposits. In production, this will be auto-detected."
        )
    
    amount = Decimal(str(request.amount))
    
    # --- REAL ON-CHAIN VERIFICATION ---
    # Fetch transaction from RPC and verify receiver/amount
    result = wallet.verify_and_process_deposit(
        db, 
        current_user, 
        request.tx_hash, 
        amount
    )
    
    if not result.get("ok"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deposit verification failed: {result.get('error')}"
        )
        
    return {
        "ok": True,
        "message": f"Deposit of {result.get('amount')} QUBIC verified and credited",
        "tx_hash": result.get("tx_hash"),
        "amount": result.get("amount"),
        "new_balance": result.get("new_balance")
    }


@router.get("/balance", response_model=BalanceResponse)
def get_balance(
    asset: str = "QUBIC",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get your current virtual wallet balance.
    
    Returns:
    - available: Balance you can use
    - reserved: Balance locked for pending operations
    - total: Sum of available + reserved
    """
    
    user_wallet = wallet.get_or_create_wallet(db, current_user)
    balances = wallet.get_total_balance(db, user_wallet.id, asset)
    
    return BalanceResponse(
        asset=asset,
        available=float(balances["available"]),
        reserved=float(balances["reserved"]),
        total=float(balances["total"])
    )


@router.get("/history", response_model=List[LedgerEntry])
def get_history(
    limit: int = 50,
    offset: int = 0,
    kind: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get your transaction history.
    
    Filters:
    - kind: DEPOSIT, WITHDRAWAL, AGENT_EXECUTION, FEE, etc.
    - limit: Max entries to return (default 50)
    - offset: Pagination offset
    """
    
    user_wallet = wallet.get_or_create_wallet(db, current_user)
    ledger = wallet.get_ledger_history(db, user_wallet.id, limit, offset, kind)
    
    return [
        LedgerEntry(
            id=entry.id,
            kind=entry.kind,
            amount=float(entry.amount),
            asset=entry.asset,
            description=entry.description or "",
            tx_id=entry.tx_id,
            created_at=entry.created_at.isoformat() if entry.created_at else "",
            meta=entry.meta
        )
        for entry in ledger
    ]


@router.post("/withdraw")
def withdraw(
    request: WithdrawRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Withdraw funds to an external Qubic address.
    
    This executes a REAL on-chain transaction from the agent's wallet.
    """
    
    user_wallet = wallet.get_or_create_wallet(db, current_user)
    amount = Decimal(str(request.amount))
    
    # Check balance
    available = wallet.get_balance(db, user_wallet.id, request.asset)
    if available < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: {available}, Requested: {amount}"
        )
    
    # Minimum withdrawal
    if amount < Decimal("1"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum withdrawal is 1 QUBIC"
        )
        
    # --- SMART VAULT CHECK ---
    from ..services.smart_vault import check_vault_safety
    if not check_vault_safety(db, current_user, {
        "action": "withdrawal",
        "amount": amount,
        "destination": request.destination,
        "asset": request.asset
    }):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Smart Vault rejected withdrawal: Violation of safety rules (Daily Limit / Whitelist / Paused)"
        )
    
    # Execute REAL withdrawal
    result = wallet.withdraw_to_chain(
        db,
        user_wallet.id,
        request.destination,
        amount,
        request.asset
    )
    
    if not result.get("ok"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Withdrawal failed: {result.get('error')}"
        )
        
    return {
        "ok": True,
        "message": f"Withdrawal of {amount} {request.asset} executed",
        "tx_hash": result.get("tx_id"),
        "destination": request.destination,
        "amount": float(amount),
        "new_balance": float(wallet.get_balance(db, user_wallet.id, request.asset)),
        "status": "broadcasted"
    }


@router.get("/info")
def get_wallet_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete wallet information.
    
    Returns wallet account details, all balances, and summary.
    """
    
    user_wallet = wallet.get_or_create_wallet(db, current_user)
    
    # Get all balances
    balances_data = []
    for asset in ["QUBIC"]:  # Add more assets as needed
        bal = wallet.get_total_balance(db, user_wallet.id, asset)
        balances_data.append({
            "asset": asset,
            "available": float(bal["available"]),
            "reserved": float(bal["reserved"]),
            "total": float(bal["total"])
        })
    
    return {
        "wallet_id": user_wallet.id,
        "type": user_wallet.type,
        "agent_address": user_wallet.onchain_identity,
        "created_at": user_wallet.created_at.isoformat() if user_wallet.created_at else None,
        "balances": balances_data,
        "deposit_address": user_wallet.onchain_identity,
        "instructions": f"To deposit, send QUBIC to {user_wallet.onchain_identity}"
    }
