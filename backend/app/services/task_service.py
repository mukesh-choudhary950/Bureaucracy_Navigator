from typing import Optional, List
from app.models.task import Task, TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self):
        self.db_path = "tasks.db"
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with tasks table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    assigned_to TEXT NOT NULL,
                    assigned_by TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    due_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Task database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing task database: {str(e)}")

    def create_task(self, task_data: TaskCreate, assigned_by: str) -> Optional[TaskResponse]:
        """Create a new task"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks (title, description, assigned_to, assigned_by, priority, due_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                task_data.title,
                task_data.description,
                task_data.assigned_to,
                assigned_by,
                task_data.priority.value,
                task_data.due_date.isoformat() if task_data.due_date else None
            ))
            
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return TaskResponse(
                id=task_id,
                title=task_data.title,
                description=task_data.description,
                assigned_to=task_data.assigned_to,
                assigned_by=assigned_by,
                status=TaskStatus.PENDING,
                priority=task_data.priority,
                due_date=task_data.due_date,
                created_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return None

    def get_tasks_by_user(self, username: str) -> List[TaskResponse]:
        """Get tasks assigned to a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, description, assigned_to, assigned_by, 
                       status, priority, due_date, created_at, updated_at
                FROM tasks 
                WHERE assigned_to = ? OR assigned_by = ?
                ORDER BY created_at DESC
            ''', (username, username))
            
            rows = cursor.fetchall()
            conn.close()
            
            tasks = []
            for row in rows:
                tasks.append(TaskResponse(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    assigned_to=row[3],
                    assigned_by=row[4],
                    status=TaskStatus(row[5]),
                    priority=TaskPriority(row[6]),
                    due_date=datetime.fromisoformat(row[7]) if row[7] else None,
                    created_at=datetime.fromisoformat(row[8]),
                    updated_at=datetime.fromisoformat(row[9]) if row[9] else None
                ))
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting tasks: {str(e)}")
            return []

    def update_task_status(self, task_id: int, status: TaskStatus) -> bool:
        """Update task status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status.value, task_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            return False

    def get_task_by_id(self, task_id: int) -> Optional[TaskResponse]:
        """Get task by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, description, assigned_to, assigned_by, 
                       status, priority, due_date, created_at, updated_at
                FROM tasks 
                WHERE id = ?
            ''', (task_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return TaskResponse(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    assigned_to=row[3],
                    assigned_by=row[4],
                    status=TaskStatus(row[5]),
                    priority=TaskPriority(row[6]),
                    due_date=datetime.fromisoformat(row[7]) if row[7] else None,
                    created_at=datetime.fromisoformat(row[8]),
                    updated_at=datetime.fromisoformat(row[9]) if row[9] else None
                )
            return None
        except Exception as e:
            logger.error(f"Error getting task: {str(e)}")
            return None

    def assign_task(self, task_id: int, assigned_to: str) -> bool:
        """Assign task to a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks 
                SET assigned_to = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (assigned_to, task_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error assigning task: {str(e)}")
            return False

    def get_unassigned_tasks(self) -> List[TaskResponse]:
        """Get all unassigned tasks"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, description, assigned_to, assigned_by, 
                       status, priority, due_date, created_at, updated_at
                FROM tasks 
                WHERE assigned_to IS NULL OR assigned_to = ''
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            tasks = []
            for row in rows:
                tasks.append(TaskResponse(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    assigned_to=row[3] or "Unassigned",
                    assigned_by=row[4],
                    status=TaskStatus(row[5]),
                    priority=TaskPriority(row[6]),
                    due_date=datetime.fromisoformat(row[7]) if row[7] else None,
                    created_at=datetime.fromisoformat(row[8]),
                    updated_at=datetime.fromisoformat(row[9]) if row[9] else None
                ))
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting unassigned tasks: {str(e)}")
            return []

    def get_all_tasks(self) -> List[TaskResponse]:
        """Get all tasks"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, description, assigned_to, assigned_by, 
                       status, priority, due_date, created_at, updated_at
                FROM tasks 
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            tasks = []
            for row in rows:
                tasks.append(TaskResponse(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    assigned_to=row[3] or "Unassigned",
                    assigned_by=row[4],
                    status=TaskStatus(row[5]),
                    priority=TaskPriority(row[6]),
                    due_date=datetime.fromisoformat(row[7]) if row[7] else None,
                    created_at=datetime.fromisoformat(row[8]),
                    updated_at=datetime.fromisoformat(row[9]) if row[9] else None
                ))
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting all tasks: {str(e)}")
            return []

# Global instance
task_service = TaskService()
