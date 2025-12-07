# app/routers/tasks.py

from uuid import uuid4
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services import task_engine 

from ..db import get_db, TaskRecord, User
from ..models.task import CreateTaskRequest, Task, TaskResponse, TaskStatus
from ..services.task_engine import plan_steps_for_goal, run_task
from ..core.deps import get_current_user


router = APIRouter(prefix="/tasks", tags=["tasks"])


def load_task_or_404(db: Session, task_id: str, user_id: str = None) -> Task:
    """Load a task by ID, optionally filtering by user"""
    query = db.query(TaskRecord).filter(TaskRecord.id == task_id)
    
    # If user_id provided, only return tasks owned by that user
    if user_id:
        query = query.filter(TaskRecord.user_id == user_id)
    
    record = query.first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")

    # Safely reconstruct Pydantic model from JSON data
    return Task.model_validate(record.data)


def save_task(db: Session, task: Task, user_id: str = None) -> None:
    # ✅ Use JSON-safe dump so datetimes + Enums become strings
    data = task.model_dump(mode="json")

    record = (
        db.query(TaskRecord)
        .filter(TaskRecord.id == task.id)
        .first()
    )

    if record:
        record.data = data
        if user_id:
            record.user_id = user_id
    else:
        record = TaskRecord(id=task.id, user_id=user_id, data=data)
        db.add(record)

    db.commit()


@router.get("", response_model=List[TaskResponse])
def list_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Get all tasks for the current user.
    
    - **limit**: Maximum number of tasks to return (default: 50)
    - **offset**: Number of tasks to skip (for pagination)
    """
    records = (
        db.query(TaskRecord)
        .filter(TaskRecord.user_id == current_user.id)
        .order_by(TaskRecord.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    
    tasks = [Task.model_validate(record.data) for record in records]
    return tasks


@router.post("", response_model=TaskResponse)
def create_task(
    req: CreateTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Optional: log incoming request body
    print("Incoming request:", req.model_dump())

    task_id = str(uuid4())
    now = datetime.utcnow()
    steps = plan_steps_for_goal(req.goal)

    task = Task(
        id=task_id,
        goal=req.goal,
        steps=steps,
        created_at=now,
        updated_at=now,
        status=TaskStatus.PENDING,
        logs=[f"[{now.isoformat()}] Task created with goal: {req.goal}"],
    )

    save_task(db, task, user_id=current_user.id)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task by ID (only if it belongs to current user)"""
    return load_task_or_404(db, task_id, user_id=current_user.id)


@router.post("/{task_id}/run", response_model=TaskResponse)
def run_existing_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run an existing task (only if it belongs to current user)"""
    task = load_task_or_404(db, task_id, user_id=current_user.id)

    if task.status in [TaskStatus.RUNNING, TaskStatus.COMPLETED]:
        raise HTTPException(status_code=400, detail=f"Task already {task.status}")

    task = run_task(task)
    save_task(db, task, user_id=current_user.id)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task (only if it belongs to current user)"""
    record = (
        db.query(TaskRecord)
        .filter(TaskRecord.id == task_id)
        .filter(TaskRecord.user_id == current_user.id)
        .first()
    )
    
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(record)
    db.commit()
    
    return {"message": "Task deleted successfully", "task_id": task_id}