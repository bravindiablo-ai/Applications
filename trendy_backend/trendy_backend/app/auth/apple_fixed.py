"""
Apple Sign-In Implementation for TRENDY App
Fixed version with proper JWT verification
"""

import logging
import os
import jwt
import httpx
from typing import Dict, Any
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.social_provider import SocialProvider
from app.auth.jwt_handler import create_access_token
from app.auth.utils import get_or_create_user_from_social

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class AppleAuth:
    def __init__(self):
        self.client_id = os.getenv("APPLE_CLIENT_ID", "mock_apple_client_id")
        self.team_id = os.getenv("APPLE_TEAM_ID", "mock_apple_team_id")
        self.key_id = os.getenv("APPLE_KEY_ID", "mock_apple_key_id")
        self.private_key = os.getenv("APPLE_PRIVATE_KEY", "mock_apple_private_key")
    
    async def get_apple_public_keys(self):
        """Get Apple's public keys for JWT verification"""
        try:
            logger.info("Fetching Apple public keys")
            async with httpx.AsyncClient() as client:
                response = await client.get("https://appleid.apple.com/auth/keys")
                return response.json()["keys"]
        except Exception as e:
            logger.error(f"Failed to fetch Apple public keys: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch Apple public keys: {str(e)}"
            )
    
    async def verify_apple_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Apple ID token and return user info using JWT verification
        """
        try:
            logger.info("Verifying Apple token")
            # Get Apple's public keys
            public_keys = await self.get_apple_public_keys()
            
            # Try to verify the token with each key
            for key in public_keys:
                try:
                    # Verify the JWT token
                    decoded = jwt.decode(
                        token,
                        key,
                        algorithms=["RS256"],
                        audience=self.client_id,
                        issuer="https://appleid.apple.com"
                    )
                    
                    logger.info(f"Apple token verified for user: {decoded.get('email')}")
                    return {
                        "provider_user_id": decoded["sub"],
                        "email": decoded.get("email"),
                        "display_name": decoded.get("name"),
                        "provider_data": decoded
                    }
                    
                except jwt.InvalidTokenError:
                    continue
            
            # If none of the keys worked, the token is invalid
            logger.warning("Invalid Apple token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Apple token"
            )
            
        except Exception as e:
            logger.error(f"Error verifying Apple token: {str(e)}")
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
            logger.info("Authenticating Apple user")
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
            logger.error(f"Error authenticating Apple user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error authenticating Apple user: {str(e)}"
            )

# Create global instance
apple_auth = AppleAuth()
