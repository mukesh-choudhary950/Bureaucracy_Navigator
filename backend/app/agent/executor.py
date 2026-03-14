from typing import List, Dict, Any, Optional
from app.schemas.task import PlanStep, GeneratedPlan
from app.tools import get_tool, list_available_tools
from app.agent.rag_system import RAGSystem
from app.agent.memory import MemorySystem
from app.models.user import Task, User
from app.core.database import get_db, SessionLocal
from datetime import datetime
import asyncio
import json
import uuid

class WorkflowExecutor:
    """Executes generated plans step by step"""
    
    def __init__(self):
        self.rag_system = RAGSystem()
        self.memory_system = MemorySystem()
        self.db = SessionLocal()
    
    async def execute_plan(self, plan: GeneratedPlan, user_id: int, task_id: Optional[int] = None) -> Dict[str, Any]:
        """Execute a generated plan step by step"""
        
        execution_results = {
            "task_id": task_id,
            "user_id": user_id,
            "plan_id": str(uuid.uuid4()),
            "started_at": datetime.now().isoformat(),
            "status": "in_progress",
            "completed_steps": [],
            "failed_steps": [],
            "current_step": None,
            "final_result": None,
            "execution_log": []
        }
        
        try:
            # Create or update task record
            if task_id:
                task = self.db.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = "in_progress"
                    task.plan = plan.dict()
                    self.db.commit()
            
            # Execute each step
            for i, step in enumerate(plan.steps):
                execution_results["current_step"] = {
                    "step_id": step.id,
                    "step_number": i + 1,
                    "description": step.description
                }
                
                try:
                    # Execute step
                    step_result = await self._execute_step(step, user_id)
                    
                    # Update step status
                    step.status = "completed" if step_result["success"] else "failed"
                    step.result = step_result
                    
                    # Record result
                    if step_result["success"]:
                        execution_results["completed_steps"].append({
                            "step_id": step.id,
                            "result": step_result,
                            "completed_at": datetime.now().isoformat()
                        })
                    else:
                        execution_results["failed_steps"].append({
                            "step_id": step.id,
                            "error": step_result.get("error", "Unknown error"),
                            "failed_at": datetime.now().isoformat()
                        })
                    
                    execution_results["execution_log"].append({
                        "timestamp": datetime.now().isoformat(),
                        "step_id": step.id,
                        "status": step.status,
                        "result": step_result
                    })
                    
                    # Update task in database
                    if task_id:
                        task = self.db.query(Task).filter(Task.id == task_id).first()
                        if task:
                            task.plan = plan.dict()
                            self.db.commit()
                    
                except Exception as e:
                    # Handle step execution error
                    step.status = "failed"
                    step.result = {"success": False, "error": str(e)}
                    
                    execution_results["failed_steps"].append({
                        "step_id": step.id,
                        "error": str(e),
                        "failed_at": datetime.now().isoformat()
                    })
                    
                    execution_results["execution_log"].append({
                        "timestamp": datetime.now().isoformat(),
                        "step_id": step.id,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Determine final status
            if len(execution_results["failed_steps"]) == 0:
                execution_results["status"] = "completed"
                execution_results["final_result"] = "Plan executed successfully"
            elif len(execution_results["failed_steps"]) < len(plan.steps):
                execution_results["status"] = "partially_completed"
                execution_results["final_result"] = "Plan partially completed with some failures"
            else:
                execution_results["status"] = "failed"
                execution_results["final_result"] = "Plan execution failed"
            
            # Update task final status
            if task_id:
                task = self.db.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = execution_results["status"]
                    task.results = execution_results
                    self.db.commit()
            
            # Store execution in memory
            self.memory_system.store_task_memory(user_id, {
                "type": "plan_execution",
                "plan_id": execution_results["plan_id"],
                "status": execution_results["status"],
                "results": execution_results
            })
            
            execution_results["completed_at"] = datetime.now().isoformat()
            
            return execution_results
            
        except Exception as e:
            execution_results["status"] = "failed"
            execution_results["final_result"] = f"Execution failed: {str(e)}"
            execution_results["completed_at"] = datetime.now().isoformat()
            
            return execution_results
    
    async def _execute_step(self, step: PlanStep, user_id: int) -> Dict[str, Any]:
        """Execute a single step"""
        
        if not step.tool:
            # Non-tool step (informational)
            return {
                "success": True,
                "message": f"Step completed: {step.description}",
                "type": "informational"
            }
        
        try:
            # Get tool instance
            tool = get_tool(step.tool)
            
            # Execute tool with parameters
            if step.parameters:
                result = await tool.execute(**step.parameters)
            else:
                result = await tool.execute()
            
            # Store tool result in memory if relevant
            if result.success and result.data:
                self._store_tool_result(step.tool, result.data, user_id)
            
            return {
                "success": result.success,
                "data": result.data,
                "error": result.error,
                "metadata": result.metadata,
                "type": "tool_execution"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "type": "tool_execution"
            }
    
    def _store_tool_result(self, tool_name: str, result_data: Any, user_id: int):
        """Store tool result in memory system"""
        try:
            if tool_name == "search_tool":
                self.memory_system.store_request_memory(user_id, {
                    "type": "search_result",
                    "tool": tool_name,
                    "data": result_data
                })
            elif tool_name == "document_parser":
                self.memory_system.store_document_memory(user_id, {
                    "type": "parsed_document",
                    "tool": tool_name,
                    "data": result_data
                })
            elif tool_name == "form_generator":
                self.memory_system.store_task_memory(user_id, {
                    "type": "generated_form",
                    "tool": tool_name,
                    "data": result_data
                })
        except Exception:
            pass  # Don't fail execution if memory storage fails
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get status of a plan execution"""
        # This would typically be stored in a database or cache
        # For now, return a placeholder
        return {
            "execution_id": execution_id,
            "status": "not_found",
            "message": "Execution not found"
        }
    
    async def pause_execution(self, execution_id: str) -> bool:
        """Pause an ongoing execution"""
        # Implementation for pausing execution
        return True
    
    async def resume_execution(self, execution_id: str) -> bool:
        """Resume a paused execution"""
        # Implementation for resuming execution
        return True
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an ongoing execution"""
        # Implementation for canceling execution
        return True
    
    async def retry_failed_steps(self, task_id: int) -> Dict[str, Any]:
        """Retry failed steps in a task"""
        
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task or not task.plan:
            return {"success": False, "error": "Task not found or no plan available"}
        
        plan_data = task.plan
        plan = GeneratedPlan(**plan_data)
        
        # Find failed steps
        failed_steps = [step for step in plan.steps if step.status == "failed"]
        
        if not failed_steps:
            return {"success": True, "message": "No failed steps to retry"}
        
        # Reset failed steps to pending
        for step in failed_steps:
            step.status = "pending"
            step.result = None
        
        # Re-execute the plan
        return await self.execute_plan(plan, task.user_id, task_id)
    
    async def get_available_tools_info(self) -> List[Dict[str, Any]]:
        """Get information about available tools"""
        tools_info = []
        
        for tool_name in list_available_tools():
            tool = get_tool(tool_name)
            tools_info.append({
                "name": tool.name,
                "description": tool.description,
                "parameters_schema": tool.get_parameters_schema()
            })
        
        return tools_info
    
    async def suggest_tools_for_request(self, user_request: str) -> List[str]:
        """Suggest relevant tools for a user request"""
        request_lower = user_request.lower()
        
        tool_suggestions = []
        
        # Simple keyword-based tool suggestion
        if any(keyword in request_lower for keyword in ["search", "find", "information", "procedure"]):
            tool_suggestions.append("search_tool")
        
        if any(keyword in request_lower for keyword in ["scrape", "website", "details", "form"]):
            tool_suggestions.append("scraper_tool")
        
        if any(keyword in request_lower for keyword in ["document", "pdf", "parse", "extract"]):
            tool_suggestions.append("document_parser")
        
        if any(keyword in request_lower for keyword in ["form", "application", "fill", "generate"]):
            tool_suggestions.append("form_generator")
        
        if any(keyword in request_lower for keyword in ["reminder", "deadline", "appointment", "date"]):
            tool_suggestions.append("reminder_tool")
        
        if any(keyword in request_lower for keyword in ["status", "track", "application", "progress"]):
            tool_suggestions.append("status_tracker")
        
        return tool_suggestions
    
    async def get_execution_summary(self, task_id: int) -> Dict[str, Any]:
        """Get a summary of task execution"""
        
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return {"success": False, "error": "Task not found"}
        
        if not task.results:
            return {"success": False, "error": "No execution results available"}
        
        results = task.results
        
        summary = {
            "task_id": task_id,
            "title": task.title,
            "status": results.get("status", "unknown"),
            "started_at": results.get("started_at"),
            "completed_at": results.get("completed_at"),
            "total_steps": len(task.plan.get("steps", [])),
            "completed_steps": len(results.get("completed_steps", [])),
            "failed_steps": len(results.get("failed_steps", [])),
            "success_rate": 0,
            "final_result": results.get("final_result"),
            "step_details": []
        }
        
        if summary["total_steps"] > 0:
            summary["success_rate"] = (summary["completed_steps"] / summary["total_steps"]) * 100
        
        # Add step details
        for step_data in task.plan.get("steps", []):
            step_summary = {
                "id": step_data["id"],
                "description": step_data["description"],
                "tool": step_data.get("tool"),
                "status": step_data.get("status", "pending"),
                "result": step_data.get("result")
            }
            summary["step_details"].append(step_summary)
        
        return {"success": True, "summary": summary}
