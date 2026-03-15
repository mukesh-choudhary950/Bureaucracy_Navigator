from fastapi import APIRouter, HTTPException, status
from app.models.workflow import WorkflowCreate, WorkflowResponse, WorkflowStatus
from app.services.workflow_service import workflow_service
from typing import List

router = APIRouter()

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(workflow_data: WorkflowCreate, username: str):
    """Create a new workflow"""
    try:
        workflow = workflow_service.create_workflow(workflow_data, username)
        if not workflow:
            raise HTTPException(
                status_code=400, 
                detail="Failed to create workflow"
            )
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")

@router.get("/user/{username}", response_model=List[WorkflowResponse])
async def get_user_workflows(username: str):
    """Get all workflows for a user"""
    try:
        workflows = workflow_service.get_workflows_by_user(username)
        return workflows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflows: {str(e)}")

@router.get("/{workflow_id}/steps")
async def get_workflow_steps(workflow_id: int):
    """Get workflow steps"""
    try:
        steps = workflow_service.get_workflow_steps(workflow_id)
        return steps
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow steps: {str(e)}")

@router.put("/{workflow_id}/status")
async def update_workflow_status(workflow_id: int, status: WorkflowStatus):
    """Update workflow status"""
    try:
        success = workflow_service.update_workflow_status(workflow_id, status)
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Failed to update workflow status"
            )
        return {"message": "Workflow status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update workflow: {str(e)}")

@router.put("/steps/{step_id}/status")
async def update_step_status(step_id: int, status: WorkflowStatus):
    """Update workflow step status"""
    try:
        success = workflow_service.update_step_status(step_id, status)
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Failed to update step status"
            )
        return {"message": "Step status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update step: {str(e)}")

@router.get("/stats/{username}")
async def get_workflow_stats(username: str):
    """Get workflow statistics for a user"""
    try:
        workflows = workflow_service.get_workflows_by_user(username)
        
        stats = {
            "total": len(workflows),
            "not_started": len([w for w in workflows if w.status == WorkflowStatus.NOT_STARTED]),
            "in_progress": len([w for w in workflows if w.status == WorkflowStatus.IN_PROGRESS]),
            "completed": len([w for w in workflows if w.status == WorkflowStatus.COMPLETED]),
            "on_hold": len([w for w in workflows if w.status == WorkflowStatus.ON_HOLD])
        }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow stats: {str(e)}")
