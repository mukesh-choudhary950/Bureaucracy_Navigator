from typing import Optional, List
from app.models.user import User, UserCreate, UserResponse
from app.core.config import settings
import sqlite3
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.db_path = "users.db"
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with users table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    email TEXT,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("User database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")

    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE name = ?", (user_data.name,))
            if cursor.fetchone():
                conn.close()
                return None
            
            # Hash password and create user
            hashed_password = self.hash_password(user_data.password)
            cursor.execute('''
                INSERT INTO users (name, phone, email, password)
                VALUES (?, ?, ?, ?)
            ''', (user_data.name, user_data.phone, user_data.email, hashed_password))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Return user response
            return UserResponse(
                id=user_id,
                name=user_data.name,
                phone=user_data.phone,
                email=user_data.email,
                created_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None

    def authenticate_user(self, name: str, password: str) -> Optional[UserResponse]:
        """Authenticate user with name and password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(password)
            cursor.execute('''
                SELECT id, name, phone, email, created_at 
                FROM users 
                WHERE name = ? AND password = ?
            ''', (name, hashed_password))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return UserResponse(
                    id=row[0],
                    name=row[1],
                    phone=row[2],
                    email=row[3],
                    created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now()
                )
            return None
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None

    def get_user_by_name(self, name: str) -> Optional[UserResponse]:
        """Get user by name"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, phone, email, created_at 
                FROM users 
                WHERE name = ?
            ''', (name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return UserResponse(
                    id=row[0],
                    name=row[1],
                    phone=row[2],
                    email=row[3],
                    created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now()
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None

    def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username (alias for get_user_by_name)"""
        return self.get_user_by_name(username)

    def get_all_users(self) -> List[UserResponse]:
        """Get all users"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, phone, email, created_at 
                FROM users 
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            users = []
            for row in rows:
                users.append(UserResponse(
                    id=row[0],
                    name=row[1],
                    phone=row[2],
                    email=row[3],
                    created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now()
                ))
            
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []

    def update_user_profile(self, username: str, name: str = None, phone: str = None, email: str = None, new_password: str = None) -> bool:
        """Update user profile information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if name and name != username:
                # Check if new name is already taken
                cursor.execute("SELECT id FROM users WHERE name = ? AND name != ?", (name, username))
                if cursor.fetchone():
                    conn.close()
                    logger.error(f"Cannot update profile: name '{name}' already exists")
                    return False
                updates.append("name = ?")
                params.append(name)
            
            if phone:
                updates.append("phone = ?")
                params.append(phone)
            
            if email:
                updates.append("email = ?")
                params.append(email)
            
            if new_password:
                hashed_password = self.hash_password(new_password)
                updates.append("password = ?")
                params.append(hashed_password)
            
            if not updates:
                conn.close()
                return True  # Nothing to update
            
            # Execute update
            query = f"UPDATE users SET {', '.join(updates)} WHERE name = ?"
            params.append(username)
            
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            
            logger.info(f"Profile updated successfully for user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False

# Global instance
user_service = UserService()
