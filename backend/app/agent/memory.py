from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.user import Memory, User
from app.core.database import get_db
from datetime import datetime
import json

class MemorySystem:
    """Persistent memory system for user data and interactions"""
    
    def __init__(self):
        self.db = next(get_db())
    
    def store_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Store user profile information"""
        try:
            # Update user profile
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.profile_data = profile_data
                self.db.commit()
            
            # Store in memory
            memory = Memory(
                user_id=user_id,
                memory_type="profile",
                content=json.dumps(profile_data),
                metadata={"updated_at": datetime.now().isoformat()}
            )
            self.db.add(memory)
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def store_document_memory(self, user_id: int, document_info: Dict[str, Any]) -> bool:
        """Store document information in memory"""
        try:
            memory = Memory(
                user_id=user_id,
                memory_type="document",
                content=json.dumps(document_info),
                metadata={
                    "document_type": document_info.get("type", "unknown"),
                    "filename": document_info.get("filename", ""),
                    "stored_at": datetime.now().isoformat()
                }
            )
            self.db.add(memory)
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def store_request_memory(self, user_id: int, request_info: Dict[str, Any]) -> bool:
        """Store user request in memory"""
        try:
            memory = Memory(
                user_id=user_id,
                memory_type="request",
                content=json.dumps(request_info),
                metadata={
                    "request_type": request_info.get("type", "general"),
                    "created_at": datetime.now().isoformat()
                }
            )
            self.db.add(memory)
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def store_task_memory(self, user_id: int, task_info: Dict[str, Any]) -> bool:
        """Store completed task information in memory"""
        try:
            memory = Memory(
                user_id=user_id,
                memory_type="task",
                content=json.dumps(task_info),
                metadata={
                    "task_status": task_info.get("status", "completed"),
                    "task_type": task_info.get("type", "general"),
                    "completed_at": datetime.now().isoformat()
                }
            )
            self.db.add(memory)
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve user profile from memory"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and user.profile_data:
                return user.profile_data
            
            # Fallback to memory table
            memory = self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.memory_type == "profile"
            ).order_by(Memory.created_at.desc()).first()
            
            if memory:
                return json.loads(memory.content)
            
            return None
        except Exception:
            return None
    
    def get_user_documents(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieve all documents for a user"""
        try:
            memories = self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.memory_type == "document"
            ).order_by(Memory.created_at.desc()).all()
            
            documents = []
            for memory in memories:
                doc_data = json.loads(memory.content)
                doc_data["memory_id"] = memory.id
                doc_data["stored_at"] = memory.created_at.isoformat()
                documents.append(doc_data)
            
            return documents
        except Exception:
            return []
    
    def get_previous_requests(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve previous user requests"""
        try:
            memories = self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.memory_type == "request"
            ).order_by(Memory.created_at.desc()).limit(limit).all()
            
            requests = []
            for memory in memories:
                req_data = json.loads(memory.content)
                req_data["memory_id"] = memory.id
                req_data["created_at"] = memory.created_at.isoformat()
                requests.append(req_data)
            
            return requests
        except Exception:
            return []
    
    def get_completed_tasks(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve completed tasks for a user"""
        try:
            memories = self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.memory_type == "task"
            ).order_by(Memory.created_at.desc()).limit(limit).all()
            
            tasks = []
            for memory in memories:
                task_data = json.loads(memory.content)
                task_data["memory_id"] = memory.id
                task_data["completed_at"] = memory.created_at.isoformat()
                tasks.append(task_data)
            
            return tasks
        except Exception:
            return []
    
    def search_memory(self, user_id: int, query: str, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search through user memory"""
        try:
            query_filter = [Memory.user_id == user_id]
            if memory_type:
                query_filter.append(Memory.memory_type == memory_type)
            
            memories = self.db.query(Memory).filter(*query_filter).all()
            
            results = []
            search_query = query.lower()
            
            for memory in memories:
                content = json.loads(memory.content)
                content_str = json.dumps(content).lower()
                
                if search_query in content_str:
                    result = {
                        "memory_id": memory.id,
                        "memory_type": memory.memory_type,
                        "content": content,
                        "created_at": memory.created_at.isoformat(),
                        "metadata": memory.metadata
                    }
                    results.append(result)
            
            return results
        except Exception:
            return []
    
    def get_context_for_request(self, user_id: int, current_request: str) -> Dict[str, Any]:
        """Get relevant context for current request"""
        context = {
            "user_profile": self.get_user_profile(user_id),
            "recent_requests": self.get_previous_requests(user_id, limit=3),
            "completed_tasks": self.get_completed_tasks(user_id, limit=3),
            "available_documents": self.get_user_documents(user_id)
        }
        
        # Extract relevant information based on current request
        request_lower = current_request.lower()
        
        # Check for similar previous requests
        similar_requests = []
        for req in context["recent_requests"]:
            if any(word in req.get("request", "").lower() for word in request_lower.split() if len(word) > 3):
                similar_requests.append(req)
        
        context["similar_requests"] = similar_requests
        
        # Check for relevant documents
        relevant_docs = []
        for doc in context["available_documents"]:
            doc_type = doc.get("type", "").lower()
            if doc_type in request_lower:
                relevant_docs.append(doc)
        
        context["relevant_documents"] = relevant_docs
        
        return context
    
    def cleanup_old_memories(self, user_id: int, days_to_keep: int = 90) -> bool:
        """Clean up old memories beyond specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Delete old memories (except profile type)
            self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.created_at < cutoff_date,
                Memory.memory_type != "profile"
            ).delete()
            
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
