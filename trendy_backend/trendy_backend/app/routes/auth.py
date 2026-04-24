"""
Authentication API Routes for TRENDY App
Handles user registration, login, and authentication using Firebase
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth
import httpx

from app.database import get_db
from app.models.user import User
from app.core.config import get_settings
from app.auth.middleware import get_current_user, verify_firebase_token
from app.auth.email_verification import send_verification_email

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()
settings = get_settings()

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    username: str = Field(..., min_length=3, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)

class UserLoginRequest(BaseModel):
    identifier: str  # Can be email or username
    password: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: Dict[str, Any]

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

@router.post("/register", response_model=AuthResponse)
async def register_user(
    request: UserRegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user with email and password"""
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == request.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # For development with mock authentication, generate a mock firebase_uid
        # In production, this would come from Firebase Auth
        mock_firebase_uid = f"mock_uid_{request.email.replace('@', '_').replace('.', '_')}"
        
        # Create user in database
        user = User(
            firebase_uid=mock_firebase_uid,
            email=request.email,
            username=request.username,
            display_name=request.display_name or request.username,
            is_verified=False,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Send verification email in background
        background_tasks.add_task(send_verification_email, user.id, user.email)
        
        # Send welcome email
        background_tasks.add_task(email_service.send_welcome_email, user.email, user.username)
        
        # Generate mock token for immediate login
        mock_token = f"mock_token_{user.id}"
        
        return AuthResponse(
            access_token=mock_token,
            refresh_token="",  # Refresh tokens will be implemented later
            user={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "display_name": user.display_name,
                "is_verified": user.is_verified,
                "avatar_url": user.avatar_url
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=AuthResponse)
async def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Login user with email/username and password"""
    try:
        # Find user by email or username
        user = db.query(User).filter(
            (User.email == request.identifier) | (User.username == request.identifier)
        ).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Account is deactivated")
        
        # For development with mock authentication, bypass Firebase verification
        # In production, this would verify with Firebase
        if request.password != "password":  # Simple mock password check
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate mock token for login
        mock_token = f"mock_token_{user.id}"
        
        return AuthResponse(
            access_token=mock_token,
            refresh_token="",  # Refresh tokens will be implemented later
            user={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "display_name": user.display_name,
                "is_verified": user.is_verified,
                "avatar_url": user.avatar_url
            }
        )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/password/reset")
async def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request password reset email"""
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            # Don't reveal if email exists for security
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Generate password reset link
        reset_link = auth.generate_password_reset_link(request.email)
        
        # Send email in background (implementation needed)
        # background_tasks.add_task(send_password_reset_email, user.email, reset_link)
        
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

@router.post("/password/reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    """Confirm password reset with token"""
    try:
        # Verify the reset token
        # This would typically involve decoding a JWT or using Firebase Admin SDK
        # For now, we'll implement a basic version
        
        # In a real implementation, you would:
        # 1. Verify the reset token is valid
        # 2. Get the user email from the token
        # 3. Update the password in Firebase
        
        raise HTTPException(status_code=501, detail="Password reset confirmation not implemented yet")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "avatar_url": current_user.avatar_url,
        "is_verified": current_user.is_verified,
        "is_premium": current_user.is_premium,
        "created_at": current_user.created_at
    }

@router.post("/refresh")
async def refresh_token(
    refresh_token: str
):
    """Refresh access token using refresh token"""
    try:
        # Firebase token refresh implementation
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://securetoken.googleapis.com/v1/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                },
                params={"key": settings.firebase_api_key}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            data = response.json()
            return {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_in": data["expires_in"]
            }
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token refresh failed")
