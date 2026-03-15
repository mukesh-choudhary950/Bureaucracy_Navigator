from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[int] = None
    name: str
    phone: str
    email: Optional[str] = None
    password: str
    created_at: Optional[datetime] = None

class UserCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    name: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
