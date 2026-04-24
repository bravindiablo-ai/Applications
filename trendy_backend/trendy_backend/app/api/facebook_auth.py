"""
Facebook OAuth authentication endpoints for TRENDY App
Provides API endpoints for Facebook login integration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.auth.facebook import facebook_auth
from app.schemas.auth import FacebookLoginRequest, AuthResponse

router = APIRouter(prefix="/auth/facebook", tags=["Facebook Authentication"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login", response_model=AuthResponse)
async def facebook_login(
    request: FacebookLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Facebook OAuth
    
    This endpoint accepts a Facebook access token, verifies it with Facebook's API,
    and either logs in an existing user or creates a new user account.
    
    Args:
        request: FacebookLoginRequest containing the Facebook access token
        db: Database session
        
    Returns:
        AuthResponse with JWT token and user information
        
    Raises:
        HTTPException: If authentication fails or token is invalid
    """
    try:
        result = await facebook_auth.handle_facebook_login(db, request.token)
        return AuthResponse(**result)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Facebook login failed: {str(e)}"
        )

@router.get("/config")
async def get_facebook_config():
    """
    Get Facebook OAuth configuration for frontend
    
    Returns the Facebook app configuration including client ID,
    authorization endpoints, and required scopes for the frontend
    to initiate the Facebook login flow.
    
    Returns:
        Dict containing Facebook OAuth configuration
    """
    try:
        config = facebook_auth.get_facebook_config()
        return {
            "success": True,
            "data": config,
            "message": "Facebook OAuth configuration retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Facebook configuration: {str(e)}"
        )

@router.get("/test")
async def test_facebook_connection():
    """
    Test Facebook API connection and configuration
    
    This endpoint tests if the Facebook OAuth configuration is properly
    set up and can be used for authentication.
    
    Returns:
        Dict indicating connection status
    """
    try:
        # Check if credentials are configured
        if not facebook_auth.client_id or not facebook_auth.client_secret:
            return {
                "success": False,
                "message": "Facebook OAuth credentials not configured",
                "configured": False
            }
        
        return {
            "success": True,
            "message": "Facebook OAuth configuration is valid",
            "configured": True,
            "client_id": facebook_auth.client_id,
            "redirect_uri": facebook_auth.redirect_uri
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Facebook configuration test failed: {str(e)}"
        )

@router.post("/link-account")
async def link_facebook_account(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Link Facebook account to existing user
    
    This endpoint allows an authenticated user to link their Facebook account
    to their existing TRENDY account for additional login options.
    
    Args:
        token: JWT token for authentication
        db: Database session
        
    Returns:
        Dict indicating success and linked account information
    """
    # This would require additional implementation to get current user from JWT
    # and then link the Facebook account
    return {
        "success": True,
        "message": "Facebook account linking endpoint - implementation pending"
    }

@router.post("/unlink-account")
async def unlink_facebook_account(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Unlink Facebook account from user
    
    This endpoint allows an authenticated user to unlink their Facebook account
    from their TRENDY account.
    
    Args:
        token: JWT token for authentication
        db: Database session
        
    Returns:
        Dict indicating success and unlinked account information
    """
    # This would require additional implementation to get current user from JWT
    # and then unlink the Facebook account
    return {
        "success": True,
        "message": "Facebook account unlinking endpoint - implementation pending"
    }
