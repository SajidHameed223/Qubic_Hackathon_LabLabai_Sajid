from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db import User, ApprovalRequest

class SmartVault:
    """
    Simulates a Smart Contract Vault on Qubic.
    
    Enforces strict on-chain style rules for transaction safety.
    This acts as the 'Final Guard' before any transaction is signed.
    """
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.settings = user.approval_settings or {}
        
    def validate_transaction(self, tx_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates a transaction against Vault rules.
        Returns {"valid": bool, "reason": str}
        """
        amount = Decimal(str(tx_details.get("amount", 0)))
        action = tx_details.get("action", "unknown")
        destination = tx_details.get("destination")
        
        # Rule 0: Emergency Pause
        if self.settings.get("is_paused", False):
            return {"valid": False, "reason": "Smart Vault is PAUSED (Emergency Shutdown)"}

        # Rule 1: Daily Spending Limit
        if not self._check_daily_limit(amount):
            return {"valid": False, "reason": "Exceeds daily spending limit"}
            
        # Rule 2: Protocol Whitelist
        if not self._check_whitelist(destination, action):
            return {"valid": False, "reason": f"Destination {destination} not in whitelist"}
            
        # Rule 3: Max Transaction Limit
        max_tx = Decimal(str(self.settings.get("max_transaction_limit", 10000)))
        if amount > max_tx:
            return {"valid": False, "reason": f"Transaction exceeds max limit of {max_tx}"}
            
        return {"valid": True, "reason": "Passed all Vault checks"}

    def _check_daily_limit(self, amount: Decimal) -> bool:
        """Check if amount is within daily limit"""
        daily_limit = Decimal(str(self.settings.get("daily_spend_limit", 5000)))
        
        # Calculate total spent today (simulated query)
        # In real implementation, query DB for today's completed transactions
        spent_today = Decimal("0") 
        
        if spent_today + amount > daily_limit:
            return False
        return True

    def _check_whitelist(self, destination: Optional[str], action: str) -> bool:
        """Check if destination is whitelisted"""
        if not destination:
            return True # Some actions don't have destination
            
        whitelist = self.settings.get("whitelisted_addresses", [])
        if not whitelist:
            return True # If no whitelist set, allow all (or default to strict?)
            
        return destination in whitelist

def check_vault_safety(db: Session, user: User, tx_details: Dict[str, Any]) -> bool:
    """Helper to check vault safety"""
    vault = SmartVault(db, user)
    result = vault.validate_transaction(tx_details)
    return result["valid"]
