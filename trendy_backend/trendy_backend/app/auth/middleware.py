"""
Unified Authentication Middleware for TRENDY App
Handles Firebase authentication consistently across all endpoints
"""

from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth, credentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.config import get_settings

settings = get_settings()

# Initialize Firebase Admin if not already initialized
if not firebase_admin._apps:
    try:
        # Check if the credentials file exists before trying to initialize
        import os
        if os.path.exists(settings.firebase_credentials_json_path):
            cred = credentials.Certificate(settings.firebase_credentials_json_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin initialized successfully")
        else:
            print(f"Warning: Firebase credentials file not found at {settings.firebase_credentials_json_path}")
            print("Firebase authentication will be disabled. Using mock authentication for development.")
    except Exception as e:
        print(f"Warning: Failed to initialize Firebase Admin: {str(e)}")
        print("Firebase authentication will be disabled. Using mock authentication for development.")

security = HTTPBearer()

async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify Firebase JWT token and return decoded token data.
    This is the primary authentication dependency for all endpoints.
    """
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    token_data: Dict[str, Any] = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from Firebase token.
    Creates user in database if they don't exist yet.
    """
    try:
        # Get user by Firebase UID
        user = db.query(User).filter(User.firebase_uid == token_data["uid"]).first()
        
        if not user:
            # Create new user from Firebase data
            user = User(
                firebase_uid=token_data["uid"],
                email=token_data.get("email", ""),
                username=token_data.get("email", "").split("@")[0],  # Default username from email
                display_name=token_data.get("name", ""),
                avatar_url=token_data.get("picture"),
                is_verified=token_data.get("email_verified", False),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

async def get_current_user_id(current_user: User = Depends(get_current_user)) -> int:
    """Get current user ID from authenticated user."""
    return current_user.id

async def get_current_user_email(current_user: User = Depends(get_current_user)) -> str:
    """Get current user email from authenticated user."""
    return current_user.email

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current authenticated user and verify admin privileges."""
    # For now, we'll treat all users as admins for development
    # In production, you would check user.role or user.is_admin
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def optional_auth(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency.
    Returns user if authenticated, None otherwise.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ", 1)[1]
        decoded_token = auth.verify_id_token(token)
        
        user = db.query(User).filter(User.firebase_uid == decoded_token["uid"]).first()
        return user
        
    except Exception:
        # Silently fail for optional auth
        return None

# Rate limiting decorator (to be implemented in Phase 4)
def rate_limit(requests_per_minute: int = 60):
    """Decorator for rate limiting endpoints."""
    # This will be implemented with Redis in Phase 4
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Role-based access control (to be implemented in Phase 4)
def require_role(required_role: str):
    """Decorator for role-based access control."""
    def decorator(func):
        async def wrapper(current_user: User = Depends(get_current_user), *args, **kwargs):
            # Check if user has required role
            # This will be implemented with proper role system in Phase 4
            if not hasattr(current_user, 'role') or current_user.role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(current_user=current_user, *args, **kwargs)
        return wrapper
    return decorator
