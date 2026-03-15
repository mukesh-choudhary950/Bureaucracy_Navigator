from typing import Optional, List
from app.models.workflow import Workflow, WorkflowCreate, WorkflowResponse, WorkflowStep, WorkflowStepResponse, WorkflowStatus
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WorkflowService:
    def __init__(self):
        self.db_path = "workflows.db"
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with workflows and workflow_steps tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'not_started',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'not_started',
                    assigned_to TEXT NOT NULL,
                    due_date TIMESTAMP,
                    completed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (workflow_id) REFERENCES workflows (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Workflow database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing workflow database: {str(e)}")

    def create_workflow(self, workflow_data: WorkflowCreate, created_by: str) -> Optional[WorkflowResponse]:
        """Create a new workflow"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO workflows (title, description, created_by, priority, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                workflow_data.title,
                workflow_data.description,
                created_by,
                workflow_data.priority,
                workflow_data.start_date.isoformat() if workflow_data.start_date else None,
                workflow_data.end_date.isoformat() if workflow_data.end_date else None
            ))
            
            workflow_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return WorkflowResponse(
                id=workflow_id,
                title=workflow_data.title,
                description=workflow_data.description,
                created_by=created_by,
                status=WorkflowStatus.NOT_STARTED,
                priority=workflow_data.priority,
                start_date=workflow_data.start_date,
                end_date=workflow_data.end_date,
                created_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            return None

    def get_workflows_by_user(self, username: str) -> List[WorkflowResponse]:
        """Get workflows created by a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, description, created_by, status, priority,
                       start_date, end_date, created_at, updated_at
                FROM workflows 
                WHERE created_by = ?
                ORDER BY created_at DESC
            ''', (username,))
            
            rows = cursor.fetchall()
            conn.close()
            
            workflows = []
            for row in rows:
                workflows.append(WorkflowResponse(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    created_by=row[3],
                    status=WorkflowStatus(row[4]),
                    priority=row[5],
                    start_date=datetime.fromisoformat(row[6]) if row[6] else None,
                    end_date=datetime.fromisoformat(row[7]) if row[7] else None,
                    created_at=datetime.fromisoformat(row[8]),
                    updated_at=datetime.fromisoformat(row[9]) if row[9] else None
                ))
            
            return workflows
        except Exception as e:
            logger.error(f"Error getting workflows: {str(e)}")
            return []

    def get_workflow_steps(self, workflow_id: int) -> List[WorkflowStepResponse]:
        """Get steps for a workflow"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, workflow_id, title, description, status, assigned_to,
                       due_date, completed_at, created_at
                FROM workflow_steps 
                WHERE workflow_id = ?
                ORDER BY created_at ASC
            ''', (workflow_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            steps = []
            for row in rows:
                steps.append(WorkflowStepResponse(
                    id=row[0],
                    workflow_id=row[1],
                    title=row[2],
                    description=row[3],
                    status=WorkflowStatus(row[4]),
                    assigned_to=row[5],
                    due_date=datetime.fromisoformat(row[6]) if row[6] else None,
                    completed_at=datetime.fromisoformat(row[7]) if row[7] else None,
                    created_at=datetime.fromisoformat(row[8])
                ))
            
            return steps
        except Exception as e:
            logger.error(f"Error getting workflow steps: {str(e)}")
            return []

    def update_workflow_status(self, workflow_id: int, status: WorkflowStatus) -> bool:
        """Update workflow status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE workflows 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status.value, workflow_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating workflow: {str(e)}")
            return False

    def update_step_status(self, step_id: int, status: WorkflowStatus) -> bool:
        """Update workflow step status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            completed_at = datetime.now().isoformat() if status == WorkflowStatus.COMPLETED else None
            
            cursor.execute('''
                UPDATE workflow_steps 
                SET status = ?, completed_at = ?
                WHERE id = ?
            ''', (status.value, completed_at, step_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating workflow step: {str(e)}")
            return False

# Global instance
workflow_service = WorkflowService()
