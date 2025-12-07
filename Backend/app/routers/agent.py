# app/routers/agent.py

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db, TaskRecord, User
from ..models.task import (
    Task,
    TaskStatus,
    TaskResponse,
    CreateTaskRequest,
)
from ..services.task_engine import plan_steps_for_goal, run_task
from ..core.deps import get_current_user

router = APIRouter(prefix="/agent", tags=["agent"])


def save_task(db: Session, task: Task, user_id: str = None) -> None:
    """
    Persist a Task into the tasks table as JSON.

    Uses Pydantic v2 .model_dump(mode="json") so datetimes/enums
    are converted to JSON-friendly values.
    """
    data = task.model_dump(mode="json")

    record = db.query(TaskRecord).filter(TaskRecord.id == task.id).first()
    if record:
        record.data = data
        if user_id:
            record.user_id = user_id
    else:
        record = TaskRecord(id=task.id, user_id=user_id, data=data)
        db.add(record)

    db.commit()


# ---------------------------------------------------------------------------
# 1) One-shot agent: clean goal-based endpoint
#    POST /agent/run
# ---------------------------------------------------------------------------

@router.post("/run", response_model=TaskResponse)
def run_goal(
    req: CreateTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    One-shot agent endpoint with SMART APPROVAL SYSTEM.

    Flow:
      1) Parse task goal to extract transaction details (amount, action)
      2) Check if approval is required based on user settings
      3a) If approval needed: Create approval request, return PENDING
      3b) If auto-approved: Execute immediately
      4) Store final state and return
    
    Request body:
      { "goal": "<your natural language goal>" }
    """
    from ..services import approval as approval_service
    from ..services import transaction_parser
    from decimal import Decimal
    
    task_id = str(uuid4())
    now = datetime.utcnow()
    
    # Parse transaction details from goal
    tx_details = transaction_parser.extract_transaction_details(req.goal)
    
    # If amount can be determined, check approval requirements - BUT SKIP IF DRY RUN
    if tx_details["amount"] is not None and not req.dry_run:
        amount = tx_details["amount"]
        action = tx_details["action"]
        
        # Check if approval is needed
        if approval_service.should_require_approval(current_user, action, amount):
            # Create approval request
            approval_request = approval_service.create_approval_request(
                db=db,
                user=current_user,
                action=action,
                amount=amount,
                asset=tx_details.get("asset", "QUBIC"),
                destination=tx_details.get("destination"),
                description=transaction_parser.format_transaction_description(tx_details),
                risk_level=transaction_parser.estimate_risk_level(action, amount),
                task_id=task_id,
                meta={"goal": req.goal, "tx_details": tx_details}
            )
            
            # Return pending approval status
            return {
                "id": task_id,
                "goal": req.goal,
                "status": "PENDING_APPROVAL",
                "approval_id": approval_request.id,
                "message": f"⏸️ Approval required for {action} of {amount} {tx_details.get('asset', 'QUBIC')}",
                "amount": float(amount),
                "action": action,
                "expires_at": approval_request.expires_at,
                "instructions": f"Approve this transaction at /approvals/approve/{approval_request.id}",
                "created_at": now,
                "updated_at": now,
                "steps": [],
                "logs": [f"[{now.isoformat()}] Approval required: {action} {amount}"]
            }
        else:
            # Auto-approve
            approval_id = approval_service.auto_approve_transaction(
                db=db,
                user=current_user,
                action=action,
                amount=amount,
                description=f"Auto-approved: {req.goal}",
                task_id=task_id
            )
            
            # Add approval info to logs
            approval_log = f"✅ Auto-approved: {action} {amount} QUBIC (below threshold)"
    else:
        # No amount detected OR Dry Run, proceed without approval
        if req.dry_run:
            approval_log = "ℹ️ Dry Run Mode: Approvals skipped."
        else:
            approval_log = "ℹ️ No transaction amount detected, proceeding without approval"
        approval_id = None
    
    # Plan and create task
    risk_profile = "moderate"
    if current_user.preferences:
        risk_profile = current_user.preferences.get("risk_tolerance", "moderate")
        
    steps = plan_steps_for_goal(req.goal, user_risk_profile=risk_profile)

    task = Task(
        id=task_id,
        goal=req.goal,
        steps=steps,
        created_at=now,
        updated_at=now,
        status=TaskStatus.PENDING,
        logs=[
            f"[{now.isoformat()}] Task created with goal: {req.goal}",
            f"[{now.isoformat()}] {approval_log}" if "approval_log" in locals() else f"[{now.isoformat()}] Dry Run started"
        ],
        dry_run=req.dry_run
    )

    # Save initial state
    save_task(db, task, user_id=current_user.id)

    # Execute
    task = run_task(task, db=db, user=current_user)

    # Save final state
    save_task(db, task, user_id=current_user.id)

    return task


# ---------------------------------------------------------------------------
# 2) Generic trigger endpoint (EasyConnect / Make / n8n / webhooks)
#    POST /agent/trigger
# ---------------------------------------------------------------------------

@router.post("/trigger", response_model=TaskResponse)
def trigger_agent(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generic trigger for AutoPilot Worker.

    Example payload from EasyConnect / Make:
    {
      "source": "easyconnect",
      "event_type": "LargeDeposit",
      "goal": "Handle LargeDeposit for contract XYZ"
    }

    If 'goal' is missing, it will be synthesized from 'source'.
    """
    goal = payload.get("goal") or f"Triggered task from {payload.get('source', 'unknown')}"

    task_id = str(uuid4())
    now = datetime.utcnow()
    steps = plan_steps_for_goal(goal)

    task = Task(
        id=task_id,
        goal=goal,
        steps=steps,
        created_at=now,
        updated_at=now,
        status=TaskStatus.PENDING,
        logs=[f"[{now.isoformat()}] Task created from trigger with goal: {goal}"],
    )

    # Persist initial state
    save_task(db, task, user_id=current_user.id)

    # Auto-run immediately
    task = run_task(task, db=db, user=current_user)

    # Persist final state
    save_task(db, task, user_id=current_user.id)

    return task


# ---------------------------------------------------------------------------
# 3) Execute Approved Task
#    POST /agent/execute-approved/{approval_id}
# ---------------------------------------------------------------------------

@router.post("/execute-approved/{approval_id}")
def execute_approved_task(
    approval_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute a task that has been approved.
    
    This is called after user approves a transaction via /approvals/approve/{id}
    """
    from ..services import approval as approval_service
    from ..db import ApprovalRequest
    
    # Get approval request
    approval = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == approval_id,
        ApprovalRequest.user_id == current_user.id
    ).first()
    
    if not approval:
        raise HTTPException(404, "Approval not found")
    
    if approval.status != "approved":
        raise HTTPException(400, f"Approval status is {approval.status}, must be 'approved'")
    
    # Get task goal from approval metadata
    goal = approval.meta.get("goal") if approval.meta else None
    if not goal:
        raise HTTPException(400, "No goal found in approval metadata")
    
    # Create and execute task
    task_id = approval.task_id or str(uuid4())
    now = datetime.utcnow()
    
    steps = plan_steps_for_goal(goal)
    
    task = Task(
        id=task_id,
        goal=goal,
        steps=steps,
        created_at=now,
        updated_at=now,
        status=TaskStatus.PENDING,
        logs=[
            f"[{now.isoformat()}] Task created from approved request: {approval_id}",
            f"[{now.isoformat()}] ✅ User approved: {approval.description}"
        ],
    )
    
    # Save and execute
    save_task(db, task, user_id=current_user.id)
    task = run_task(task, db=db, user=current_user)
    save_task(db, task, user_id=current_user.id)
    
    return task