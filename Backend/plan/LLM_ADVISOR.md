# 🤖 LLM Advisor - Your Personal Qubic Financial Advisor

## ✨ Overview

The **LLM Advisor** is an AI-powered financial advisor that provides real-time, personalized advice based on:
- ✅ Your Qubic wallet balance
- ✅ Recent transfer activity  
- ✅ Your task execution history
- ✅ Current market conditions
- ✅ Your usage patterns

## 🚀 Quick Start

### 1. **Ask a Question**

```bash
curl -X POST http://localhost:8000/advisor/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "question": "Can I safely send 500 QU right now?"
  }'
```

**Response:**
```json
{
  "ok": true,
  "advice": "Based on your current balance of 10,000 QU, yes, you can safely send 500 QU. This represents only 5% of your total balance, leaving you with a healthy reserve of 9,500 QU. Given your recent activity shows minimal outgoing transfers this week, this transaction won't impact your liquidity. I recommend proceeding with the transfer.",
  "suggested_goals": [
    "Monitor wallet balance and send alert if drops below threshold",
    "Fetch current QUBIC price and market trends",
    "Analyze recent transfers and calculate net flow"
  ],
  "context_used": {
    "wallet_balance": 10000,
    "recent_tasks_count": 3,
    "wallet_identity": "YOUR_WALLET_ID"
  },
  "timestamp": "2025-12-05T16:45:00Z"
}
```

### 2. **Get Quick Advice**

```bash
curl -X POST http://localhost:8000/advisor/quick \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "scenario": "weekly_summary"
  }'
```

### 3. **Get Suggested Goals**

```bash
curl http://localhost:8000/advisor/suggestions \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
[
  "Set up automated portfolio rebalancing",
  "Create a yield farming strategy with 50% of balance",
  "Fetch current QUBIC price and market trends"
]
```

## 📚 API Endpoints

### **POST /advisor/ask**
Ask the advisor any question about your wallet or finances.

**Request:**
```json
{
  "question": "What should I do with my current balance?",
  "wallet_identity": "optional-override-wallet"
}
```

**Response:**
```json
{
  "ok": true,
  "advice": "AI-generated advice...",
  "suggested_goals": ["goal1", "goal2"],
  "context_used": {...},
  "timestamp": "ISO-8601"
}
```

### **POST /advisor/quick**
Get quick advice for common scenarios.

**Scenarios:**
- `send_qu` - "Can I safely send X QU?"
- `balance_check` - "What's my current balance situation?"
- `weekly_summary` - "Summarize my activity this week"
- `strategy` - "Suggest a DeFi strategy"

**Request:**
```json
{
  "scenario": "send_qu",
  "amount": 1000
}
```

### **GET /advisor/suggestions**
Get suggested agent goals based on your activity.

**Response:**
```json
[
  "Set up automated portfolio rebalancing",
  "Create a yield farming strategy",
  "Schedule weekly portfolio health check"
]
```

### **GET /advisor/status**
Get your current wallet status and activity summary.

**Response:**
```json
{
  "user": {
    "email": "user@example.com",
    "member_since": "2025-12-01",
    "total_tasks_last_week": 5
  },
  "wallet": {
    "identity": "YOUR_WALLET_ID",
    "balance": {...},
    "recent_transfers_count": 3
  },
  "recent_tasks": [...]
}
```

## 💡 Example Questions

### **Balance & Safety**
- "Can I safely send 500 QU right now?"
- "What's my current balance and is it healthy?"
- "How much should I keep in reserve?"

### **Activity Analysis**
- "How much have I sent this week?"
- "What's my net flow for the past 7 days?"
- "Summarize my wallet activity"

### **Strategy & Planning**
- "What DeFi strategy do you recommend?"
- "Should I stake my QU tokens?"
- "How can I maximize yield with my current balance?"

### **Risk Management**
- "Am I overexposed to any particular strategy?"
- "What are the risks with my current holdings?"
- "Should I diversify?"

## 🎯 Context Awareness

The advisor has access to:

### **1. Wallet Data**
```python
- Current balance
- Recent transfers (in/out)
- Current network tick
```

### **2. User Activity**
```python
- Total tasks executed (last 7 days)
- Recent task goals and results
- Task success/failure rates
- Usage patterns
```

### **3. Market Data** (if available)
```python
- Current QUBIC price
- Market trends
- Network conditions
```

## 🔄 Using Suggested Goals

The advisor provides actionable goals you can execute directly:

```bash
# 1. Get suggestions
SUGGESTIONS=$(curl -s http://localhost:8000/advisor/suggestions \
  -H "Authorization: Bearer $TOKEN")

# 2. Pick a goal
GOAL=$(echo $SUGGESTIONS | jq -r '.[0]')

#3. Execute it
curl -X POST http://localhost:8000/agent/run \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"goal\": \"$GOAL\"}"
```

## 🤖 How It Works

```
┌─────────────┐
│ User Question│
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│ Gather Context           │
│ - Wallet balance         │
│ - Recent transfers       │
│ - Task history           │
│ - User activity          │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Build System Prompt      │
│ - User profile           │
│ - Current state          │
│ - Recent activity        │
│ - Guidelines             │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Call LLM (GPT-4)         │
│ - Analyze context        │
│ - Generate advice        │
│ - Consider risks         │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Return Advice            │
│ - Natural language       │
│ - Action items           │
│ - Suggested goals        │
└──────────────────────────┘
```

## 💻 Frontend Integration

### **React Example**

```jsx
function Advisor() {
  const [question, setQuestion] = useState('');
  const [advice, setAdvice] = useState(null);
  const token = localStorage.getItem('token');

  async function askQuestion() {
    const response = await fetch('http://localhost:8000/advisor/ask', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question })
    });
    const data = await response.json();
    setAdvice(data);
  }

  return (
    <div>
      <input 
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask your advisor..."
      />
      <button onClick={askQuestion}>Ask</button>
      
      {advice && (
        <div>
          <p>{advice.advice}</p>
          <h3>Suggested Actions:</h3>
          <ul>
            {advice.suggested_goals.map(goal => (
              <li key={goal}>{goal}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

### **JavaScript Example**

```javascript
async function getWeeklySummary() {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:8000/advisor/quick', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      scenario: 'weekly_summary'
    })
  });
  
  const data = await response.json();
  console.log(data.advice);
}
```

## 🎨 UI Ideas

### **Chat Interface**
```
You: Can I safely send 500 QU?

Advisor: Based on your current balance of 10,000 QU, 
         yes you can safely send 500 QU. This represents 
         only 5% of your holdings...

         💡 Suggested Actions:
         • Monitor balance after transfer
         • Set up low balance alert
```

### **Dashboard Widget**
```
┌─────────────────────────────────────┐
│ 🤖 Your AI Advisor                  │
├─────────────────────────────────────┤
│ Quick Insights:                     │
│ • Balance: Healthy (10,000 QU)     │
│ • Activity: Active (5 tasks/week)  │
│ • Recommendation: Consider staking │
│                                     │
│ [Ask a Question] [Weekly Summary]   │
└─────────────────────────────────────┘
```

## 🔒 Privacy & Security

- ✅ All advice is personalized to YOU
- ✅ Requires authentication (JWT token)
- ✅ No data is shared with third parties
- ✅ Wallet data is fetched in real-time
- ✅ LLM only sees aggregated data

## 🎯 Best Practices

1. **Ask specific questions** for better advice
2. **Review suggestions** before executing
3. **Use quick scenarios** for common tasks
4. **Check status** regularly to monitor health
5. **Combine with agent** for automated execution

## 🚀 Next Steps

1. **Try it now**: Ask your first question
2. **Integrate in frontend**: Add chat interface
3. **Automate**: Execute suggested goals
4. **Monitor**: Check weekly summaries

**Your personal AI financial advisor is ready to help! 🎉**
