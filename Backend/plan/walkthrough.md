# Walkthrough: Portfolio Analysis & Dry Run

I've implemented the two new features you requested to enhance visibility and safety.

## 1. 🔥 Explain My Portfolio

We added a **Natural Language Analytics** endpoint where the AI acts as a sophisticated financial analyst.

### How to use
- **Method**: `GET`
- **Endpoint**: `/advisor/explain`
- **What it does**:
    1. Aggregates your **Virtual Balance** (Available vs Reserved).
    2. Checks for **Pending Approvals** that need your attention.
    3. Reviews your **Recent Agent Tasks** (last 7 days).
    4. Uses the LLM to synthesize this into a professional, emoji-enhanced summary.

**Example Response:**
```json
{
    "ok": true,
    "analysis": "💰 **High-Level Summary**: You have 1,500 QUBIC available...\n\n🚦 **Action Items**: You have 1 pending transaction...",
    "timestamp": "2024-12-06T..."
}
```

## 2. ✅ Dry Run Mode (Simulation)

You can now simulate any agent goal safely without risking funds.

### How to use
- **Method**: `POST`
- **Endpoint**: `/agent/run`
- **Body**:
```json
{
    "goal": "Buy 100 QUBIC using my USDT",
    "dry_run": true
}
```

**What happens:**
1. The AI **Plans** the task normally (creating steps like `Swap`, `Bridge`).
2. The Agent **Executes** the logic flows.
3. When it hits a "Side-Effect" step (Transaction, HTTP Request, Tool Call), it **SKIPS** execution.
4. Returns the full Task object so you can see exactly what *would* have happened.

**Verification:**
Check the logs in the response:
```json
"logs": [
    ...
    "⚠️ Dry Run: Skipped execution of QUBIC_TX"
]
```

## 🧪 Testing
I've updated your **Postman Collection** (v4.0) in the root directory:
`/Users/freya/Documents/work/hackit/qubic/qubic_autopilot_postman_collection.json`

Check the folder **"3. AI Advisor"** and **"4. Task Management"** for the new pre-configured requests.
