from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings
from app.schemas.task import PlanStep, GeneratedPlan
import json
import re

class TaskPlanner:
    """Autonomous task planner using LLM"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_plan(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> GeneratedPlan:
        """Generate a step-by-step plan for the user request"""
        
        system_prompt = """You are an expert government procedure planner. Your task is to break down user requests into clear, actionable steps for obtaining government certificates or services in India.

Follow these guidelines:
1. Break the request into logical, sequential steps
2. Each step should be specific and actionable
3. Identify which tool (if any) should be used for each step
4. Consider the typical government procedure flow
5. Include document preparation, form filling, submission, and follow-up steps

Available tools:
- search_tool: Search for government information and procedures
- scraper_tool: Extract detailed information from government websites
- document_parser: Extract text from uploaded documents
- form_generator: Generate pre-filled application forms
- reminder_tool: Create reminders for deadlines and appointments
- status_tracker: Track application status

Common procedure flow:
1. Information gathering
2. Document preparation
3. Form filling
4. Submission
5. Verification
6. Follow-up

Return a JSON response with:
{
  "steps": [
    {
      "id": "step_1",
      "description": "Clear description of what to do",
      "tool": "tool_name or null",
      "parameters": {"key": "value"} or {},
      "status": "pending"
    }
  ],
  "reasoning": "Explanation of why this plan was chosen"
}"""

        user_prompt = f"""User Request: {user_request}

Additional Context: {json.dumps(context) if context else "No additional context"}

Please generate a step-by-step plan to help the user complete this government procedure."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                plan_data = self._create_fallback_plan(user_request)
            
            # Convert to PlanStep objects
            steps = []
            for step_data in plan_data.get("steps", []):
                step = PlanStep(
                    id=step_data.get("id", f"step_{len(steps)+1}"),
                    description=step_data.get("description", ""),
                    tool=step_data.get("tool"),
                    parameters=step_data.get("parameters", {}),
                    status=step_data.get("status", "pending")
                )
                steps.append(step)
            
            return GeneratedPlan(
                steps=steps,
                reasoning=plan_data.get("reasoning", "Generated plan based on standard government procedures")
            )
            
        except Exception as e:
            # Fallback plan in case of API failure
            return self._create_fallback_plan_object(user_request)
    
    def _create_fallback_plan(self, user_request: str) -> Dict[str, Any]:
        """Create a fallback plan when LLM fails"""
        return {
            "steps": [
                {
                    "id": "step_1",
                    "description": "Search for procedure information",
                    "tool": "search_tool",
                    "parameters": {"query": user_request},
                    "status": "pending"
                },
                {
                    "id": "step_2",
                    "description": "Identify required documents",
                    "tool": "scraper_tool",
                    "parameters": {"content_type": "documents"},
                    "status": "pending"
                },
                {
                    "id": "step_3",
                    "description": "Prepare application form",
                    "tool": "form_generator",
                    "parameters": {},
                    "status": "pending"
                },
                {
                    "id": "step_4",
                    "description": "Submit application",
                    "tool": None,
                    "parameters": {},
                    "status": "pending"
                },
                {
                    "id": "step_5",
                    "description": "Track application status",
                    "tool": "status_tracker",
                    "parameters": {},
                    "status": "pending"
                }
            ],
            "reasoning": "Fallback plan using standard government procedure steps"
        }
    
    def _create_fallback_plan_object(self, user_request: str) -> GeneratedPlan:
        """Create a fallback plan object when LLM fails"""
        plan_data = self._create_fallback_plan(user_request)
        
        steps = []
        for step_data in plan_data.get("steps", []):
            step = PlanStep(
                id=step_data.get("id", f"step_{len(steps)+1}"),
                description=step_data.get("description", ""),
                tool=step_data.get("tool"),
                parameters=step_data.get("parameters", {}),
                status=step_data.get("status", "pending")
            )
            steps.append(step)
        
        return GeneratedPlan(
            steps=steps,
            reasoning=plan_data.get("reasoning", "Generated plan based on standard government procedures")
        )
    
    async def refine_plan(self, current_plan: GeneratedPlan, user_feedback: str) -> GeneratedPlan:
        """Refine the existing plan based on user feedback"""
        
        system_prompt = """You are an expert government procedure planner. Your task is to refine an existing plan based on user feedback.

Analyze the user feedback and modify the plan accordingly. You can:
- Add new steps
- Remove unnecessary steps
- Modify existing steps
- Reorder steps
- Change tool assignments

Return a JSON response with the same format as the original plan generation."""

        current_plan_json = {
            "steps": [
                {
                    "id": step.id,
                    "description": step.description,
                    "tool": step.tool,
                    "parameters": step.parameters,
                    "status": step.status
                }
                for step in current_plan.steps
            ]
        }

        user_prompt = f"""Current Plan:
{json.dumps(current_plan_json, indent=2)}

User Feedback: {user_feedback}

Please refine the plan based on this feedback."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
            else:
                # Return original plan if parsing fails
                return current_plan
            
            # Convert to PlanStep objects
            steps = []
            for step_data in plan_data.get("steps", []):
                step = PlanStep(
                    id=step_data.get("id", f"step_{len(steps)+1}"),
                    description=step_data.get("description", ""),
                    tool=step_data.get("tool"),
                    parameters=step_data.get("parameters", {}),
                    status=step_data.get("status", "pending")
                )
                steps.append(step)
            
            return GeneratedPlan(
                steps=steps,
                reasoning=plan_data.get("reasoning", "Plan refined based on user feedback")
            )
            
        except Exception as e:
            # Return original plan if refinement fails
            return current_plan
