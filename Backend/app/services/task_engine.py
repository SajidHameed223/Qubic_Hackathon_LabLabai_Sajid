from datetime import datetime
from typing import List
import json  # 👈 add this

from ..models.task import Task, Step, TaskStatus, StepStatus, StepType
from . import actions
from . import ai_planner


def plan_steps_for_goal(goal: str, user_risk_profile: str = "moderate") -> List[Step]:
    from . import multi_agent_planner
    from . import ai_planner
    
    # Run the multi-agent council
    plan_dicts = multi_agent_planner.run_multi_agent_plan(goal, user_risk_profile)
    
    # Convert to Step objects
    steps = ai_planner.build_steps_from_plan(plan_dicts)
    return steps


def append_log(task: Task, message: str) -> None:
    timestamp = datetime.utcnow().isoformat()
    entry = f"[{timestamp}] {message}"
    task.logs.append(entry)


# def execute_step(task: Task, step: Step) -> Step:
#     step.started_at = datetime.utcnow()
#     step.status = StepStatus.RUNNING
#     append_log(task, f"Started step ({step.type}): {step.description}")

#     try:
#         # Call the right handler
#         if step.type == StepType.AI_PLAN:
#             result = actions.handle_ai_plan(task, step)

#         elif step.type == StepType.QUBIC_ORACLE:
#             result = actions.handle_qubic_oracle(task, step)

#         elif step.type == StepType.QUBIC_TX:
#             result = actions.handle_qubic_tx(task, step)

#         elif step.type == StepType.HTTP_REQUEST:
#             result = actions.handle_http_request(task, step)

#         elif step.type == StepType.LOG_ONLY:
#             result = actions.handle_log_only(task, step)

#         else:
#             result = actions.handle_custom(task, step)

#         # Normalize: dict/list → JSON, else → string
#         if isinstance(result, (dict, list)):
#             step.result = json.dumps(result)
#         else:
#             step.result = str(result)

#         step.status = StepStatus.COMPLETED
#         append_log(task, f"Completed step: {step.description}")

#     except Exception as e:
#         step.status = StepStatus.FAILED
#         step.error = str(e)
#         append_log(task, f"Failed step: {step.description} | error={e}")

#     step.finished_at = datetime.utcnow()
#     return step



def execute_step(task: Task, step: Step, db=None, user=None) -> Step:
    step.started_at = datetime.utcnow()
    step.status = StepStatus.RUNNING
    append_log(task, f"Started step ({step.type}): {step.description}")

    # --- DRY RUN CHECK ---
    # If task is dry_run, we skip side-effect steps
    SIDE_EFFECT_STEPS = {StepType.QUBIC_TX, StepType.HTTP_REQUEST, StepType.TOOL_EXECUTION}
    
    # Check if this step should be skipped
    if getattr(task, "dry_run", False) and step.type in SIDE_EFFECT_STEPS:
        step.result = json.dumps({"ok": True, "dry_run": True, "message": "Step execution skipped (Dry Run)"})
        step.status = StepStatus.COMPLETED
        step.finished_at = datetime.utcnow()
        append_log(task, f"⚠️ Dry Run: Skipped execution of {step.type}")
        return step

    try:
        raw_result: Any = None

        # --- dispatch by step type ---
        if step.type == StepType.AI_PLAN:
            raw_result = actions.handle_ai_plan(task, step)

        elif step.type == StepType.QUBIC_ORACLE:
            raw_result = actions.handle_qubic_oracle(task, step)

        elif step.type == StepType.QUBIC_TX:
            raw_result = actions.handle_qubic_tx(task, step, db=db, user=user)

        elif step.type == StepType.HTTP_REQUEST:
            raw_result = actions.handle_http_request(task, step)

        elif step.type == StepType.LOG_ONLY:
            raw_result = actions.handle_log_only(task, step)
        
        elif step.type == StepType.TOOL_EXECUTION:
            # --- SMART VAULT CHECK ---
            if db and user:
                from .smart_vault import check_vault_safety
                # Extract params from step.params (which might be nested)
                # Usually step.params has "tool_params"
                tool_params = step.params.get("tool_params", {})
                if not check_vault_safety(db, user, tool_params):
                     raise RuntimeError("Smart Vault rejected transaction: Violation of safety rules")
            
            # --- INTERCEPT TRANSFER TOOLS ---
            # If planner uses a tool for transfer, redirect to QUBIC_TX to ensure wallet logic is used
            tool_name = step.params.get("tool_name", "").lower()
            if tool_name in ["transfer", "send_qu", "send_qubic", "send_tokens", "pay"]:
                t_params = step.params.get("tool_params", {})
                # Map params
                step.params["destination"] = t_params.get("destination") or t_params.get("to") or t_params.get("recipient")
                step.params["amount"] = t_params.get("amount")
                raw_result = actions.handle_qubic_tx(task, step, db=db, user=user)
            else:
                from . import tool_handler
                raw_result = tool_handler.handle_tool_execution(task, step)

        else:
            raw_result = actions.handle_custom(task, step)

        # --- interpret result + detect logical failure ---

        # If handler returns a dict, we can inspect it and then JSON-encode it
        if isinstance(raw_result, dict):
            # For some step types, treat ok: False as a hard failure
            if step.type in {StepType.QUBIC_TX, StepType.QUBIC_ORACLE, StepType.HTTP_REQUEST}:
                if raw_result.get("ok") is False:
                    # Raise so we land in the except block and mark the step as FAILED
                    raise RuntimeError(raw_result.get("error", f"{step.type} returned ok=false"))

            step.result = json.dumps(raw_result)

        else:
            # Fallback: just string-ify whatever came back
            if raw_result is not None:
                step.result = str(raw_result)
            else:
                step.result = None

        step.status = StepStatus.COMPLETED
        append_log(task, f"Completed step: {step.description}")

    except Exception as e:
        step.status = StepStatus.FAILED
        step.error = str(e)
        append_log(task, f"Failed step: {step.description} | error={e}")

    step.finished_at = datetime.utcnow()
    return step




def run_task(task: Task, db=None, user=None) -> Task:
    """
    Execute all steps in a task sequentially.
    Stops on first failure.
    """
    append_log(task, f"Starting execution for goal: {task.goal}")
    task.status = TaskStatus.RUNNING
    task.updated_at = datetime.utcnow()

    for i, step in enumerate(task.steps):
        step = execute_step(task, step, db=db, user=user)
        task.steps[i] = step
        task.updated_at = datetime.utcnow()
        if step.status == StepStatus.FAILED:
            task.status = TaskStatus.FAILED
            append_log(task, "Stopping task due to step failure.")
            return task

    task.status = TaskStatus.COMPLETED
    append_log(task, "Task completed successfully.")
    task.updated_at = datetime.utcnow()
    return task