from sqlalchemy import Column, String, DateTime, Integer, Numeric, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class WalletAccount(Base):
    """Virtual wallet account for each user"""
    __tablename__ = "wallet_accounts"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Account type
    type = Column(String, default="agent_custody")  # agent_custody, external, etc.
    
    # On-chain identity (agent's wallet for custodial accounts)
    onchain_identity = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wallet_accounts")
    balances = relationship("WalletBalance", back_populates="wallet_account", cascade="all, delete-orphan")
    ledger_entries = relationship("WalletLedger", back_populates="wallet_account", cascade="all, delete-orphan")


class WalletBalance(Base):
    """Balance for each asset in a wallet account"""
    __tablename__ = "wallet_balances"
    
    id = Column(String, primary_key=True, index=True)
    wallet_account_id = Column(String, ForeignKey("wallet_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Asset details
    asset = Column(String, nullable=False, default="QUBIC")  # QUBIC, USDT, BTC, etc.
    
    # Balance tracking
    balance = Column(Numeric(precision=20, scale=8), default=0, nullable=False)  # Available balance
    reserved = Column(Numeric(precision=20, scale=8), default=0, nullable=False)  # Reserved for pending orders/tx
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wallet_account = relationship("WalletAccount", back_populates="balances")


class WalletLedger(Base):
    """Internal ledger tracking all wallet movements"""
    __tablename__ = "wallet_ledger"
    
    id = Column(String, primary_key=True, index=True)
    wallet_account_id = Column(String, ForeignKey("wallet_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction type
    kind = Column(String, nullable=False)  # DEPOSIT, WITHDRAWAL, INTERNAL_TRADE, FEE, AGENT_EXECUTION, etc.
    
    # Amount details
    amount = Column(Numeric(precision=20, scale=8), nullable=False)
    asset = Column(String, nullable=False, default="QUBIC")
    
    # On-chain transaction reference (if applicable)
    tx_id = Column(String, nullable=True, index=True)
    tx_tick = Column(Integer, nullable=True)
    
    # Source/destination for internal transfers
    source_wallet_id = Column(String, nullable=True)
    dest_wallet_id = Column(String, nullable=True)
    
    # Metadata
    meta = Column(JSON, nullable=True)  # task_id, reason, description, etc.
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    wallet_account = relationship("WalletAccount", back_populates="ledger_entries")
