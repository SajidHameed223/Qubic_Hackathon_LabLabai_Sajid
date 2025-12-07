# 🧪 POSTMAN TESTING GUIDE - Virtual Wallet System

## 🎯 **IMPORTANT CONCEPT FIRST**

### **How the Custodial Wallet Works:**

**❌ OLD WAY (What your frontend might be expecting):**
- User provides their own Qubic wallet address
- User gives you their private seed
- You execute transactions with their wallet

**✅ NEW WAY (What you actually have):**
- Users **DON'T need their own wallet**
- Users just sign up with email/password
- System creates virtual wallet automatically
- Users deposit QU to **AGENT's wallet** address
- System tracks who owns what in database

---

## 📱 **What to Tell Your Frontend Team:**

```javascript
// ❌ DON'T ask users for:
- "Enter your Qubic wallet address"
- "Enter your private seed"
- "Connect your wallet"

// ✅ DO show users:
- "Your balance: 5000 QUBIC" (from /wallet/balance)
- "Deposit address: AGENT_WALLET_ADDRESS" (from /wallet/info)
- "To deposit: Send QU to this address"
```

**Users send funds TO the agent's wallet, not from their own wallet!**

---

## 🚀 **Step-by-Step Postman Testing**

### **STEP 1: Set Up Postman Environment**

Create environment variables:
```
BASE_URL: http://localhost:8000
TOKEN: (will be set after login)
```

---

### **STEP 2: Register a New User**

**Endpoint:** `POST {{BASE_URL}}/auth/register`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "email": "alice@example.com",
  "password": "securepass123",
  "full_name": "Alice Johnson"
}
```

**Expected Response (201):**
```json
{
  "id": "user-uuid-here",
  "email": "alice@example.com",
  "full_name": "Alice Johnson",
  "is_active": true,
  "created_at": "2025-12-05T20:30:00Z"
}
```

**✅ Result:** User created + Virtual wallet auto-created!

---

### **STEP 3: Login to Get JWT Token**

**Endpoint:** `POST {{BASE_URL}}/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "email": "alice@example.com",
  "password": "securepass123"
}
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**📝 Action:** Copy the `access_token` and save it in your Postman environment as `TOKEN`

---

### **STEP 4: Get Wallet Info**

**Endpoint:** `GET {{BASE_URL}}/wallet/info`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
```

**Expected Response (200):**
```json
{
  "wallet_id": "wallet-uuid",
  "type": "agent_custody",
  "agent_address": "UXUFAQMCXZPZBCZVXVDCVLBPSZWAMLZHMAVYMYZBWGZJJKIQPDYBFUFAEPHM",
  "created_at": "2025-12-05T20:30:00Z",
  "balances": [
    {
      "asset": "QUBIC",
      "available": 0.0,
      "reserved": 0.0,
      "total": 0.0
    }
  ],
  "deposit_address": "UXUFAQMCXZPZBCZVXVDCVLBPSZWAMLZHMAVYMYZBWGZJJKIQPDYBFUFAEPHM",
  "instructions": "To deposit, send QUBIC to UXUFAQMCXZPZBCZVXVDCVLBPSZWAMLZHMAVYMYZBWGZJJKIQPDYBFUFAEPHM"
}
```

**✅ Key Info:**
- `agent_address`: This is where users send their QU
- `balances[0].available`: Current available balance (starts at 0)
- `type`: "agent_custody" means custodial wallet

---

### **STEP 5: Check Current Balance**

**Endpoint:** `GET {{BASE_URL}}/wallet/balance`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
```

**Query Parameters (optional):**
```
asset: QUBIC
```

**Expected Response (200):**
```json
{
  "asset": "QUBIC",
  "available": 0.0,
  "reserved": 0.0,
  "total": 0.0
}
```

**✅ Shows:** User's virtual balance (starts at 0)

---

### **STEP 6: Simulate a Deposit**

**Endpoint:** `POST {{BASE_URL}}/wallet/deposit/init`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
```

**Expected Response (200):**
```json
{
  "deposit_id": "deposit-uuid",
  "agent_address": "UXUFAQMCXZPZBCZVXVDCVLBPSZWAMLZHMAVYMYZBWGZJJKIQPDYBFUFAEPHM",
  "instructions": "Send QUBIC to UXUFAQMCXZPZBCZVXVDCVLBPSZWAMLZHMAVYMYZBWGZJJKIQPDYBFUFAEPHM then submit the transaction hash via /wallet/deposit/confirm",
  "min_amount": 1.0,
  "estimated_confirmations": 3
}
```

**📝 In Real Life:**
1. User sends QU on-chain to the agent_address
2. User gets transaction hash
3. User submits tx hash to confirm deposit

---

### **STEP 7: Confirm Deposit (Simulated)**

**Endpoint:** `POST {{BASE_URL}}/wallet/deposit/confirm`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "tx_hash": "SIMULATED_TX_12345",
  "amount": 1000
}
```

**Expected Response (200):**
```json
{
  "ok": true,
  "message": "Deposit of 1000 QUBIC credited to your virtual balance",
  "tx_hash": "SIMULATED_TX_12345",
  "amount": 1000.0,
  "new_balance": 1000.0
}
```

**✅ Result:** Virtual balance increased to 1000 QUBIC!

---

### **STEP 8: Check Updated Balance**

**Endpoint:** `GET {{BASE_URL}}/wallet/balance`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
```

**Expected Response (200):**
```json
{
  "asset": "QUBIC",
  "available": 1000.0,
  "reserved": 0.0,
  "total": 1000.0
}
```

**✅ Confirmed:** Deposit successful!

---

### **STEP 9: View Transaction History**

**Endpoint:** `GET {{BASE_URL}}/wallet/history`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
```

**Query Parameters (optional):**
```
limit: 50
offset: 0
kind: DEPOSIT  (optional filter)
```

**Expected Response (200):**
```json
[
  {
    "id": "ledger-entry-uuid",
    "kind": "DEPOSIT",
    "amount": 1000.0,
    "asset": "QUBIC",
    "description": "Deposit: +1000 QUBIC from on-chain transaction",
    "tx_id": "SIMULATED_TX_12345",
    "created_at": "2025-12-05T20:35:00Z",
    "meta": {}
  }
]
```

**✅ Shows:** Complete transaction ledger

---

### **STEP 10: Ask AI Advisor About Balance**

**Endpoint:** `POST {{BASE_URL}}/advisor/ask`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "question": "What can I do with my current balance?"
}
```

**Expected Response (200):**
```json
{
  "ok": true,
  "advice": "With your virtual balance of 1000.0 QUBIC, and considering your low risk tolerance, I recommend...",
  "suggested_goals": [
    "Stake 500 QUBIC for passive income",
    "Keep 500 QUBIC as reserve"
  ],
  "context_used": {
    "wallet_balance": 1000.0,
    "preferences_applied": true,
    "live_market_data": true,
    "provider": "openai_gpt4o-mini"
  },
  "timestamp": "2025-12-05T20:36:00Z"
}
```

**✅ Advisor sees virtual balance and gives advice!**

---

### **STEP 11: Execute Small Task (Auto-Approved)**

**Endpoint:** `POST {{BASE_URL}}/agent/run`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "goal": "Stake 50 QUBIC"
}
```

**Expected Response (200):**
```json
{
  "id": "task-uuid",
  "goal": "Stake 50 QUBIC",
  "status": "COMPLETED",
  "steps": [...],
  "logs": [
    "[2025-12-05T20:37:00] Task created with goal: Stake 50 QUBIC",
    "[2025-12-05T20:37:00] ✅ Auto-approved: stake 50 QUBIC (below threshold)",
    "[2025-12-05T20:37:01] Task completed successfully."
  ]
}
```

**✅ Result:** Small amount auto-approved and executed!

---

### **STEP 12: Execute Large Task (Requires Approval)**

**Endpoint:** `POST {{BASE_URL}}/agent/run`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "goal": "Swap 500 QUBIC to USDT"
}
```

**Expected Response (200):**
```json
{
  "id": "task-uuid",
  "goal": "Swap 500 QUBIC to USDT",
  "status": "PENDING_APPROVAL",
  "approval_id": "approval-uuid-here",
  "message": "⏸️ Approval required for swap of 500 QUBIC",
  "amount": 500.0,
  "action": "swap",
  "expires_at": "2025-12-06T20:37:00Z",
  "instructions": "Approve this transaction at /approvals/approve/approval-uuid-here"
}
```

**✅ Result:** Large amount requires approval!

**📝 Save the `approval_id` for next step**

---

### **STEP 13: View Pending Approvals**

**Endpoint:** `GET {{BASE_URL}}/approvals/pending`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
```

**Expected Response (200):**
```json
{
  "pending_count": 1,
  "total_amount_pending": 500.0,
  "requests": [
    {
      "id": "approval-uuid-here",
      "action": "swap",
      "amount": 500.0,
      "asset": "QUBIC",
      "description": "Swap 500 QUBIC",
      "risk_level": "medium",
      "status": "pending",
      "created_at": "2025-12-05T20:37:00Z",
      "expires_at": "2025-12-06T20:37:00Z"
    }
  ]
}
```

**✅ Shows:** Transaction waiting for approval

---

### **STEP 14: Approve the Transaction**

**Endpoint:** `POST {{BASE_URL}}/approvals/approve/{approval_id}`

**Replace `{approval_id}` with the actual ID from Step 12**

**Headers:**
```
Authorization: Bearer {{TOKEN}}
Content-Type: application/json
```

**Body (JSON - optional):**
```json
{
  "note": "Looks good, approved"
}
```

**Expected Response (200):**
```json
{
  "ok": true,
  "message": "Transaction approved",
  "approval_id": "approval-uuid-here",
  "status": "approved",
  "note": "The agent will execute this transaction shortly"
}
```

**✅ Transaction approved!**

---

### **STEP 15: Execute the Approved Task**

**Endpoint:** `POST {{BASE_URL}}/agent/execute-approved/{approval_id}`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
```

**Expected Response (200):**
```json
{
  "id": "task-uuid",
  "goal": "Swap 500 QUBIC to USDT",
  "status": "COMPLETED",
  "steps": [...],
  "logs": [
    "[2025-12-05T20:38:00] Task created from approved request",
    "[2025-12-05T20:38:00] ✅ User approved: Swap 500 QUBIC",
    "[2025-12-05T20:38:01] Task completed successfully."
  ]
}
```

**✅ Approved transaction executed!**

---

### **STEP 16: Withdraw Funds**

**Endpoint:** `POST {{BASE_URL}}/wallet/withdraw`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "amount": 100,
  "destination": "EXTERNAL_QUBIC_WALLET_ADDRESS_HERE",
  "asset": "QUBIC"
}
```

**Expected Response (200):**
```json
{
  "ok": true,
  "message": "Withdrawal of 100 QUBIC initiated",
  "tx_hash": "SIMULATED_TX_xyz789",
  "destination": "EXTERNAL_QUBIC_WALLET_ADDRESS_HERE",
  "amount": 100.0,
  "new_balance": 900.0,
  "status": "simulated - will be real on-chain in production"
}
```

**✅ Withdrawal processed!**

---

### **STEP 17: View Approval Settings**

**Endpoint:** `GET {{BASE_URL}}/approvals/settings`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
```

**Expected Response (200):**
```json
{
  "auto_approve_threshold": 100.0,
  "require_approval_for_withdrawals": true,
  "require_approval_for_trades": false,
  "require_approval_for_defi": false,
  "notify_on_auto_approve": true,
  "approval_timeout_hours": 24
}
```

---

### **STEP 18: Update Approval Settings**

**Endpoint:** `PUT {{BASE_URL}}/approvals/settings`

**Headers:**
```
Authorization: Bearer {{TOKEN}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "auto_approve_threshold": 200.0,
  "require_approval_for_trades": true
}
```

**Expected Response (200):**
```json
{
  "auto_approve_threshold": 200.0,
  "require_approval_for_withdrawals": true,
  "require_approval_for_trades": true,
  "require_approval_for_defi": false,
  "notify_on_auto_approve": true,
  "approval_timeout_hours": 24
}
```

**✅ Settings updated! Now auto-approves up to 200 QUBIC**

---

## 📦 **Postman Collection JSON**

Save this as `qubic-wallet.postman_collection.json`:

```json
{
  "info": {
    "name": "Qubic Virtual Wallet API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. Register User",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"alice@example.com\",\n  \"password\": \"securepass123\",\n  \"full_name\": \"Alice Johnson\"\n}"
        },
        "url": {
          "raw": "{{BASE_URL}}/auth/register",
          "host": ["{{BASE_URL}}"],
          "path": ["auth", "register"]
        }
      }
    },
    {
      "name": "2. Login",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"alice@example.com\",\n  \"password\": \"securepass123\"\n}"
        },
        "url": {
          "raw": "{{BASE_URL}}/auth/login",
          "host": ["{{BASE_URL}}"],
          "path": ["auth", "login"]
        }
      }
    },
    {
      "name": "3. Get Wallet Info",
      "request": {
        "method": "GET",
        "header": [{"key": "Authorization", "value": "Bearer {{TOKEN}}"}],
        "url": {
          "raw": "{{BASE_URL}}/wallet/info",
          "host": ["{{BASE_URL}}"],
          "path": ["wallet", "info"]
        }
      }
    },
    {
      "name": "4. Check Balance",
      "request": {
        "method": "GET",
        "header": [{"key": "Authorization", "value": "Bearer {{TOKEN}}"}],
        "url": {
          "raw": "{{BASE_URL}}/wallet/balance",
          "host": ["{{BASE_URL}}"],
          "path": ["wallet", "balance"]
        }
      }
    },
    {
      "name": "5. Confirm Deposit",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Authorization", "value": "Bearer {{TOKEN}}"},
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"tx_hash\": \"SIMULATED_TX_12345\",\n  \"amount\": 1000\n}"
        },
        "url": {
          "raw": "{{BASE_URL}}/wallet/deposit/confirm",
          "host": ["{{BASE_URL}}"],
          "path": ["wallet", "deposit", "confirm"]
        }
      }
    }
  ]
}
```

---

## 🎨 **Frontend Integration Guide**

### **What Your Frontend Should Show:**

```jsx
// 1. After user logs in
GET /wallet/info
→ Display: 
  - "Deposit Address: AGENT_WALLET_ADDRESS"
  - "Current Balance: 1000 QUBIC"

// 2. Deposit Flow
<DepositWidget>
  <QRCode value={agentAddress} />
  <CopyButton text={agentAddress}>Copy Address</CopyButton>
  <Input placeholder="Paste transaction hash" />
  <Button onClick={confirmDeposit}>Confirm Deposit</Button>
</DepositWidget>

// 3. Balance Display
<BalanceCard>
  <Available>{balance.available} QUBIC</Available>
  <Reserved>{balance.reserved} QUBIC</Reserved>
  <Total>{balance.total} QUBIC</Total>
</BalanceCard>

// 4. Approval Queue
<ApprovalQueue>
  {pendingApprovals.map(approval => (
    <ApprovalCard>
      <Description>{approval.description}</Description>
      <Amount>{approval.amount} {approval.asset}</Amount>
      <Button onClick={() => approve(approval.id)}>Approve</Button>
      <Button onClick={() => reject(approval.id)}>Reject</Button>
    </ApprovalCard>
  ))}
</ApprovalQueue>
```

---

## ✅ **Complete Testing Checklist**

- [ ] Register new user
- [ ] Login and get JWT token
- [ ] Get wallet info (see agent address)
- [ ] Check initial balance (should be 0)
- [ ] Simulate deposit
- [ ] Check updated balance
- [ ] View transaction history
- [ ] Ask advisor about balance
- [ ] Execute small task (auto-approved)
- [ ] Execute large task (requires approval)
- [ ] View pending approvals
- [ ] Approve transaction
- [ ] Execute approved task
- [ ] Withdraw funds
- [ ] View approval settings
- [ ] Update approval settings

---

**You're ready to test! Import the Postman collection and start testing! 🚀**
