from typing import Dict, Any
from app.db import SessionLocal, User
# Circular import risk: scanner imports strategy, strategy imports scanner?
# Better to have scanner emit events, and strategy listen.
# For now, I'll just pass the alert data.

class StrategyEngine:
    """
    The Brain that decides what to do with Market Signals.
    """
    
    def __init__(self):
        # Default Strategy: Buy $100 worth of QUBIC when RSI is oversold
        self.active_strategies = {
            "RSI_BUY": {
                "enabled": False, # Disabled by default for safety
                "amount_usd": 100, 
                "asset": "QUBIC"
            }
        }
        
    def process_alert(self, alert: Dict[str, Any]):
        """
        Decide whether to act on a scanner alert.
        """
        message = alert.get("message", "")
        print(f"🧠 Strategy Engine received: {message}")
        
        if "RSI OVERSOLD" in message:
            self._handle_rsi_oversold(message)

    def _handle_rsi_oversold(self, message: str):
        strat = self.active_strategies.get("RSI_BUY")
        if not strat or not strat["enabled"]:
            print("🧠 Strategy RSI_BUY is disabled. Ignoring.")
            return

        # Parse Asset from message: "📉 RSI OVERSOLD (25.00) for QUBIC - BUY SIGNAL"
        try:
            parts = message.split(" for ")
            if len(parts) > 1:
                asset = parts[1].split(" - ")[0]
                
                # Execute
                self._execute_trade(asset, strat["amount_usd"])
        except Exception as e:
            print(f"🧠 Error parsing alert: {e}")

    def _execute_trade(self, asset: str, amount_usd: float):
        print(f"🤖 AUTOPILOT ENGAGED: Attempting to BUY ${amount_usd} of {asset}")
        
        db = SessionLocal()
        try:
            user = db.query(User).first()
            if not user:
                print("❌ No user found to execute trade for.")
                return

            # 1. Safety Check (Smart Vault)
            # We need to import check_vault_safety here to avoid circular imports at top level if possible
            from app.services.smart_vault import check_vault_safety
            
            # Convert USD to Asset units (approx)
            # We need price.
            from app.tools.infrastructure_tools import fetch_price_feed
            price_data = fetch_price_feed({"asset": asset})
            price = price_data.get("price", 0)
            
            if price == 0:
                print("❌ Price is zero, cannot trade.")
                return
                
            amount_asset = amount_usd / price
            
            safety_params = {
                "action": "trade",
                "amount": amount_asset,
                "asset": asset,
                "destination": "DEX_ROUTER" # Simulated destination
            }
            
            if not check_vault_safety(db, user, safety_params):
                print(f"🛡️ Strategy Blocked by Smart Vault: Safety Violation")
                return

            # 2. Execute Trade
            # Since we don't have a real DEX connection yet, we log this as a "Paper Trade"
            # or a "Signal Execution".
            # In the future, this calls `wallet.withdraw_to_chain(..., destination=DEX)`
            
            print(f"🚀 ORDER PLACED: BUY {amount_asset:.4f} {asset} (@ ${price})")
            # TODO: Record in DB as a Trade
            
        except Exception as e:
            print(f"❌ Strategy Execution Failed: {e}")
        finally:
            db.close()

# Global Instance
strategy_engine = StrategyEngine()
