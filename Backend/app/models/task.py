from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# --- Pydantic Models ---

# what kind of action it is (AI/Qubic/HTTP/etc.)
class StepType(str, Enum):
    AI_PLAN = "AI_PLAN"             # LangGraph / Ollama reasoning
    QUBIC_ORACLE = "QUBIC_ORACLE"   # Fetch on-chain / oracle data
    QUBIC_TX = "QUBIC_TX"           # Send tx via Qubic CLI / SDK
    HTTP_REQUEST = "HTTP_REQUEST"   # Call Make/n8n, webhooks, APIs
    LOG_ONLY = "LOG_ONLY"           # Internal bookkeeping / log
    TOOL_EXECUTION = "TOOL_EXECUTION"  # Execute a registered tool
    CUSTOM = "CUSTOM"               # For future extension


class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class Step(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    description: str
    type: StepType = StepType.LOG_ONLY
    params: Dict[str, Any] = Field(default_factory=dict)

    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    steps: List[Step] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    logs: List[str] = Field(default_factory=list)
    dry_run: bool = False


class CreateTaskRequest(BaseModel):
    goal: str
    dry_run: Optional[bool] = False


class TaskResponse(Task):
    approval_id: Optional[str] = None
    message: Optional[str] = None
    instructions: Optional[str] = None
    amount: Optional[float] = None
    action: Optional[str] = None
    expires_at: Optional[datetime] = None
    pass


# --- SQLAlchemy Models ---
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class TaskRecord(Base):
    """Task record for storing task execution data"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: Each task belongs to one user
    user = relationship("User", back_populates="tasks")
