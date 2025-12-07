# Qubic Autopilot Worker - Tool Registry

## 🎯 Overview

The Qubic Autopilot Worker now includes **50+ DeFi, RWA, and Infrastructure tools** that the AI planner can intelligently use to accomplish complex on-chain tasks.

## 🏗️ Architecture

```
User Goal → AI Planner → Tool Selection → Execution → Result
```

The AI planner:
1. Receives a natural language goal
2. Discovers available tools from the registry
3. Creates an execution plan using appropriate tools
4. Executes steps sequentially
5. Returns results

## 📚 Tool Categories

### 1. **DeFi Tools** (15 tools)

#### Trading
- `swap_tokens` - Swap tokens on Qubic DEX with slippage protection
- `place_limit_order` - Place limit orders
- `cancel_order` - Cancel existing orders

#### Lending
- `supply_collateral` - Supply assets to earn yield
- `borrow_asset` - Borrow against collateral
- `repay_loan` - Repay borrowed assets
- `withdraw_collateral` - Withdraw supplied collateral

#### Derivatives & Perpetuals
- `open_perp_position` - Open leveraged perpetual positions
- `close_perp_position` - Close perpetual positions
- `buy_option` - Buy call/put options

#### Yield Farming
- `stake_lp_tokens` - Stake LP tokens for rewards
- `harvest_rewards` - Harvest farming rewards
- `compound_rewards` - Auto-compound for higher APY

#### Liquidity
- `add_liquidity` - Add liquidity to DEX pools
- `remove_liquidity` - Remove liquidity from pools

### 2. **RWA (Real World Assets) Tools** (17 tools)

#### Asset Tokenization
- `tokenize_asset` - Tokenize real-world assets (real estate, commodities, securities)
- `fractionalize_asset` - Fractionalize assets for partial ownership
- `transfer_asset_ownership` - Transfer tokenized asset ownership

#### Virtual Wallets
- `create_virtual_wallet` - Create virtual wallets for users/entities
- `fund_virtual_wallet` - Fund wallets with assets
- `withdraw_from_wallet` - Withdraw assets from wallets

#### Payment Rails
- `process_payment` - Process payment transactions
- `batch_payments` - Process multiple payments in one transaction
- `create_payment_link` - Create payment links for invoicing

#### RWA Bridge
- `bridge_asset_to_qubic` - Bridge assets from other chains to Qubic
- `bridge_asset_from_qubic` - Bridge assets from Qubic to other chains

#### Payroll & Subscriptions
- `schedule_payroll` - Schedule recurring payroll payments
- `execute_payroll` - Execute payroll runs
- `create_subscription` - Create recurring subscriptions
- `cancel_subscription` - Cancel subscriptions
- `process_subscription_payment` - Process subscription cycles

#### Crypto Cards
- `issue_crypto_card` - Issue crypto-backed debit cards
- `card_transaction` - Process card transactions

### 3. **Infrastructure Tools** (20+ tools)

#### Oracle & Data Feeds
- `fetch_price_feed` - Get real-time price data
- `publish_oracle_data` - Publish data to oracle network
- `subscribe_to_oracle` - Subscribe to data feed updates

#### Automation
- `create_automation` - Create automated tasks with triggers
- `execute_automation` - Execute automation tasks
- `pause_automation` - Pause active automations

#### Smart Contracts
- `deploy_contract` - Deploy smart contracts to Qubic
- `call_contract_function` - Call contract functions
- `upgrade_contract` - Upgrade contract implementations

#### Monitoring & Alerts
- `create_alert` - Create monitoring alerts
- `check_system_health` - Check system health metrics
- `get_transaction_status` - Get transaction status

#### Developer Tools
- `generate_api_key` - Generate API keys for integrations
- `create_webhook` - Create webhooks for events
- `test_webhook` - Test webhook endpoints

#### Analytics
- `generate_report` - Generate analytics reports
- `track_event` - Track custom events

#### Governance
- `create_proposal` - Create governance proposals
- `vote_on_proposal` - Vote on proposals
- `execute_proposal` - Execute approved proposals

## 🚀 API Endpoints

### Tool Discovery
```bash
# List all tools
GET /tools/list

# List categories
GET /tools/categories

# List tools by category
GET /tools/category/defi
GET /tools/category/rwa
GET /tools/category/infrastructure

# Get tool descriptions (what AI sees)
GET /tools/descriptions

# Get tool statistics
GET /tools/stats
```

### Tool Execution
```bash
# Execute a tool directly
POST /tools/execute/{tool_name}
{
  "param1": "value1",
  "param2": "value2"
}
```

### Agent Endpoints
```bash
# One-shot agent execution
POST /agent/run
{
  "goal": "Swap 1000 QUBIC to USDT and stake the LP tokens"
}

# Webhook trigger (for EasyConnect/Make/n8n)
POST /agent/trigger
{
  "source": "easyconnect",
  "event_type": "LargeDeposit",
  "goal": "Handle large deposit event"
}
```

## 💡 Example Use Cases

### DeFi Strategy
```json
{
  "goal": "Implement a yield farming strategy: swap 5000 QUBIC to USDT, add liquidity to QUBIC/USDT pool, and stake the LP tokens"
}
```

The AI will:
1. Use `swap_tokens` to convert QUBIC to USDT
2. Use `add_liquidity` to create LP tokens
3. Use `stake_lp_tokens` to earn farming rewards

### RWA Tokenization
```json
{
  "goal": "Tokenize a $1M real estate property and fractionalize it into 1000 shares"
}
```

The AI will:
1. Use `tokenize_asset` to create the token
2. Use `fractionalize_asset` to create 1000 shares
3. Set up payment rails for dividend distribution

### Automated Payroll
```json
{
  "goal": "Set up monthly payroll for 50 employees with crypto payments"
}
```

The AI will:
1. Use `create_virtual_wallet` for each employee
2. Use `schedule_payroll` to set up recurring payments
3. Use `execute_payroll` to process payments monthly

### Cross-Chain Bridge
```json
{
  "goal": "Bridge 10 ETH from Ethereum to Qubic and swap to QUBIC tokens"
}
```

The AI will:
1. Use `bridge_asset_to_qubic` to bridge ETH
2. Use `swap_tokens` to convert wETH to QUBIC

## 🔧 Adding New Tools

To add a new tool:

1. Create the handler function:
```python
def my_new_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    # Your implementation
    return {"ok": True, "result": "..."}
```

2. Register it:
```python
registry.register(Tool(
    name="my_new_tool",
    category=ToolCategory.DEFI,
    description="What this tool does",
    parameters={"param1": "string", "param2": "number"},
    handler=my_new_tool,
    examples=["Example usage"]
))
```

3. The AI planner will automatically discover and use it!

## 📊 Tool Statistics

Run `GET /tools/stats` to see:
```json
{
  "total_tools": 52,
  "by_category": {
    "defi": 15,
    "rwa": 17,
    "infrastructure": 15,
    "oracle": 3,
    "governance": 3
  }
}
```

## 🎯 Next Steps

1. **Test the tools**: Use `/tools/execute/{tool_name}` to test individual tools
2. **Try the agent**: Use `/agent/run` with natural language goals
3. **Integrate smart contracts**: Replace simulated tools with real Qubic smart contract calls
4. **Add more tools**: Extend the registry with domain-specific primitives

## 🔐 Security Notes

- Tools are currently in **simulation mode**
- Before production, implement:
  - Authentication & authorization
  - Rate limiting
  - Transaction signing validation
  - Audit logging
  - Parameter validation

## 📝 License

MIT License - See LICENSE file for details
