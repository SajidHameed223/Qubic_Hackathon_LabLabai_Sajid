# app/services/actions.py

from typing import Any, Dict, List, Optional
import json
import httpx

from ..models.task import Task, Step
from . import qubic_client


# --- AI / Planning logic -----------------------------------------------------


def handle_ai_plan(task: Task, step: Step) -> Dict[str, Any]:
    """
    Use oracle data + target allocation to compute rebalance trades.

    Flow:
      1. Find previous QUBIC_ORACLE step and parse its result.
      2. Read portfolio_value + current_allocations from oracle data.
      3. Read target_allocation from this step's params.
      4. Compute buy/sell amounts for each asset.
      5. Inject trade_actions into the next QUBIC_TX step's params.
      6. Return a JSON-serializable summary of the rebalance plan.
    """
    goal = step.params.get("goal", task.goal)

    # 1) Locate previous QUBIC_ORACLE step
    oracle_step: Optional[Step] = None
    current_index: Optional[int] = None

    for i, s in enumerate(task.steps):
        if s.id == step.id:
            current_index = i
            break

    if current_index is not None:
        for j in range(current_index - 1, -1, -1):
            prev = task.steps[j]
            if str(prev.type) == "QUBIC_ORACLE":
                oracle_step = prev
                break

    if oracle_step is None or not oracle_step.result:
        return {
            "goal": goal,
            "note": "No oracle data found, skipping rebalance calculation.",
        }

    # 2) Parse oracle result
    try:
        oracle_data = json.loads(oracle_step.result)
    except Exception as e:
        return {
            "goal": goal,
            "note": f"Failed to parse oracle result: {e}",
        }
    
    portfolio_value = float(oracle_data.get("portfolio_value", 0.0))
    current_allocations = oracle_data.get("current_allocations", {})

    # 3) Target allocation from this step
    target_allocation = step.params.get("target_allocation", {})

    if not target_allocation or portfolio_value <= 0:
        return {
            "goal": goal,
            "note": "Missing target allocation or portfolio value; no rebalance performed.",
            "oracle_data": oracle_data,
        }

    # 4) Compute trade deltas per asset
    trade_actions: List[Dict[str, Any]] = []
    for asset, target_ratio in target_allocation.items():
        current_ratio = float(current_allocations.get(asset, 0.0))

        current_amount = current_ratio * portfolio_value
        target_amount = float(target_ratio) * portfolio_value
        delta = target_amount - current_amount  # positive = buy, negative = sell

        if abs(delta) < 1e-6:
            continue

        action = "buy" if delta > 0 else "sell"
        trade_actions.append(
            {
                "asset": asset,
                "action": action,
                "amount": abs(delta),
            }
        )

    # 5) Inject into next QUBIC_TX step
    tx_step: Optional[Step] = None
    if current_index is not None and current_index + 1 < len(task.steps):
        candidate = task.steps[current_index + 1]
        if str(candidate.type) == "QUBIC_TX":
            tx_step = candidate

    if tx_step:
        if tx_step.params is None:
            tx_step.params = {}
        tx_step.params["trade_actions"] = trade_actions

    # 6) Return summary
    return {
        "goal": goal,
        "portfolio_value": portfolio_value,
        "current_allocations": current_allocations,
        "target_allocation": target_allocation,
        "trade_actions": trade_actions,
        "oracle_data_raw": oracle_data,
    }


# --- Qubic Oracle / On-chain data --------------------------------------------

# --- Qubic Oracle / On-chain data --------------------------------------------

def handle_qubic_oracle(task: Task, step: Step) -> Dict[str, Any]:
    """
    Fetch real wallet data from Qubic RPC and derive a simple portfolio view.

    - If step.params has `identity` or `wallet_address`, use that.
    - Otherwise fall back to QUBIC_WALLET_IDENTITY from env.
    - Returns:
        {
          "ok": True/False,
          "wallet": <raw RPC result or error>,
          "portfolio_value": <float>,
          "current_allocations": { ... },
          "assets": [...],
          "error": <str> (if any)
        }
    """
    # 1) Read identity from step if provided
    identity_from_step = (
        step.params.get("identity")
        or step.params.get("wallet_address")
    )

    # ignore placeholders like "<your_wallet_address>"
    if isinstance(identity_from_step, str) and "<" in identity_from_step:
        identity_from_step = None

    # 2) Fetch from RPC (this is REAL data)
    wallet_info = qubic_client.get_wallet_balance(identity_from_step)

    # If the RPC call itself failed, propagate failure
    if wallet_info.get("ok") is False:
        return {
            "ok": False,
            "wallet": wallet_info,
            "portfolio_value": 0.0,
            "current_allocations": {},
            "assets": [],
            "error": wallet_info.get("error", "Failed to fetch wallet balance"),
        }

    # 3) Derive portfolio_value + allocations from wallet_info["data"] or ["balance"]
    balance_raw = wallet_info.get("balance") or wallet_info.get("data")

    portfolio_value: float = 0.0
    allocations: Dict[str, float] = {}

    # Case A: balance_raw is a single number (e.g., total QUBIC)
    if isinstance(balance_raw, (int, float, str)):
        try:
            portfolio_value = float(balance_raw)
            if portfolio_value > 0:
                allocations = {"QUBIC": 1.0}
        except Exception:
            # can't parse, leave as 0 with empty allocations
            pass

    # Case B: balance_raw is a dict (e.g., multiple assets/fields)
    elif isinstance(balance_raw, dict):
        numeric_map: Dict[str, float] = {}
        for key, val in balance_raw.items():
            try:
                numeric_map[key] = float(val)
            except Exception:
                continue

        total = sum(numeric_map.values())
        if total > 0:
            portfolio_value = total
            allocations = {k: v / total for k, v in numeric_map.items()}

    # 4) Build response object
    data: Dict[str, Any] = {
        "ok": True,
        "wallet": wallet_info,                # 🔥 real on-chain info
        "portfolio_value": portfolio_value,   # derived numeric total (if we could)
        "current_allocations": allocations,   # per-key weights (0–1)
        "assets": list(allocations.keys()) or step.params.get("assets", []),
    }

    return data

# --- Qubic TX / CLI or SDK ---------------------------------------------------
from sqlalchemy.orm import Session
from ..db import User
from . import wallet

# --- Qubic TX / CLI or SDK ---------------------------------------------------
def handle_qubic_tx(task: Task, step: Step, db: Session = None, user: User = None) -> Dict[str, Any]:
    """
    Qubic TX execution.

    Modes:

      1) Simple transfer (REAL TX):
            params = { "destination" or "recipient" or "wallet_id", "amount": <int> }
         -> sends QU from the agent wallet using QubiPy.
         -> CHECKS VIRTUAL WALLET BALANCE FIRST if db/user provided.

      2) Rebalance trades (SIMULATION):
            params = { "trade_actions": [ {asset, action, amount}, ... ] }

      3) Meta TX steps (NO-OP):
            params = { "transaction_id": "..." }
         -> just log info, no on-chain action (sign/broadcast conceptual only).
    """

    # ----- Mode 1: simple transfer (REAL TX) -----
    # Accept "destination", "recipient", or "wallet_id" (planner used wallet_id)
    destination = (
        step.params.get("destination")
        or step.params.get("recipient")
        or step.params.get("wallet_id")
    )
    amount = step.params.get("amount")

    if destination is not None and amount is not None:
        try:
            amount_int = int(amount)
        except (TypeError, ValueError):
            return {
                "ok": False,
                "mode": "TRANSFER",
                "error": f"Invalid 'amount' for QUBIC_TX: {amount}",
            }
        
        # --- VIRTUAL WALLET INTEGRATION ---
        reserved = False
        wallet_acct = None
        
        if db and user:
            # 1. Get Wallet
            wallet_acct = wallet.get_or_create_wallet(db, user)
            
            # 2. Check & Reserve
            if not wallet.reserve_balance(db, wallet_acct.id, amount_int, "QUBIC"):
                return {
                    "ok": False,
                    "mode": "TRANSFER",
                    "error": f"Insufficient virtual balance. Need {amount_int} QUBIC.",
                }
            reserved = True
            print(f"💰 Funds reserved for task: {amount_int} QUBIC")

        # 3. Execute On-Chain
        send_result = qubic_client.send_qu_to_identity(destination, amount_int)
        
        # 4. Finalize Wallet State
        if reserved and wallet_acct:
            if send_result.get("ok"):
                # Success: Burn reservation (finalize withdrawal)
                wallet.release_reserved(db, wallet_acct.id, amount_int, "QUBIC", to_balance=False)
                # Create Ledger Entry
                from uuid import uuid4
                from datetime import datetime
                from ..db import WalletLedger
                
                ledger = WalletLedger(
                    id=str(uuid4()),
                    wallet_account_id=wallet_acct.id,
                    kind="AGENT_EXECUTION",
                    amount=-amount_int,
                    asset="QUBIC",
                    tx_id=send_result.get("tx_id"),
                    description=f"Agent Task: {task.goal[:50]}...",
                    created_at=datetime.utcnow()
                )
                db.add(ledger)
                db.commit()
            else:
                # Failure: Refund reservation
                print(f"❌ Transaction failed, refunding user: {send_result.get('error')}")
                wallet.release_reserved(db, wallet_acct.id, amount_int, "QUBIC", to_balance=True)

        return {
            "mode": "TRANSFER",
            "destination": destination,
            "amount": amount_int,
            **send_result,
        }

    # ----- Mode 3: meta steps like "sign" / "broadcast" with transaction_id -----
    if "transaction_id" in step.params:
        # We already sign+broadcast in the main TRANSFER step,
        # so these become bookkeeping/logging only.
        return {
            "mode": "TX_META_NOOP",
            "note": "Signing/broadcasting handled in main TRANSFER step.",
            "params": step.params,
        }

    # ----- Mode 2: rebalance trades (SIMULATION) -----
    trade_actions = step.params.get("trade_actions", [])
    if trade_actions:
        summaries = []
        for action in trade_actions:
            asset = action.get("asset")
            side = action.get("action")
            amt = float(action.get("amount", 0.0))
            summaries.append(f"{side} {amt:.4f} of {asset}")

        return {
            "mode": "REBALANCE_SIMULATED",
            "simulated": True,
            "executed_trades": trade_actions,
            "summary": summaries,
        }
    
    # ----- Mode 3: meta steps like "sign" / "broadcast" with transaction_id or signed tx -----
    if "transaction_id" in step.params or "signed_transaction" in step.params:
        # We already sign+broadcast in the main TRANSFER step,
        # so these become bookkeeping/logging only.
        return {
            "mode": "TX_META_NOOP",
            "note": "Signing/broadcasting handled in main TRANSFER step.",
            "params": step.params,
        }


    # ----- Fallback if no recognizable params -----
    return {
        "ok": False,
        "error": "QUBIC_TX step has neither (destination/recipient/wallet_id + amount), transaction_id, nor trade_actions.",
        "params": step.params,
    }

# --- HTTP triggers (Make / n8n / webhooks) -----------------------------------




# --- HTTP triggers (Make / n8n / webhooks) -----------------------------------

def handle_http_request(task: Task, step: Step) -> Dict[str, Any]:
    """
    Call external HTTP endpoints (Make, n8n, webhooks, etc.)

    Returns a dict with:
      {
        "ok": True/False,
        "url": str | None,
        "method": str,
        "status_code": int | None,
        "payload": dict,
        "response_snippet": str | None,
        "error": str | None,
        "skipped": bool (optional)
      }
    """
    url = step.params.get("url")
    method = step.params.get("method", "POST").upper()
    payload = step.params.get("payload", {"goal": task.goal, "task_id": task.id})

    # If no URL is given, treat as a non-fatal "skipped" step
    if not url:
        return {
            "ok": True,            # 👈 no failure, just skip
            "skipped": True,
            "note": "HTTP_REQUEST skipped: no 'url' provided in step.params",
            "url": None,
            "method": method,
            "status_code": None,
            "payload": payload,
            "response_snippet": None,
            "error": None,
        }

    try:
        with httpx.Client(timeout=10.0) as client:
            if method == "GET":
                resp = client.get(url, params=payload)
            else:
                resp = client.post(url, json=payload)

        # Consider 2xx/3xx as ok, 4xx/5xx as failure
        ok = 200 <= resp.status_code < 400

        return {
            "ok": ok,
            "url": url,
            "method": method,
            "status_code": resp.status_code,
            "payload": payload,
            "response_snippet": (resp.text[:500] if resp.text else None),
            "error": None if ok else f"Non-success status code: {resp.status_code}",
        }

    except Exception as e:
        return {
            "ok": False,
            "url": url,
            "method": method,
            "status_code": None,
            "payload": payload,
            "response_snippet": None,
            "error": f"HTTP request failed: {e}",
        }


# --- LOG ONLY -----------------------------------------------------------------


def handle_log_only(task: Task, step: Step) -> Dict[str, Any]:
    return {
        "note": f"Log-only step executed for goal: {task.goal}",
        "params": step.params,
    }


# --- CUSTOM -------------------------------------------------------------------


def handle_custom(task: Task, step: Step) -> Dict[str, Any]:
    return {
        "note": "Custom handler executed",
        "step_description": step.description,
        "params": step.params,
    }