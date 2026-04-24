from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.auth.google import google_auth

router = APIRouter(prefix="/auth/google", tags=["Google Authentication"])

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class GoogleLoginRequest(BaseModel):
    token: str

class GoogleLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

@router.post("/login", response_model=GoogleLoginResponse)
async def google_login(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth token
    """
    try:
        result = await google_auth.handle_google_login(db, request.token)
        
        return GoogleLoginResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            user_id=result["user"].id,
            email=result["user"].email,
            username=result["user"].username,
            display_name=result["user"].display_name,
            avatar_url=result["user"].avatar_url
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

import os
from dotenv import load_dotenv

load_dotenv()

@router.get("/config")
async def get_google_config():
    """
    Get Google OAuth configuration for frontend
    """
    return {
        "client_id": google_auth.client_id,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "scope": "openid email profile",
        "redirect_uri": os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:3000/auth/google/callback")
    }
