"""
Apple Sign-In Implementation for TRENDY App
"""

import os
import httpx
from typing import Dict, Any
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.social_provider import SocialProvider
from app.auth.jwt_handler import create_access_token
from app.auth.utils import get_or_create_user_from_social

class AppleAuth:
    def __init__(self):
        self.client_id = os.getenv("APPLE_CLIENT_ID")
        self.team_id = os.getenv("APPLE_TEAM_ID")
        self.key_id = os.getenv("APPLE_KEY_ID")
        self.private_key = os.getenv("APPLE_PRIVATE_KEY")
        if not all([self.client_id, self.team_id, self.key_id, self.private_key]):
            raise ValueError("Apple OAuth credentials not set")
    
    async def verify_apple_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Apple ID token and return user info
        """
        try:
            # Verify the token with Apple
            url = "https://appleid.apple.com/auth/verify"
            headers = {"Content-Type": "application/json"}
            payload = {
                "id_token": token,
                "client_id": self.client_id,
                "client_secret": self.private_key,
                "team_id": self.team_id,
                "key_id": self.key_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                user_info = response.json()
            
            if response.status_code != 200 or "error" in user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Apple token"
                )
            
            return {
                "provider_user_id": user_info["sub"],
                "email": user_info.get("email"),
                "display_name": user_info.get("name"),
                "provider_data": user_info
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error verifying Apple token: {str(e)}"
            )
    
    async def authenticate_apple_user(
        self, 
        token: str, 
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """
        Authenticate user with Apple token and return JWT
        """
        try:
            # Verify Apple token
            apple_user_info = await self.verify_apple_token(token)
            
            # Get or create user from social provider
            user, is_new_user = await get_or_create_user_from_social(
                db=db,
                provider="apple",
                provider_user_id=apple_user_info["provider_user_id"],
                email=apple_user_info["email"],
                display_name=apple_user_info["display_name"],
                provider_data=apple_user_info["provider_data"],
                email_verified=True  # Apple emails are typically verified
            )
            
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error authenticating Apple user: {str(e)}"
            )

# Create global instance
apple_auth = AppleAuth()
