import time
import threading
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db import SessionLocal, WalletAccount, WalletLedger, User
from app.services import qubic_client
from app.services.wallet import credit_balance

class DepositListener:
    """
    Monitors Qubic blockchain for incoming deposits to the Agent's wallet.
    Credits the internal Virtual Wallet when funds arrive.
    """
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_checked_tick = 0
        self.agent_identity = qubic_client.QUBIC_WALLET_IDENTITY
        
    def start(self):
        """Start the listener thread"""
        if not self.agent_identity:
            print("⚠️ Deposit Listener: QUBIC_WALLET_IDENTITY not set. Cannot listen for deposits.")
            return
            
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        print(f"📥 Deposit Listener ACTIVATED (Watching {self.agent_identity[:8]}...)")

    def stop(self):
        """Stop the listener"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("📥 Deposit Listener DEACTIVATED")

    def _listen_loop(self):
        """Main polling loop"""
        while self.running:
            try:
                self._check_for_deposits()
                time.sleep(10) # Check every 10 seconds (approx 1 tick)
            except Exception as e:
                print(f"⚠️ Deposit Listener Error: {e}")
                time.sleep(10)

    def _check_for_deposits(self):
        """Poll RPC for new transfers"""
        # Get current network tick
        status = qubic_client.get_current_tick()
        if not status.get("ok"):
            return
            
        current_tick = status["data"].get("tick")
        if not current_tick:
            return
            
        if self.last_checked_tick == 0:
            self.last_checked_tick = current_tick - 10 # Start looking from recent past
            
        if current_tick <= self.last_checked_tick:
            return

        # Fetch transfers
        # Note: RPC might limit range. We fetch in small batches if needed.
        # Here we just fetch last_checked to current.
        resp = qubic_client.get_transfers_for_identity(
            self.agent_identity, 
            self.last_checked_tick, 
            current_tick
        )
        
        if resp.get("ok"):
            transfers = resp.get("data", [])
            self._process_transfers(transfers)
            self.last_checked_tick = current_tick

    def _process_transfers(self, transfers: List[Dict[str, Any]]):
        """Process detected transfers"""
        db = SessionLocal()
        try:
            from app.services.wallet import detect_deposit, get_or_create_wallet
            
            for tx in transfers:
                try:
                    # Check if incoming (dest == agent)
                    if tx.get("destId") != self.agent_identity:
                        continue
                        
                    amount = float(tx.get("amount", 0))
                    tx_id = tx.get("txId")
                    source_id = tx.get("sourceId")
                    
                    if not tx_id or amount <= 0:
                        continue
                    
                    # Incoming deposit: Credit the Primary User
                    # In a real multi-user system, we'd check the memo/payload or source mapping
                    user = db.query(User).first()
                    if not user:
                        print("⚠️ Deposit Listener: No users found to credit.")
                        break
                        
                    # Get wallet (auto-create if needed)
                    # We pass 'user' object, but need to be careful with session attachment
                    # Re-query user in this session to be safe? It is already queried.
                    wallet = get_or_create_wallet(db, user)
                    
                    # Attempt to credit (detect_deposit handles idempotency)
                    from decimal import Decimal
                    ledger = detect_deposit(
                        db,
                        wallet.id,
                        tx_id,
                        Decimal(str(amount))
                    )
                    
                    if ledger:
                        print(f"✅ Deposit Confirmed: +{amount} QUBIC from {source_id[:8]}... (TX: {tx_id[:8]})")
                    else:
                        # Already processed (silently skip)
                        pass
                        
                except Exception as e:
                    print(f"❌ Error processing tx {tx.get('txId', 'unknown')}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Deposit Listener Critical Error: {e}")
        finally:
            db.close()

# Global Listener Instance
deposit_listener = DepositListener()
