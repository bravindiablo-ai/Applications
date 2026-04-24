"""
Social Authentication Routes for TRENDY App
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.google import google_auth
from app.auth.facebook import facebook_auth
from app.auth.apple_fixed import apple_auth

router = APIRouter(prefix="/auth/social", tags=["social-auth"])

class GoogleAuthRequest(BaseModel):
    token: str

class FacebookAuthRequest(BaseModel):
    code: str
    redirect_uri: str

class AppleAuthRequest(BaseModel):
    token: str

@router.post("/google", summary="Authenticate with Google")
async def auth_google(
    request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user using Google OAuth token
    """
    try:
        result = await google_auth.authenticate_google_user(request.token, db)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )

@router.post("/facebook", summary="Authenticate with Facebook")
async def auth_facebook(
    request: FacebookAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user using Facebook OAuth code
    """
    try:
        result = await facebook_auth.authenticate_facebook_user(
            request.code, request.redirect_uri, db
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Facebook authentication failed: {str(e)}"
        )

@router.post("/apple", summary="Authenticate with Apple")
async def auth_apple(
    request: AppleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user using Apple Sign-In token
    """
    try:
        result = await apple_auth.authenticate_apple_user(request.token, db)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Apple authentication failed: {str(e)}"
        )

@router.get("/providers", summary="Get available social providers")
async def get_social_providers():
    """
    Get list of available social authentication providers
    """
    providers = []
    
    if google_auth.client_id:
        providers.append({
            "provider": "google",
            "name": "Google",
            "client_id": google_auth.client_id
        })
    
    if facebook_auth.client_id:
        providers.append({
            "provider": "facebook",
            "name": "Facebook",
            "client_id": facebook_auth.client_id
        })
    
    if apple_auth.client_id:
        providers.append({
            "provider": "apple",
            "name": "Apple",
            "client_id": apple_auth.client_id
        })
    
    return {"providers": providers}

@router.get("/user/{user_id}/providers", summary="Get user's social providers")
async def get_user_social_providers(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get list of social providers linked to a user account
    """
    from app.models.social_provider import SocialProvider
    
    providers = db.query(SocialProvider).filter(
        SocialProvider.user_id == user_id
    ).all()
    
    return {
        "providers": [
            {
                "provider": p.provider,
                "provider_user_id": p.provider_user_id,
                "email": p.email,
                "display_name": p.display_name,
                "created_at": p.created_at
            }
            for p in providers
        ]
    }
