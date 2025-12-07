# 🧪 POSTMAN TESTING GUIDE - AI Tools

## 🎯 **Test AI Agent with 50+ Tools**

---

## **STEP 1: Login (Get Token)**

**Method:** `POST`  
**URL:** `http://localhost:8000/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "email": "test@example.com",
  "password": "testpass123"
}
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**📝 ACTION:** Copy the `access_token` value!

---

## **STEP 2: Test Staking (DeFi Tool)**

**Method:** `POST`  
**URL:** `http://localhost:8000/agent/run`

**Headers:**
```
Authorization: Bearer <paste-your-token-here>
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "goal": "Stake 25 QUBIC"
}
```

**Expected Response:**
```json
{
  "id": "task-uuid",
  "goal": "Stake 25 QUBIC",
  "status": "COMPLETED",
  "steps": [
    {
      "type": "TOOL_EXECUTION",
      "description": "Stake QUBIC tokens",
      "params": {
        "tool_name": "stake_tokens",
        "tool_params": {
          "token": "QUBIC",
          "amount": 25
        }
      },
      "status": "COMPLETED"
    }
  ]
}
```

**✅ Look for:** `"type": "TOOL_EXECUTION"` and `"tool_name": "stake_tokens"`

---

## **STEP 3: Test Token Swap (DeFi Tool)**

**Method:** `POST`  
**URL:** `http://localhost:8000/agent/run`

**Headers:**
```
Authorization: Bearer <your-token>
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "goal": "Swap 100 QUBIC to USDT"
}
```

**Expected Response:**
```json
{
  "goal": "Swap 100 QUBIC to USDT",
  "status": "COMPLETED",
  "steps": [
    {
      "type": "TOOL_EXECUTION",
      "params": {
        "tool_name": "swap_tokens",
        "tool_params": {
          "from_token": "QUBIC",
          "to_token": "USDT",
          "amount": 100
        }
      }
    }
  ]
}
```

**✅ Look for:** `"tool_name": "swap_tokens"` with correct params

---

## **STEP 4: Test Perpetuals (DeFi Tool)**

**Method:** `POST`  
**URL:** `http://localhost:8000/agent/run`

**Headers:**
```
Authorization: Bearer <your-token>
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "goal": "Open a 3x long position on BTC with 1000 QUBIC"
}
```

**Expected Response:**
```json
{
  "goal": "Open a 3x long position on BTC with 1000 QUBIC",
  "status": "COMPLETED",
  "steps": [
    {
      "type": "TOOL_EXECUTION",
      "params": {
        "tool_name": "open_perp_position",
        "tool_params": {
          "market": "BTC-USD",
          "side": "long",
          "leverage": 3,
          "margin": 1000
        }
      }
    }
  ]
}
```

**✅ Look for:** `"tool_name": "open_perp_position"` with leverage=3

---

## **STEP 5: Test Virtual Wallet (RWA Tool)**

**Method:** `POST`  
**URL:** `http://localhost:8000/agent/run`

**Headers:**
```
Authorization: Bearer <your-token>
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "goal": "Create a virtual wallet for Alice"
}
```

**Expected Response:**
```json
{
  "goal": "Create a virtual wallet for Alice",
  "status": "COMPLETED",
  "steps": [
    {
      "type": "TOOL_EXECUTION",
      "params": {
        "tool_name": "create_virtual_wallet",
        "tool_params": {
          "user_id": "Alice"
        }
      }
    }
  ]
}
```

**✅ Look for:** `"tool_name": "create_virtual_wallet"`

---

## **STEP 6: Test Asset Tokenization (RWA Tool)**

**Method:** `POST`  
**URL:** `http://localhost:8000/agent/run`

**Headers:**
```
Authorization: Bearer <your-token>
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "goal": "Tokenize my building worth 1 million dollars"
}
```

**Expected Response:**
```json
{
  "goal": "Tokenize my building worth 1 million dollars",
  "status": "COMPLETED",
  "steps": [
    {
      "type": "TOOL_EXECUTION",
      "params": {
        "tool_name": "tokenize_asset",
        "tool_params": {
          "asset_type": "real_estate",
          "value": 1000000
        }
      }
    }
  ]
}
```

**✅ Look for:** `"tool_name": "tokenize_asset"`

---

## **STEP 7: Test Payroll (RWA Tool)**

**Method:** `POST`  
**URL:** `http://localhost:8000/agent/run`

**Headers:**
```
Authorization: Bearer <your-token>
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "goal": "Schedule monthly payroll for 5 employees"
}
```

**Expected Response:**
```json
{
  "goal": "Schedule monthly payroll for 5 employees",
  "status": "COMPLETED",
  "steps": [
    {
      "type": "TOOL_EXECUTION",
      "params": {
        "tool_name": "schedule_payroll",
        "tool_params": {
          "frequency": "monthly",
          "employee_count": 5
        }
      }
    }
  ]
}
```

**✅ Look for:** `"tool_name": "schedule_payroll"` or `"create_automation"`

---

## **STEP 8: Test Smart Contract (Infrastructure Tool)**

**Method:** `POST`  
**URL:** `http://localhost:8000/agent/run`

**Headers:**
```
Authorization: Bearer <your-token>
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "goal": "Deploy a new smart contract"
}
```

**Expected Response:**
```json
{
  "goal": "Deploy a new smart contract",
  "status": "COMPLETED",
  "steps": [
    {
      "type": "TOOL_EXECUTION",
      "params": {
        "tool_name": "deploy_contract"
      }
    }
  ]
}
```

**✅ Look for:** `"tool_name": "deploy_contract"`

---

## **STEP 9: Test Oracle (Infrastructure Tool)**

**Method:** `POST`  
**URL:** `http://localhost:8000/agent/run`

**Headers:**
```
Authorization: Bearer <your-token>
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "goal": "Set up a price oracle for BTC"
}
```

**Expected Response:**
```json
{
  "goal": "Set up a price oracle for BTC",
  "status": "COMPLETED",
  "steps": [
    {
      "type": "TOOL_EXECUTION",
      "params": {
        "tool_name": "register_oracle_feed",
        "tool_params": {
          "asset": "BTC"
        }
      }
    }
  ]
}
```

**✅ Look for:** `"tool_name": "register_oracle_feed"`

---

## **STEP 10: Test Complex Multi-Step**

**Method:** `POST`  
**URL:** `http://localhost:8000/agent/run`

**Headers:**
```
Authorization: Bearer <your-token>
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "goal": "Maximize yield on 1000 QUBIC by diversifying"
}
```

**Expected Response:**
```json
{
  "goal": "Maximize yield on 1000 QUBIC by diversifying",
  "status": "COMPLETED",
  "steps": [
    {
      "type": "TOOL_EXECUTION",
      "params": {
        "tool_name": "stake_tokens"
      }
    },
    {
      "type": "TOOL_EXECUTION",
      "params": {
        "tool_name": "add_liquidity"
      }
    },
    {
      "type": "TOOL_EXECUTION",
      "params": {
        "tool_name": "lend_assets"
      }
    }
  ]
}
```

**✅ Look for:** Multiple `TOOL_EXECUTION` steps with different tools!

---

## ✅ **What to Check in EVERY Response:**

1. **`"type": "TOOL_EXECUTION"`** - Confirms AI is using tools, not generic steps
2. **`"tool_name": "..."`** - Shows which tool was selected
3. **`"tool_params": {...}`** - Shows AI understood the parameters
4. **`"status": "COMPLETED"`** - Tool executed successfully

---

## ❌ **Old Behavior (Before Fix):**

```json
{
  "steps": [
    {
      "type": "AI_PLAN",  // ❌ Generic, not using tools
      "description": "Plan the task"
    },
    {
      "type": "QUBIC_TX",  // ❌ Generic blockchain tx
      "description": "Execute transaction"
    }
  ]
}
```

## ✅ **New Behavior (Now!):**

```json
{
  "steps": [
    {
      "type": "TOOL_EXECUTION",  // ✅ Using real tool!
      "params": {
        "tool_name": "stake_tokens",  // ✅ Specific tool
        "tool_params": {
          "amount": 25,
          "token": "QUBIC"
        }
      }
    }
  ]
}
```

---

## 🎨 **Try These Creative Goals:**

1. **"Help me earn passive income with 500 QUBIC"**
   - Should use: stake_tokens, lend_assets, or add_liquidity

2. **"I want to trade BTC with 5x leverage"**
   - Should use: open_perp_position

3. **"Create a payment system for my business"**
   - Should use: create_virtual_wallet, process_payment, etc.

4. **"Set up automated DCA for BTC"**
   - Should use: create_automation

5. **"Monitor my wallet for large transactions"**
   - Should use: set_monitoring_alert

---

## 🚀 **Quick Copy-Paste Tests:**

### Test 1: Staking
```json
{"goal": "Stake 25 QUBIC"}
```

### Test 2: Swap
```json
{"goal": "Swap 100 QUBIC to USDT"}
```

### Test 3: Perpetuals
```json
{"goal": "Open 3x long BTC position"}
```

### Test 4: Tokenization
```json
{"goal": "Tokenize my building worth $1M"}
```

### Test 5: Payroll
```json
{"goal": "Schedule monthly payroll for 5 employees"}
```

---

## 📊 **Success Criteria:**

✅ Every response should have `"type": "TOOL_EXECUTION"`  
✅ Tool names should match the goal (stake → stake_tokens, etc.)  
✅ Tool params should be reasonable  
✅ Status should be "COMPLETED"  

---

**🎉 You're testing a REAL AI orchestrator with 50+ tools!**

Just change the `goal` field to any task and watch the AI pick the right tool! 🚀
