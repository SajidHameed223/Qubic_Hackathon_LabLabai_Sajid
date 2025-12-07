# app/services/wallet.py

"""
Virtual Wallet Service

Manages custodial virtual wallets for users. The agent holds the actual QU on-chain,
while users have virtual balances tracked in the database.
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session

from ..db import User, WalletAccount, WalletBalance, WalletLedger
from ..config import settings
from . import qubic_client


def create_wallet_account(db: Session, user: User) -> WalletAccount:
    """
    Create a virtual wallet account for a user.
    
    The account is linked to the agent's on-chain identity.
    """
    wallet_id = str(uuid4())
    
    wallet = WalletAccount(
        id=wallet_id,
        user_id=user.id,
        type="agent_custody",
        onchain_identity=settings.qubic_wallet_identity,  # Agent's wallet
        created_at=datetime.utcnow()
    )
    
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    
    # Create initial QUBIC balance entry
    balance = WalletBalance(
        id=str(uuid4()),
        wallet_account_id=wallet.id,
        asset="QUBIC",
        balance=Decimal("0"),
        reserved=Decimal("0")
    )
    
    db.add(balance)
    db.commit()
    
    return wallet


def get_or_create_wallet(db: Session, user: User) -> WalletAccount:
    """Get user's wallet account, create if doesn't exist"""
    wallet = db.query(WalletAccount).filter(WalletAccount.user_id == user.id).first()
    
    if not wallet:
        wallet = create_wallet_account(db, user)
    
    return wallet


def get_balance(db: Session, wallet_account_id: str, asset: str = "QUBIC") -> Decimal:
    """Get available balance for an asset"""
    balance = (
        db.query(WalletBalance)
        .filter(
            WalletBalance.wallet_account_id == wallet_account_id,
            WalletBalance.asset == asset
        )
        .first()
    )
    
    if not balance:
        return Decimal("0")
    
    return balance.balance


def get_total_balance(db: Session, wallet_account_id: str, asset: str = "QUBIC") -> Dict[str, Decimal]:
    """Get total balance (available + reserved)"""
    balance = (
        db.query(WalletBalance)
        .filter(
            WalletBalance.wallet_account_id == wallet_account_id,
            WalletBalance.asset == asset
        )
        .first()
    )
    
    if not balance:
        return {"available": Decimal("0"), "reserved": Decimal("0"), "total": Decimal("0")}
    
    return {
        "available": balance.balance,
        "reserved": balance.reserved,
        "total": balance.balance + balance.reserved
    }


def credit_balance(
    db: Session,
    wallet_account_id: str,
    amount: Decimal,
    asset: str = "QUBIC",
    kind: str = "DEPOSIT",
    tx_id: Optional[str] = None,
    description: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> WalletLedger:
    """
    Credit (add to) a wallet balance.
    
    Creates a ledger entry and updates the balance.
    """
    # Get or create balance entry
    balance = (
        db.query(WalletBalance)
        .filter(
            WalletBalance.wallet_account_id == wallet_account_id,
            WalletBalance.asset == asset
        )
        .first()
    )
    
    if not balance:
        balance = WalletBalance(
            id=str(uuid4()),
            wallet_account_id=wallet_account_id,
            asset=asset,
            balance=Decimal("0"),
            reserved=Decimal("0")
        )
        db.add(balance)
    
    # Update balance
    balance.balance += amount
    balance.updated_at = datetime.utcnow()
    
    # Create ledger entry
    ledger = WalletLedger(
        id=str(uuid4()),
        wallet_account_id=wallet_account_id,
        kind=kind,
        amount=amount,
        asset=asset,
        tx_id=tx_id,
        description=description or f"{kind}: +{amount} {asset}",
        meta=meta or {},
        created_at=datetime.utcnow()
    )
    
    db.add(ledger)
    db.commit()
    db.refresh(ledger)
    
    return ledger


def debit_balance(
    db: Session,
    wallet_account_id: str,
    amount: Decimal,
    asset: str = "QUBIC",
    kind: str = "WITHDRAWAL",
    tx_id: Optional[str] = None,
    description: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> Optional[WalletLedger]:
    """
    Debit (subtract from) a wallet balance.
    
    Returns None if insufficient balance.
    """
    balance = (
        db.query(WalletBalance)
        .filter(
            WalletBalance.wallet_account_id == wallet_account_id,
            WalletBalance.asset == asset
        )
        .first()
    )
    
    if not balance or balance.balance < amount:
        return None  # Insufficient balance
    
    # Update balance
    balance.balance -= amount
    balance.updated_at = datetime.utcnow()
    
    # Create ledger entry
    ledger = WalletLedger(
        id=str(uuid4()),
        wallet_account_id=wallet_account_id,
        kind=kind,
        amount=-amount,  # Negative for debits
        asset=asset,
        tx_id=tx_id,
        description=description or f"{kind}: -{amount} {asset}",
        meta=meta or {},
        created_at=datetime.utcnow()
    )
    
    db.add(ledger)
    db.commit()
    db.refresh(ledger)
    
    return ledger


def reserve_balance(
    db: Session,
    wallet_account_id: str,
    amount: Decimal,
    asset: str = "QUBIC"
) -> bool:
    """
    Reserve balance for pending operations.
    
    Moves from 'balance' to 'reserved'.
    Returns True if successful, False if insufficient balance.
    """
    balance = (
        db.query(WalletBalance)
        .filter(
            WalletBalance.wallet_account_id == wallet_account_id,
            WalletBalance.asset == asset
        )
        .first()
    )
    
    if not balance or balance.balance < amount:
        return False
    
    balance.balance -= amount
    balance.reserved += amount
    balance.updated_at = datetime.utcnow()
    
    db.commit()
    return True


def release_reserved(
    db: Session,
    wallet_account_id: str,
    amount: Decimal,
    asset: str = "QUBIC",
    to_balance: bool = True
) -> bool:
    """
    Release reserved balance.
    
    If to_balance=True, moves back to available balance.
    If to_balance=False, removes entirely (used for completed withdrawals).
    """
    balance = (
        db.query(WalletBalance)
        .filter(
            WalletBalance.wallet_account_id == wallet_account_id,
            WalletBalance.asset == asset
        )
        .first()
    )
    
    if not balance or balance.reserved < amount:
        return False
    
    balance.reserved -= amount
    if to_balance:
        balance.balance += amount
    balance.updated_at = datetime.utcnow()
    
    db.commit()
    return True


def get_ledger_history(
    db: Session,
    wallet_account_id: str,
    limit: int = 50,
    offset: int = 0,
    kind: Optional[str] = None
) -> List[WalletLedger]:
    """Get ledger history for a wallet"""
    query = db.query(WalletLedger).filter(
        WalletLedger.wallet_account_id == wallet_account_id
    )
    
    if kind:
        query = query.filter(WalletLedger.kind == kind)
    
    ledger = query.order_by(WalletLedger.created_at.desc()).limit(limit).offset(offset).all()
    
    return ledger


def detect_deposit(
    db: Session,
    wallet_account_id: str,
    tx_id: str,
    amount: Decimal
) -> Optional[WalletLedger]:
    """
    Process a detected deposit.
    
    Checks if already processed, then credits the balance.
    """
    # Check if already processed
    existing = (
        db.query(WalletLedger)
        .filter(
            WalletLedger.wallet_account_id == wallet_account_id,
            WalletLedger.tx_id == tx_id
        )
        .first()
    )
    
    if existing:
        return None  # Already processed
    
    # Credit the balance
    ledger = credit_balance(
        db,
        wallet_account_id,
        amount,
        asset="QUBIC",
        kind="DEPOSIT",
        tx_id=tx_id,
        description=f"Deposit: +{amount} QUBIC from on-chain transaction"
    )
    
    return ledger


def withdraw_to_chain(
    db: Session,
    wallet_account_id: str,
    destination: str,
    amount: Decimal,
    asset: str = "QUBIC"
) -> Dict[str, Any]:
    """
    Execute a real on-chain withdrawal.
    """
    # 1. Check balance and reserve
    if not reserve_balance(db, wallet_account_id, amount, asset):
        return {"ok": False, "error": "Insufficient balance"}
        
    # 2. Execute on-chain TX
    # Qubic uses integers. Ensure amount is integer.
    amount_int = int(amount)
    
    print(f"💸 Initiating Real Withdrawal: {amount_int} QUBIC to {destination}")
    result = qubic_client.send_qu_to_identity(destination, amount_int)
    
    if result.get("ok"):
        # 3. Success: Finalize debit (burn reserved)
        release_reserved(db, wallet_account_id, amount, asset, to_balance=False)
        
        # Record in ledger
        ledger = WalletLedger(
            id=str(uuid4()),
            wallet_account_id=wallet_account_id,
            kind="WITHDRAWAL",
            amount=-amount,
            asset=asset,
            tx_id=result.get("tx_id"),
            description=f"Withdrawal to {destination}",
            created_at=datetime.utcnow()
        )
        db.add(ledger)
        db.commit()
        
        print(f"✅ Withdrawal Success: TX {result.get('tx_id')}")
        return {"ok": True, "tx_id": result.get("tx_id")}
    else:
        # 4. Failure: Refund
        print(f"❌ Withdrawal Failed: {result.get('error')}")
        release_reserved(db, wallet_account_id, amount, asset, to_balance=True)
        return {"ok": False, "error": result.get("error")}


def verify_and_process_deposit(
    db: Session,
    user: User,
    tx_hash: str,
    user_provided_amount: Optional[Decimal] = None
) -> Dict[str, Any]:
    """
    Verify a deposit on-chain and process it if valid.
    """
    # 1. Verify on-chain
    verification = qubic_client.verify_transaction_with_fallback(tx_hash)
    
    if not verification.get("ok"):
        return {"ok": False, "error": verification.get("error")}
        
    # 2. Check Receiver (must be Agent)
    agent_wallet = settings.qubic_wallet_identity
    if verification.get("receiver") != agent_wallet and agent_wallet:
         # Note: If agent wallet not configured, we might skip this check for dev,
         # but in production this is CRITICAL.
         return {
             "ok": False, 
             "error": f"Transaction receiver {verification.get('receiver')} does not match Agent Wallet {agent_wallet}"
         }
    
    # 3. Check Amount
    onchain_amount = Decimal(str(verification.get("amount", 0)))
    if user_provided_amount:
         # Optional: Check if matches what user claimed
         if onchain_amount != user_provided_amount:
             return {
                 "ok": False, 
                 "error": f"Amount mismatch: Transaction has {onchain_amount}, expected {user_provided_amount}"
             }
             
    # 4. Process Deposit
    wallet_account = get_or_create_wallet(db, user)
    ledger = detect_deposit(db, wallet_account.id, tx_hash, onchain_amount)
    
    if not ledger:
        return {"ok": False, "error": "Deposit already processed"}
        
    return {
        "ok": True,
        "amount": float(onchain_amount),
        "tx_hash": tx_hash,
        "new_balance": float(get_balance(db, wallet_account.id, "QUBIC"))
    }
