from fastapi import APIRouter, HTTPException, status
from app.models.user import UserCreate, UserLogin, UserResponse
from app.services.user_service import user_service
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter()

class ProfileUpdateRequest(BaseModel):
    name: str = None
    phone: str = None
    email: str = None
    current_password: str = None
    new_password: str = None

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        # Validate input
        if not user_data.name or len(user_data.name) < 3:
            raise HTTPException(
                status_code=400, 
                detail="Name must be at least 3 characters long"
            )
        
        if not user_data.phone or len(user_data.phone) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Phone number must be at least 10 digits"
            )
        
        if not user_data.password or len(user_data.password) < 6:
            raise HTTPException(
                status_code=400, 
                detail="Password must be at least 6 characters long"
            )
        
        # Create user
        user = user_service.create_user(user_data)
        if not user:
            raise HTTPException(
                status_code=400, 
                detail="User with this name already exists"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=UserResponse)
async def login_user(login_data: UserLogin):
    """Authenticate user login"""
    try:
        if not login_data.name or not login_data.password:
            raise HTTPException(
                status_code=400, 
                detail="Name and password are required"
            )
        
        user = user_service.authenticate_user(login_data.name, login_data.password)
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="Invalid name or password"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/profile/{username}")
async def get_user_profile(username: str):
    """Get user profile"""
    try:
        user = user_service.get_user_by_name(username)
        if not user:
            raise HTTPException(
                status_code=404, 
                detail="User not found"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

@router.put("/profile/{username}")
async def update_user_profile(username: str, request: ProfileUpdateRequest):
    """Update user profile"""
    try:
        # Verify user exists
        user = user_service.get_user_by_name(username)
        if not user:
            raise HTTPException(
                status_code=404, 
                detail="User not found"
            )
        
        # If changing password, verify current password
        if request.new_password:
            if not request.current_password:
                raise HTTPException(
                    status_code=400,
                    detail="Current password is required to change password"
                )
            
            # Verify current password
            auth_user = user_service.authenticate_user(username, request.current_password)
            if not auth_user:
                raise HTTPException(
                    status_code=401,
                    detail="Current password is incorrect"
                )
        
        # Update profile
        success = user_service.update_user_profile(
            username=username,
            name=request.name,
            phone=request.phone,
            email=request.email,
            new_password=request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to update profile"
            )
        
        # Get updated user data
        updated_user = user_service.get_user_by_name(request.name or username)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": updated_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.get("/check-username/{username}")
async def check_username_availability(username: str):
    """Check if username is available"""
    try:
        user = user_service.get_user_by_name(username)
        return {"available": user is None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check username: {str(e)}")
