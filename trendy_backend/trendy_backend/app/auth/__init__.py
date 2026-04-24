"""
Authentication package for TRENDY App
Includes JWT handling, social authentication, and email verification
"""

from .jwt_handler import create_access_token, decode_token
from .social_auth import router as social_auth_router
from .email_verification import router as email_verification_router
from .facebook import FacebookAuth
from .google import GoogleAuth

# Export the main router for easy import
router = social_auth_router

__all__ = [
    'create_access_token',
    'decode_token',
    'social_auth_router',
    'email_verification_router',
    'FacebookAuth',
    'GoogleAuth',
    'router'
]
