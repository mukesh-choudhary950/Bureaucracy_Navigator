from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.task import QueryRequest, QueryResponse, TaskRequest, TaskResponse
from app.agent.planner import TaskPlanner
from app.agent.executor import WorkflowExecutor
from app.agent.memory import MemorySystem
from app.agent.rag_system import RAGSystem
from app.models.user import Task, User
from typing import Dict, Any
import asyncio

router = APIRouter()

# Initialize components
planner = TaskPlanner()
executor = WorkflowExecutor()
memory_system = MemorySystem()
rag_system = RAGSystem()

@router.post("/query", response_model=QueryResponse)
async def handle_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle user query and generate plan"""
    try:
        # Get user context
        user_context = memory_system.get_context_for_request(request.user_id, request.message)
        
        # Generate plan
        plan = await planner.generate_plan(request.message, user_context)
        
        # Create task record
        task = Task(
            user_id=request.user_id,
            title=f"Request: {request.message[:50]}...",
            description=request.message,
            status="pending",
            plan=plan.dict()
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Store request in memory
        memory_system.store_request_memory(request.user_id, {
            "type": "user_query",
            "message": request.message,
            "task_id": task.id,
            "context": user_context
        })
        
        # Execute plan in background
        background_tasks.add_task(execute_plan_background, task.id, request.user_id)
        
        return QueryResponse(
            response=f"I understand you want to: {request.message}. I've created a plan with {len(plan.steps)} steps and started executing it. You can track the progress using task ID: {task.id}",
            task_id=task.id,
            plan=plan
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@router.post("/task", response_model=TaskResponse)
async def create_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new task"""
    try:
        # Generate plan for task
        plan = await planner.generate_plan(request.description)
        
        # Create task record
        task = Task(
            user_id=1,  # Default user for demo
            title=request.title,
            description=request.description,
            status="pending",
            plan=plan.dict()
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Execute plan in background
        background_tasks.add_task(execute_plan_background, task.id, task.user_id)
        
        return TaskResponse.from_orm(task)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task creation failed: {str(e)}")

@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get task details"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse.from_orm(task)

@router.get("/task/{task_id}/status")
async def get_task_status(task_id: int, db: Session = Depends(get_db)):
    """Get detailed task status"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get execution summary
    summary_result = await executor.get_execution_summary(task_id)
    
    return {
        "task_id": task_id,
        "status": task.status,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "plan": task.plan,
        "results": task.results,
        "summary": summary_result.get("summary") if summary_result.get("success") else None
    }

@router.post("/task/{task_id}/retry")
async def retry_task(task_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Retry failed steps in a task"""
    try:
        # Retry failed steps
        result = await executor.retry_failed_steps(task_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return {"message": "Task retry initiated", "result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task retry failed: {str(e)}")

@router.get("/user/{user_id}/tasks")
async def get_user_tasks(user_id: int, db: Session = Depends(get_db)):
    """Get all tasks for a user"""
    tasks = db.query(Task).filter(Task.user_id == user_id).order_by(Task.created_at.desc()).all()
    return [TaskResponse.from_orm(task) for task in tasks]

@router.post("/ask")
async def ask_question(request: Dict[str, Any]):
    """Ask a question using RAG system"""
    try:
        question = request.get("question", "")
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        # Get answer from RAG system
        answer_result = await rag_system.answer_question(question)
        
        return {
            "question": question,
            "answer": answer_result["answer"],
            "sources": answer_result["sources"],
            "confidence": answer_result["confidence"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question answering failed: {str(e)}")

@router.get("/tools")
async def get_available_tools():
    """Get list of available tools"""
    tools_info = await executor.get_available_tools_info()
    return {"tools": tools_info}

@router.post("/suggest-tools")
async def suggest_tools(request: Dict[str, Any]):
    """Suggest tools for a request"""
    try:
        user_request = request.get("request", "")
        if not user_request:
            raise HTTPException(status_code=400, detail="Request is required")
        
        suggestions = await executor.suggest_tools_for_request(user_request)
        
        return {
            "request": user_request,
            "suggested_tools": suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool suggestion failed: {str(e)}")

@router.get("/user/{user_id}/profile")
async def get_user_profile(user_id: int):
    """Get user profile from memory"""
    profile = memory_system.get_user_profile(user_id)
    return {"profile": profile}

@router.post("/user/{user_id}/profile")
async def update_user_profile(user_id: int, profile_data: Dict[str, Any]):
    """Update user profile"""
    try:
        success = memory_system.store_user_profile(user_id, profile_data)
        if success:
            return {"message": "Profile updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Profile update failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")

@router.get("/user/{user_id}/memory")
async def get_user_memory(user_id: int, memory_type: str = None):
    """Get user memory"""
    if memory_type == "documents":
        data = memory_system.get_user_documents(user_id)
    elif memory_type == "requests":
        data = memory_system.get_previous_requests(user_id)
    elif memory_type == "tasks":
        data = memory_system.get_completed_tasks(user_id)
    else:
        # Get all memory
        data = {
            "profile": memory_system.get_user_profile(user_id),
            "documents": memory_system.get_user_documents(user_id),
            "requests": memory_system.get_previous_requests(user_id),
            "tasks": memory_system.get_completed_tasks(user_id)
        }
    
    return {"memory_type": memory_type, "data": data}

async def execute_plan_background(task_id: int, user_id: int):
    """Execute plan in background"""
    try:
        # Get task from database
        from app.core.database import SessionLocal
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            return
        
        # Parse plan
        from app.schemas.task import GeneratedPlan
        plan = GeneratedPlan(**task.plan)
        
        # Execute plan
        await executor.execute_plan(plan, user_id, task_id)
        
    except Exception as e:
        print(f"Background execution failed: {e}")
    finally:
        db.close()
