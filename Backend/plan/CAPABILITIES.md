# 🚀 Qubic Autopilot Agent: Capabilities Report

## 🧠 The Brain (Strategy Engine)
The agent is now **Proactive**, not just reactive.
- **Autonomous Trading**: Automatically executes trades based on market signals.
- **RSI Strategy**: Buys QUBIC when RSI is **Oversold (<30)**.
- **Configurable**: Enable/Disable strategies and set amounts via the `/strategy` API.

## 📡 The Radar (Market Scanner)
- **Real-Time Feeds**: Monitors QUBIC, BTC, ETH, SOL prices via CoinGecko.
- **Technical Analysis**: Built-in **High-Performance RSI Engine** (custom implementation, no heavy deps).
- **Signal Detection**: Instantly detects market opportunities (Oversold/Overbought).

## 💳 Real Wallet System
- **Auto-Deposits**: Watches the Qubic blockchain and credits your virtual wallet instantly upon receiving funds.
- **Real Withdrawals**: Signs and broadcasts actual on-chain transactions using `qubipy`.
- **Ledger**: Tracks every satoshi in a double-entry ledger system.

## 🛡️ Smart Vault (The Shield)
- **Safety First**: Every transaction (manual or AI-initiated) is vetted by the Vault.
- **Rules**:
  - 🛑 **Daily Limits**: Prevents draining funds.
  - 📝 **Whitelist**: Only allows withdrawals to known addresses.
  - ⏸️ **Emergency Pause**: Instantly freezes all agent activity.

## 🔗 Infrastructure
- **FastAPI**: High-performance REST API.
- **PostgreSQL**: Robust data persistence.
- **Dockerized**: One-command deployment.

---

### 🎮 How to Use
1. **Deposit Funds**: Send QUBIC to the Agent's address.
2. **Enable Autopilot**: POST `/strategy/rsi_buy` with `{"enabled": true, "amount_usd": 100}`.
3. **Watch it Work**: The agent will scan 24/7 and execute trades when the math says "Buy".
