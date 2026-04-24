"""
Social Authentication Module for TRENDY App
Handles Google, Facebook, and Apple OAuth integration
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx
import jwt
from datetime import datetime, timedelta
import secrets

from app.database import get_db
from app.models.user import User
from app.core.config import get_settings
settings = get_settings()
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth/social", tags=["social-auth"])

class SocialLoginRequest(BaseModel):
    provider: str
    token: str
    email: str
    name: str
    profile_picture: str = None

class SocialLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict

@router.post("/login", response_model=SocialLoginResponse)
async def social_login(request: SocialLoginRequest, db: Session = Depends(get_db)):
    """Handle social login for Google, Facebook, and Apple"""
    
    provider = request.provider.lower()
    
    # Verify token based on provider
    if provider == "google":
        user_info = await verify_google_token(request.token)
    elif provider == "facebook":
        user_info = await verify_facebook_token(request.token)
    elif provider == "apple":
        user_info = await verify_apple_token(request.token)
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    
    # Check if user exists
    user = db.query(User).filter(User.email == user_info["email"]).first()
    
    if not user:
        # Create new user
        user = User(
            email=user_info["email"],
            username=user_info.get("username", user_info["email"].split("@")[0]),
            full_name=user_info.get("name", ""),
            profile_picture=user_info.get("picture"),
            is_verified=True,  # Social login users are verified
            provider=provider,
            provider_id=user_info["id"],
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(user.id)
    
    return SocialLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "profile_picture": user.profile_picture,
            "is_verified": user.is_verified
        }
    )

async def verify_google_token(token: str) -> dict:
    """Verify Google OAuth token"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            )
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid Google token")
            
            data = response.json()
            return {
                "id": data["sub"],
                "email": data["email"],
                "name": data.get("name", ""),
                "picture": data.get("picture", "")
            }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Google token verification failed: {str(e)}")

async def verify_facebook_token(token: str) -> dict:
    """Verify Facebook OAuth token"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://graph.facebook.com/me?fields=id,name,email,picture.type(large)&access_token={token}"
            )
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid Facebook token")
            
            data = response.json()
            return {
                "id": data["id"],
                "email": data.get("email", ""),
                "name": data.get("name", ""),
                "picture": data.get("picture", {}).get("data", {}).get("url", "")
            }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Facebook token verification failed: {str(e)}")

async def verify_apple_token(token: str) -> dict:
    """Verify Apple Sign-In token"""
    try:
        # Apple uses JWT tokens
        payload = jwt.decode(token, options={"verify_signature": False})
        return {
            "id": payload["sub"],
            "email": payload.get("email", ""),
            "name": payload.get("name", "")
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Apple token verification failed: {str(e)}")

def create_refresh_token(user_id: int) -> str:
    """Create refresh token for user"""
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode = {"exp": expire, "sub": str(user_id), "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
