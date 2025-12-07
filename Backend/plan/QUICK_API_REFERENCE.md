# 🚀 QUICK POSTMAN REFERENCE

## Base URL
```
http://localhost:8000
```

---

## 🔑 **AUTHENTICATION**

### Register
```
POST /auth/register
{
  "email": "alice@example.com",
  "password": "securepass123",
  "full_name": "Alice Johnson"
}
```

### Login
```
POST /auth/login
{
  "email": "alice@example.com",
  "password": "securepass123"
}
→ Returns: {"access_token": "..."}
→ Copy token, use in headers: Authorization: Bearer <token>
```

---

## 💰 **WALLET ENDPOINTS**

### Get Wallet Info
```
GET /wallet/info
Headers: Authorization: Bearer <token>

Returns agent address where users deposit funds!
```

### Check Balance
```
GET /wallet/balance
Headers: Authorization: Bearer <token>
```

### Simulate Deposit
```
POST /wallet/deposit/confirm
Headers: 
  Authorization: Bearer <token>
  Content-Type: application/json
Body:
{
  "tx_hash": "SIMULATED_TX_12345",
  "amount": 1000
}
```

### View History
```
GET /wallet/history
Headers: Authorization: Bearer <token>
```

### Withdraw
```
POST /wallet/withdraw
Headers: 
  Authorization: Bearer <token>
  Content-Type: application/json
Body:
{
  "amount": 100,
  "destination": "EXTERNAL_WALLET_ADDRESS"
}
```

---

## ✅ **APPROVAL ENDPOINTS**

### Get Settings
```
GET /approvals/settings
Headers: Authorization: Bearer <token>
```

### Update Settings
```
PUT /approvals/settings
Headers: 
  Authorization: Bearer <token>
  Content-Type: application/json
Body:
{
  "auto_approve_threshold": 200.0,
  "require_approval_for_trades": true
}
```

### View Pending
```
GET /approvals/pending
Headers: Authorization: Bearer <token>
```

### Approve
```
POST /approvals/approve/{approval_id}
Headers: Authorization: Bearer <token>
```

### Reject
```
POST /approvals/reject/{approval_id}
Headers: Authorization: Bearer <token>
```

---

## 🤖 **AGENT ENDPOINTS**

### Execute Task (with approval check)
```
POST /agent/run
Headers: 
  Authorization: Bearer <token>
  Content-Type: application/json
Body:
{
  "goal": "Stake 50 QUBIC"
}

→ Small amounts: Auto-approved & executed
→ Large amounts: Returns approval_id for manual approval
```

### Execute Approved Task
```
POST /agent/execute-approved/{approval_id}
Headers: Authorization: Bearer <token>
```

---

## 🧠 **ADVISOR ENDPOINTS**

### Ask Question
```
POST /advisor/ask
Headers: 
  Authorization: Bearer <token>
  Content-Type: application/json
Body:
{
  "question": "What should I do with my balance?"
}
```

### Quick Advice
```
POST /advisor/quick
Headers: 
  Authorization: Bearer <token>
  Content-Type: application/json
Body:
{
  "scenario": "balance_check"
}
```

---

## 📝 **TESTING WORKFLOW**

1. **Register** → Get user account
2. **Login** → Get JWT token (save it!)
3. **Get wallet info** → See deposit address
4. **Deposit** → Simulate adding funds
5. **Check balance** → Confirm funds received
6. **Ask advisor** → Get recommendations
7. **Execute small task** → Auto-approves
8. **Execute large task** → Requires approval
9. **Approve** → Manually approve
10. **Execute approved** → Task runs

---

## 🎯 **QUICK TEST COMMANDS (cURL)**

```bash
# 1. Login and get token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  | jq -r '.access_token')

# 2. Get wallet info
curl -s http://localhost:8000/wallet/info \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. Deposit funds
curl -s -X POST http://localhost:8000/wallet/deposit/confirm \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tx_hash":"TEST_12345","amount":1000}' | jq .

# 4. Check balance
curl -s http://localhost:8000/wallet/balance \
  -H "Authorization: Bearer $TOKEN" | jq .

# 5. Execute task
curl -s -X POST http://localhost:8000/agent/run \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"goal":"Stake 50 QUBIC"}' | jq .
```

---

## ❌ **Common Mistakes**

### 1. **"User needs wallet address?"**
**NO!** Users DON'T provide their wallet. They:
- Sign up with email/password
- Get a virtual wallet automatically
- Deposit to AGENT's address (shown in /wallet/info)

### 2. **"Where to get Qubic wallet?"**
**Not needed!** The system is 100% custodial:
- Agent has ONE wallet for all users
- Users' balances tracked in database
- Users just deposit to agent's address

### 3. **"How to connect wallet?"**
**No wallet connection!** Just:
- Register → Login → Get token
- Use token for all requests

---

## 📱 **Frontend Needs:**

```javascript
// What frontend should do:

// 1. Login
const {access_token} = await login(email, password);
localStorage.setItem('token', access_token);

// 2. Get deposit address
const {deposit_address} = await getWalletInfo();
// Show: "Send QU to: {deposit_address}"

// 3. Check balance
const {available, reserved, total} = await getBalance();
// Show: "Balance: {available} QUBIC"

// 4. No wallet connection needed!
```

---

**See POSTMAN_TESTING_GUIDE.md for detailed examples** 🚀
