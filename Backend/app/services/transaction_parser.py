# app/services/transaction_parser.py

"""
Transaction Parser

Extracts transaction details (amount, action) from task goals.
Used to determine if approval is needed.
"""

import re
from decimal import Decimal
from typing import Optional, Dict, Any


def extract_transaction_details(goal: str) -> Dict[str, Any]:
    """
    Parse a task goal to extract transaction details.
    
    Returns:
    {
        "action": "send", "stake", "swap", "withdraw", etc.
        "amount": Decimal or None
        "asset": "QUBIC", "USDT", etc.
        "destination": address if applicable
    }
    """
    goal_lower = goal.lower()
    
    # Extract amount (look for numbers followed by asset name)
    amount = None
    asset = "QUBIC"  # Default
    
    # Common patterns: "500 QUBIC", "1000 QU", "50 USDT"
    amount_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:qubic|qu)\b',
        r'(\d+(?:\.\d+)?)\s*usdt\b',
        r'(\d+(?:\.\d+)?)\s*btc\b',
        r'(\d+(?:\.\d+)?)\s*eth\b',
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, goal_lower)
        if match:
            amount = Decimal(match.group(1))
            # Determine asset from pattern
            if 'usdt' in pattern:
                asset = 'USDT'
            elif 'btc' in pattern:
                asset = 'BTC'
            elif 'eth' in pattern:
                asset = 'ETH'
            else:
                asset = 'QUBIC'
            break
    
    # Determine action
    action = "unknown"
    
    if any(word in goal_lower for word in ['send', 'transfer', 'pay']):
        action = "send"
    elif any(word in goal_lower for word in ['withdraw', 'withdrawal']):
        action = "withdraw"
    elif any(word in goal_lower for word in ['stake', 'staking']):
        action = "stake"
    elif any(word in goal_lower for word in ['swap', 'trade', 'exchange']):
        action = "swap"
    elif any(word in goal_lower for word in ['lend', 'lending', 'deposit']):
        action = "lend"
    elif any(word in goal_lower for word in ['liquidity', 'pool', 'lp']):
        action = "liquidity"
    elif any(word in goal_lower for word in ['farm', 'yield', 'farming']):
        action = "farm"
    elif any(word in goal_lower for word in ['buy', 'purchase']):
        action = "buy"
    elif any(word in goal_lower for word in ['sell']):
        action = "sell"
    
    # Extract destination (wallet addresses or identifiers)
    destination = None
    # Look for Qubic-style addresses (60 chars uppercase)
    address_match = re.search(r'\b([A-Z]{60})\b', goal)
    if address_match:
        destination = address_match.group(1)
    
    return {
        "action": action,
        "amount": amount,
        "asset": asset,
        "destination": destination,
        "requires_amount": amount is not None
    }


def estimate_risk_level(action: str, amount: Optional[Decimal]) -> str:
    """
    Estimate risk level for a transaction.
    
    Returns: "low", "medium", or "high"
    """
    if amount is None:
        return "low"
    
    amount_float = float(amount)
    
    # High-risk actions
    if action in ["withdraw", "send"] and amount_float >= 1000:
        return "high"
    
    # High amounts are high risk
    if amount_float >= 5000:
        return "high"
    
    # Medium risk
    if action in ["swap", "trade"] and amount_float >= 500:
        return "medium"
    
    if amount_float >= 500:
        return "medium"
    
    # Default low risk
    return "low"


def format_transaction_description(details: Dict[str, Any]) -> str:
    """Generate a human-readable description"""
    action = details["action"].title()
    amount = details.get("amount")
    asset = details.get("asset", "QUBIC")
    destination = details.get("destination")
    
    if amount:
        desc = f"{action} {amount} {asset}"
        if destination:
            desc += f" to {destination[:20]}..."
        return desc
    else:
        return f"{action} transaction"
