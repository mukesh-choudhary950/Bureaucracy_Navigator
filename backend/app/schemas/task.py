from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class TaskRequest(BaseModel):
    title: str
    description: str

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    plan: Optional[List[Dict[str, Any]]] = None
    results: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class PlanStep(BaseModel):
    id: str
    description: str
    tool: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    status: str = "pending"
    result: Optional[Any] = None

class GeneratedPlan(BaseModel):
    steps: List[PlanStep]
    reasoning: str

class QueryRequest(BaseModel):
    message: str
    user_id: Optional[int] = 1  # Default user for demo

class QueryResponse(BaseModel):
    response: str
    task_id: Optional[int] = None
    plan: Optional[GeneratedPlan] = None
