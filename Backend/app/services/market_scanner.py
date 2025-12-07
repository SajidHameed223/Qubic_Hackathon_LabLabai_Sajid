import time
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.tools.infrastructure_tools import fetch_price_feed
import pandas as pd

class MarketScanner:
    """
    24/7 Market Scanner (The Radar)
    
    Continuously monitors assets for:
    - Price changes (> X%)
    - Target price hits (Sniper targets)
    - Technical Analysis (RSI)
    """
    
    def __init__(self):
        self.targets: Dict[str, float] = {}  # Asset -> Target Price
        self.alerts: List[Dict[str, Any]] = []
        self.running = False
        self.thread = None
        self.assets_to_watch = ["QUBIC", "BTC", "ETH", "SOL"]
        self.price_history: Dict[str, List[float]] = {asset: [] for asset in self.assets_to_watch}
        
    def start(self):
        """Start the background scanning thread"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.thread.start()
        print("📡 Market Scanner ACTIVATED (with Technical Analysis)")

    def stop(self):
        """Stop the scanner"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("📡 Market Scanner DEACTIVATED")

    def set_target(self, asset: str, price: float):
        """Set a sniper target"""
        self.targets[asset.upper()] = price
        print(f"🎯 Sniper Target Set: {asset} @ ${price}")

    def _scan_loop(self):
        """Main scanning loop"""
        while self.running:
            try:
                for asset in self.assets_to_watch:
                    self._check_asset(asset)
                
                # Scan every 60 seconds
                time.sleep(60)
            except Exception as e:
                print(f"⚠️ Scanner Error: {e}")
                time.sleep(60)

    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI manually using Wilder's Smoothing"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _check_asset(self, asset: str):
        """Check a single asset against targets and TA"""
        data = fetch_price_feed({"asset": asset})
        current_price = data.get("price", 0)
        
        if current_price == 0:
            return

        # 1. Update History
        if asset not in self.price_history:
            self.price_history[asset] = []
        
        self.price_history[asset].append(current_price)
        # Keep last 100 candles
        if len(self.price_history[asset]) > 100:
            self.price_history[asset].pop(0)

        # 2. Check Sniper Targets
        target = self.targets.get(asset)
        if target:
            if current_price <= target:
                self._trigger_alert(f"🎯 SNIPER ALERT: {asset} hit target ${target} (Current: ${current_price})")

        # 3. Technical Analysis (RSI)
        if len(self.price_history[asset]) >= 14:
            try:
                df = pd.DataFrame({"close": self.price_history[asset]})
                # Calculate RSI Manually
                rsi_series = self._calculate_rsi(df["close"])
                rsi = rsi_series.iloc[-1]
                
                if not pd.isna(rsi):
                    if rsi < 30:
                        self._trigger_alert(f"📉 RSI OVERSOLD ({rsi:.2f}) for {asset} - BUY SIGNAL")
                    elif rsi > 70:
                        self._trigger_alert(f"📈 RSI OVERBOUGHT ({rsi:.2f}) for {asset} - SELL SIGNAL")
            except Exception as e:
                print(f"⚠️ TA Error for {asset}: {e}")

    def _trigger_alert(self, message: str):
        """Trigger an alert (and potentially an action)"""
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        }
        self.alerts.append(alert)
        print(f"🚨 {message}")
        
        # Hook to Strategy Engine
        try:
            from app.services.strategy_engine import strategy_engine
            strategy_engine.process_alert(alert)
        except Exception as e:
            print(f"⚠️ Failed to trigger strategy: {e}")

# Global Scanner Instance
scanner = MarketScanner()
