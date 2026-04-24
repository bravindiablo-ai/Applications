"""
Authentication schemas for TRENDY App
Contains Pydantic models for authentication requests and responses
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any

class AuthResponse(BaseModel):
    """Base authentication response schema"""
    access_token: str
    token_type: str
    user_id: int
    email: str
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool = False

class GoogleLoginRequest(BaseModel):
    """Google OAuth login request schema"""
    token: str

class FacebookLoginRequest(BaseModel):
    """Facebook OAuth login request schema"""
    token: str

class AppleLoginRequest(BaseModel):
    """Apple Sign-In login request schema"""
    token: str
    user_identifier: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None

class EmailLoginRequest(BaseModel):
    """Email/password login request schema"""
    email: EmailStr
    password: str

class EmailRegisterRequest(BaseModel):
    """Email registration request schema"""
    email: EmailStr
    password: str
    username: str
    display_name: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""
    token: str
    new_password: str

class VerifyEmailRequest(BaseModel):
    """Email verification request schema"""
    token: str

class SocialProviderConfig(BaseModel):
    """Social provider configuration schema"""
    client_id: str
    auth_uri: str
    token_uri: str
    scope: str
    redirect_uri: str

class AuthConfigResponse(BaseModel):
    """Authentication configuration response"""
    google: Optional[SocialProviderConfig] = None
    facebook: Optional[SocialProviderConfig] = None
    apple: Optional[SocialProviderConfig] = None

class TokenRefreshRequest(BaseModel):
    """Token refresh request schema"""
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    """Token refresh response schema"""
    access_token: str
    token_type: str
    expires_in: int

class LogoutRequest(BaseModel):
    """Logout request schema"""
    refresh_token: Optional[str] = None

class AuthErrorResponse(BaseModel):
    """Authentication error response schema"""
    error: str
    error_description: Optional[str] = None
    error_uri: Optional[str] = None

class UserSession(BaseModel):
    """User session information schema"""
    user_id: int
    email: str
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool
    is_premium: bool
    permissions: Dict[str, bool] = {}
    session_expires_at: int

class SocialAccountLink(BaseModel):
    """Social account linking information"""
    provider: str
    provider_user_id: str
    email: str
    connected_at: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

class LinkedAccountsResponse(BaseModel):
    """Linked social accounts response"""
    accounts: list[SocialAccountLink]
    can_disconnect: bool
