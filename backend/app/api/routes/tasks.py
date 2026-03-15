from fastapi import APIRouter, HTTPException, status
from app.models.task import TaskCreate, TaskResponse, TaskUpdate, TaskStatus
from app.services.task_service import task_service
from app.services.user_service import user_service
from typing import List
from pydantic import BaseModel

router = APIRouter()

class AutoAssignRequest(BaseModel):
    task_id: int

class AssignTaskRequest(BaseModel):
    task_id: int
    assigned_to: str
    reason: str = ""

@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, username: str):
    """Create a new task"""
    try:
        task = task_service.create_task(task_data, username)
        if not task:
            raise HTTPException(
                status_code=400, 
                detail="Failed to create task"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

@router.get("/user/{username}", response_model=List[TaskResponse])
async def get_user_tasks(username: str):
    """Get all tasks for a user"""
    try:
        tasks = task_service.get_tasks_by_user(username)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    """Get task by ID"""
    try:
        task = task_service.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=404, 
                detail="Task not found"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")

@router.put("/{task_id}/status")
async def update_task_status(task_id: int, status: TaskStatus):
    """Update task status"""
    try:
        success = task_service.update_task_status(task_id, status)
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Failed to update task status"
            )
        return {"message": "Task status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")

@router.post("/auto-assign")
async def auto_assign_task(request: AutoAssignRequest):
    """Auto-assign task to best available user based on workload"""
    try:
        # Get the task
        task = task_service.get_task_by_id(request.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get all users
        users = user_service.get_all_users()
        if not users:
            raise HTTPException(status_code=400, detail="No users available for assignment")
        
        # Find best assignee based on workload and task type
        best_assignee = None
        min_workload = float('inf')
        
        for user in users:
            # Skip the task creator
            if user.username == task.assigned_by:
                continue
                
            # Get user's current task count
            user_tasks = task_service.get_tasks_by_user(user.username)
            workload = len([t for t in user_tasks if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]])
            
            # Simple workload balancing - assign to user with least tasks
            if workload < min_workload:
                min_workload = workload
                best_assignee = user
        
        if not best_assignee:
            # Fallback to first available user
            best_assignee = next((u for u in users if u.username != task.assigned_by), None)
        
        if not best_assignee:
            raise HTTPException(status_code=400, detail="Could not find suitable assignee")
        
        # Assign the task
        success = task_service.assign_task(request.task_id, best_assignee.username)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to assign task")
        
        return {
            "message": f"Task auto-assigned to {best_assignee.username}",
            "assigned_to": best_assignee.username,
            "workload": min_workload,
            "reason": "Selected based on lowest current workload"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-assignment failed: {str(e)}")

@router.post("/assign")
async def assign_task(request: AssignTaskRequest):
    """Manually assign task to a specific user"""
    try:
        # Verify task exists
        task = task_service.get_task_by_id(request.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Verify user exists
        user = user_service.get_user_by_username(request.assigned_to)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Assign the task
        success = task_service.assign_task(request.task_id, request.assigned_to)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to assign task")
        
        return {
            "message": f"Task assigned to {request.assigned_to}",
            "task_id": request.task_id,
            "assigned_to": request.assigned_to,
            "reason": request.reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task assignment failed: {str(e)}")

@router.get("/unassigned/all", response_model=List[TaskResponse])
async def get_unassigned_tasks():
    """Get all unassigned tasks"""
    try:
        tasks = task_service.get_unassigned_tasks()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unassigned tasks: {str(e)}")

@router.get("/stats/{username}")
async def get_task_stats(username: str):
    """Get task statistics for a user"""
    try:
        tasks = task_service.get_tasks_by_user(username)
        
        stats = {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.status == TaskStatus.PENDING]),
            "in_progress": len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
            "completed": len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            "cancelled": len([t for t in tasks if t.status == TaskStatus.CANCELLED])
        }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task stats: {str(e)}")
