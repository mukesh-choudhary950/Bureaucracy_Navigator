from typing import Dict, Any, List
from app.tools.base import BaseTool, ToolResult
from datetime import datetime, timedelta
import json

class ReminderTool(BaseTool):
    name = "reminder_tool"
    description = "Create reminders for government procedure deadlines and appointments"
    
    async def execute(self, reminder_type: str, details: Dict[str, Any]) -> ToolResult:
        """Create a reminder for government procedure tasks"""
        try:
            reminder = {
                "id": f"reminder_{datetime.now().timestamp()}",
                "type": reminder_type,
                "title": details.get("title", ""),
                "description": details.get("description", ""),
                "due_date": details.get("due_date", ""),
                "priority": details.get("priority", "medium"),
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "actions": []
            }
            
            # Add specific actions based on reminder type
            if reminder_type == "document_submission":
                reminder["actions"] = self._get_document_submission_actions(details)
            elif reminder_type == "appointment":
                reminder["actions"] = self._get_appointment_actions(details)
            elif reminder_type == "follow_up":
                reminder["actions"] = self._get_follow_up_actions(details)
            elif reminder_type == "payment":
                reminder["actions"] = self._get_payment_actions(details)
            
            # Calculate reminder schedule
            reminder["schedule"] = self._calculate_reminder_schedule(
                reminder["due_date"], 
                reminder["priority"]
            )
            
            return ToolResult(
                success=True,
                data={
                    "reminder": reminder,
                    "message": f"Reminder created: {reminder['title']}",
                    "next_reminder": reminder["schedule"][0] if reminder["schedule"] else None
                },
                metadata={"reminder_type": reminder_type}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Reminder creation error: {str(e)}"
            )
    
    def _get_document_submission_actions(self, details: Dict[str, Any]) -> List[str]:
        """Get actions for document submission reminder"""
        actions = [
            "Gather all required documents",
            "Make photocopies of originals",
            "Get documents self-attested",
            "Prepare application form",
            "Check office timings",
            "Visit the government office"
        ]
        
        if details.get("online_submission"):
            actions.extend([
                "Scan documents",
                "Upload to portal",
                "Pay online fees",
                "Save confirmation receipt"
            ])
        
        return actions
    
    def _get_appointment_actions(self, details: Dict[str, Any]) -> List[str]:
        """Get actions for appointment reminder"""
        actions = [
            "Confirm appointment time and date",
            "Carry required documents",
            "Reach venue 15 minutes early",
            "Bring appointment confirmation",
            "Note contact person details"
        ]
        
        if details.get("biometric"):
            actions.append("Carry original ID for biometric verification")
        
        if details.get("medical_test"):
            actions.extend([
                "Fast if required (12 hours)",
                "Carry medical reports",
                "Avoid alcohol/smoking 24 hours before"
            ])
        
        return actions
    
    def _get_follow_up_actions(self, details: Dict[str, Any]) -> List[str]:
        """Get actions for follow-up reminder"""
        actions = [
            "Check application status online",
            "Call helpline number",
            "Visit office in person",
            "Bring application reference number",
            "Carry ID proof"
        ]
        
        if details.get("escalation"):
            actions.extend([
                "Contact higher authority",
                "Submit written complaint",
                "File RTI application if needed"
            ])
        
        return actions
    
    def _get_payment_actions(self, details: Dict[str, Any]) -> List[str]:
        """Get actions for payment reminder"""
        actions = [
            "Check exact fee amount",
            "Verify payment methods accepted",
            "Carry exact change if offline payment",
            "Save payment receipt",
            "Note transaction ID"
        ]
        
        payment_mode = details.get("payment_mode", "")
        if payment_mode == "online":
            actions.extend([
                "Ensure internet banking working",
                "Check card limits",
                "Save payment confirmation"
            ])
        elif payment_mode == "dd":
            actions.extend([
                "Visit bank for demand draft",
                "Carry application form copy",
                "Pay DD charges"
            ])
        
        return actions
    
    def _calculate_reminder_schedule(self, due_date: str, priority: str) -> List[str]:
        """Calculate reminder schedule based on due date and priority"""
        try:
            due_dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            now = datetime.now()
            
            schedules = []
            
            if priority == "high":
                # High priority: more frequent reminders
                schedules.extend([
                    (due_dt - timedelta(days=7)).isoformat(),
                    (due_dt - timedelta(days=3)).isoformat(),
                    (due_dt - timedelta(days=1)).isoformat(),
                    (due_dt - timedelta(hours=12)).isoformat(),
                    (due_dt - timedelta(hours=6)).isoformat(),
                    (due_dt - timedelta(hours=2)).isoformat()
                ])
            elif priority == "medium":
                # Medium priority: standard reminders
                schedules.extend([
                    (due_dt - timedelta(days=7)).isoformat(),
                    (due_dt - timedelta(days=3)).isoformat(),
                    (due_dt - timedelta(days=1)).isoformat(),
                    (due_dt - timedelta(hours=12)).isoformat()
                ])
            else:
                # Low priority: fewer reminders
                schedules.extend([
                    (due_dt - timedelta(days=7)).isoformat(),
                    (due_dt - timedelta(days=2)).isoformat(),
                    (due_dt - timedelta(days=1)).isoformat()
                ])
            
            # Filter out past dates and sort
            future_schedules = [
                schedule for schedule in schedules 
                if datetime.fromisoformat(schedule.replace('Z', '+00:00')) > now
            ]
            
            return sorted(future_schedules)
            
        except Exception:
            # Fallback to default schedule
            return [
                (datetime.now() + timedelta(days=7)).isoformat(),
                (datetime.now() + timedelta(days=3)).isoformat(),
                (datetime.now() + timedelta(days=1)).isoformat()
            ]
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "reminder_type": {
                    "type": "string",
                    "enum": ["document_submission", "appointment", "follow_up", "payment"],
                    "description": "Type of reminder to create"
                },
                "details": {
                    "type": "object",
                    "description": "Reminder details",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "due_date": {"type": "string", "format": "date-time"},
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "default": "medium"
                        },
                        "online_submission": {"type": "boolean"},
                        "biometric": {"type": "boolean"},
                        "medical_test": {"type": "boolean"},
                        "escalation": {"type": "boolean"},
                        "payment_mode": {
                            "type": "string",
                            "enum": ["online", "offline", "dd", "cash"]
                        }
                    },
                    "required": ["title", "due_date"]
                }
            },
            "required": ["reminder_type", "details"]
        }
