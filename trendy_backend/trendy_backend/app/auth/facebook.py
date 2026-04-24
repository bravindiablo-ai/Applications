"""
Facebook OAuth Implementation for TRENDY App
"""

import logging
import httpx
from typing import Dict, Any
from fastapi import HTTPException, status, Depends
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

class FacebookAuth:
    def __init__(self):
        settings = get_settings()
        self.client_id = settings.facebook_client_id
        self.client_secret = settings.facebook_client_secret
        # Allow initialization for testing even if credentials are not set
        if (not self.client_id or not self.client_secret or 
            self.client_id == "your_facebook_client_id" or
            self.client_id == "mock_facebook_client_id"):
            # For testing, we'll allow initialization but mark as disabled
            self.enabled = False
        else:
            self.enabled = True
    
    async def verify_facebook_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Facebook access token and return user info
        """
        try:
            logger.info("Verifying Facebook token")
            # First, debug the token to get app ID and user ID
            debug_url = f"https://graph.facebook.com/debug_token"
            debug_params = {
                "input_token": token,
                "access_token": f"{self.client_id}|{self.client_secret}"
            }
            
            async with httpx.AsyncClient() as client:
                debug_response = await client.get(debug_url, params=debug_params)
                debug_data = debug_response.json()
            
            if debug_response.status_code != 200 or "error" in debug_data:
                logger.warning("Invalid Facebook token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Facebook token"
                )
            
            # Verify the token is for our app
            if debug_data["data"]["app_id"] != self.client_id:
                logger.warning("Token not issued for this application")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token not issued for this application"
                )
            
            # Get user info
            user_id = debug_data["data"]["user_id"]
            user_url = f"https://graph.facebook.com/{user_id}"
            user_params = {
                "fields": "id,name,email,picture.type(large)",
                "access_token": token
            }
            
            async with httpx.AsyncClient() as client:
                user_response = await client.get(user_url, params=user_params)
                user_data = user_response.json()
            
            if user_response.status_code != 200 or "error" in user_data:
                logger.warning("Failed to fetch Facebook user info")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to fetch Facebook user info"
                )
            
            logger.info(f"Facebook token verified for user: {user_data.get('email')}")
            return {
                "provider_user_id": user_data["id"],
                "email": user_data.get("email"),
                "display_name": user_data.get("name"),
                "profile_picture": user_data.get("picture", {}).get("data", {}).get("url"),
                "provider_data": user_data
            }
            
        except httpx.RequestError as e:
            logger.error(f"Network error verifying Facebook token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Network error verifying Facebook token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error verifying Facebook token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error verifying Facebook token: {str(e)}"
            )
    
    async def get_facebook_access_token(self, code: str, redirect_uri: str) -> str:
        """
        Exchange authorization code for access token
        """
        try:
            logger.info("Getting Facebook access token")
            token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
            token_params = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": redirect_uri
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(token_url, params=token_params)
                token_data = response.json()
            
            if response.status_code != 200 or "error" in token_data:
                logger.warning("Failed to exchange code for access token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to exchange code for access token"
                )
            
            logger.info("Facebook access token obtained successfully")
            return token_data["access_token"]
            
        except httpx.RequestError as e:
            logger.error(f"Network error getting Facebook access token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Network error getting Facebook access token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error getting Facebook access token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting Facebook access token: {str(e)}"
            )
    
    async def authenticate_facebook_user(
        self, 
        code: str, 
        redirect_uri: str,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """
        Authenticate user with Facebook OAuth code and return JWT
        """
        try:
            logger.info("Authenticating Facebook user")
            # Exchange code for access token
            access_token = await self.get_facebook_access_token(code, redirect_uri)
            
            # Verify token and get user info
            facebook_user_info = await self.verify_facebook_token(access_token)
            
            # Get or create user from social provider
            user, is_new_user = await get_or_create_user_from_social(
                db=db,
                provider="facebook",
                provider_user_id=facebook_user_info["provider_user_id"],
                email=facebook_user_info["email"],
                display_name=facebook_user_info["display_name"],
                profile_picture=facebook_user_info["profile_picture"],
                provider_data=facebook_user_info["provider_data"],
                email_verified=True  # Facebook emails are typically verified
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
            logger.error(f"Error authenticating Facebook user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error authenticating Facebook user: {str(e)}"
            )

# Create global instance
facebook_auth = FacebookAuth()
