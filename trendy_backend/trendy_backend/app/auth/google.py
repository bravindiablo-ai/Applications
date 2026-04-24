"""
Google OAuth Implementation for TRENDY App
"""

import logging
from typing import Dict, Any
from fastapi import HTTPException, status, Depends
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.social_provider import SocialProvider
from app.auth.jwt_handler import create_access_token
from app.auth.utils import get_or_create_user_from_social
from app.core.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GoogleAuth:
    def __init__(self):
        settings = get_settings()
        self.client_id = settings.google_client_id
        # Allow initialization for testing even if credentials are not set
        if (not self.client_id or self.client_id == "your_google_client_id" or
            self.client_id == "mock_google_client_id"):
            # For testing, we'll allow initialization but mark as disabled
            self.enabled = False
        else:
            self.enabled = True
    
    async def verify_google_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Google ID token and return user info
        """
        try:
            logger.info("Verifying Google token")
            # Verify the token
            id_info = id_token.verify_oauth2_token(
                token, google_requests.Request(), self.client_id
            )
            
            # Check if token is from correct audience
            if id_info['aud'] != self.client_id:
                logger.warning("Invalid audience in Google token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid audience in Google token"
                )
            
            logger.info(f"Google token verified for user: {id_info.get('email')}")
            return {
                "provider_user_id": id_info['sub'],
                "email": id_info.get('email'),
                "email_verified": id_info.get('email_verified', False),
                "display_name": id_info.get('name'),
                "profile_picture": id_info.get('picture'),
                "provider_data": id_info
            }
            
        except ValueError as e:
            logger.error(f"Invalid Google token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error verifying Google token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error verifying Google token: {str(e)}"
            )
    
    async def authenticate_google_user(
        self, 
        token: str, 
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """
        Authenticate user with Google token and return JWT
        """
        try:
            logger.info("Authenticating Google user")
            # Verify Google token
            google_user_info = await self.verify_google_token(token)
            
            # Get or create user from social provider
            user, is_new_user = await get_or_create_user_from_social(
                db=db,
                provider="google",
                provider_user_id=google_user_info["provider_user_id"],
                email=google_user_info["email"],
                display_name=google_user_info["display_name"],
                profile_picture=google_user_info["profile_picture"],
                provider_data=google_user_info["provider_data"],
                email_verified=google_user_info["email_verified"]
            )
            
            logger.info(f"User {'created' if is_new_user else 'authenticated'}: {user.email}")
            
            # Create JWT token
            access_token = create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "username": user.username
                }
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "display_name": user.display_name,
                    "avatar_url": user.avatar_url,
                    "is_verified": user.is_verified,
                    "is_premium": user.is_premium
                },
                "is_new_user": is_new_user
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error authenticating Google user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error authenticating Google user: {str(e)}"
            )

# Create global instance
google_auth = GoogleAuth()
