from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class WorkflowStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class WorkflowStep(BaseModel):
    id: Optional[int] = None
    workflow_id: int
    title: str
    description: str
    status: WorkflowStatus = WorkflowStatus.NOT_STARTED
    assigned_to: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

class Workflow(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    created_by: str
    status: WorkflowStatus = WorkflowStatus.NOT_STARTED
    priority: str = "medium"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class WorkflowCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class WorkflowResponse(BaseModel):
    id: int
    title: str
    description: str
    created_by: str
    status: WorkflowStatus
    priority: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class WorkflowStepResponse(BaseModel):
    id: int
    workflow_id: int
    title: str
    description: str
    status: WorkflowStatus
    assigned_to: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
