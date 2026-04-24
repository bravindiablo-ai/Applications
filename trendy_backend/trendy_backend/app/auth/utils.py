"""
Utility functions for social authentication
"""

import json
from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.social_provider import SocialProvider

async def get_or_create_user_from_social(
    db: Session,
    provider: str,
    provider_user_id: str,
    email: Optional[str] = None,
    display_name: Optional[str] = None,
    profile_picture: Optional[str] = None,
    provider_data: Optional[Dict[str, Any]] = None,
    email_verified: bool = False
) -> Tuple[User, bool]:
    """
    Get existing user or create new user from social provider data
    Returns tuple of (user, is_new_user)
    """
    try:
        # First, check if social provider association exists
        social_provider = db.query(SocialProvider).filter(
            SocialProvider.provider == provider,
            SocialProvider.provider_user_id == provider_user_id
        ).first()
        
        if social_provider:
            # User exists, return the user
            return social_provider.user, False
        
        # Check if user with email exists
        user = None
        if email:
            user = db.query(User).filter(User.email == email).first()
        
        if user:
            # User exists but no social provider association, create it
            social_provider = SocialProvider(
                user_id=user.id,
                provider=provider,
                provider_user_id=provider_user_id,
                email=email,
                display_name=display_name,
                profile_picture=profile_picture,
                provider_data=json.dumps(provider_data) if provider_data else None
            )
            db.add(social_provider)
            
            # Update user flags
            user.has_social_login = True
            user.primary_social_provider = provider
            if not user.is_verified and email_verified:
                user.is_verified = True
            if profile_picture and not user.avatar_url:
                user.avatar_url = profile_picture
            if display_name and not user.display_name:
                user.display_name = display_name
                
            db.commit()
            return user, False
        
        # Create new user in database
        username = generate_username_from_email(email) if email else f"{provider}_{provider_user_id}"
        user = User(
            email=email or f"{provider_user_id}@{provider}.com",
            username=username,
            display_name=display_name or username,
            avatar_url=profile_picture,
            is_verified=email_verified,
            has_social_login=True,
            primary_social_provider=provider
        )
        db.add(user)
        db.flush()  # Flush to get user ID
        
        # Create social provider association
        social_provider = SocialProvider(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            display_name=display_name,
            profile_picture=profile_picture,
            provider_data=json.dumps(provider_data) if provider_data else None
        )
        db.add(social_provider)
        
        db.commit()
        return user, True
        
    except IntegrityError:
        db.rollback()
        # Handle race condition - user might have been created by another process
        social_provider = db.query(SocialProvider).filter(
            SocialProvider.provider == provider,
            SocialProvider.provider_user_id == provider_user_id
        ).first()
        if social_provider:
            return social_provider.user, False
        raise
    except Exception as e:
        db.rollback()
        raise e

def generate_username_from_email(email: str) -> str:
    """
    Generate a username from email address
    """
    if not email:
        return "user"
    
    # Extract username part from email
    username_part = email.split('@')[0]
    
    # Remove special characters and make lowercase
    username = ''.join(c for c in username_part if c.isalnum()).lower()
    
    # Ensure username is not empty
    if not username:
        username = "user"
    
    # Add random suffix if needed to ensure uniqueness
    # In practice, you'd check for uniqueness in database
    return username

async def link_social_provider_to_existing_user(
    db: Session,
    user_id: int,
    provider: str,
    provider_user_id: str,
    email: Optional[str] = None,
    display_name: Optional[str] = None,
    profile_picture: Optional[str] = None,
    provider_data: Optional[Dict[str, Any]] = None
) -> SocialProvider:
    """
    Link a social provider to an existing user account
    """
    # Check if provider association already exists
    existing = db.query(SocialProvider).filter(
        SocialProvider.provider == provider,
        SocialProvider.provider_user_id == provider_user_id
    ).first()
    
    if existing:
        return existing
    
    # Create new association
    social_provider = SocialProvider(
        user_id=user_id,
        provider=provider,
        provider_user_id=provider_user_id,
        email=email,
        display_name=display_name,
        profile_picture=profile_picture,
        provider_data=json.dumps(provider_data) if provider_data else None
    )
    
    db.add(social_provider)
    
    # Update user flags
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.has_social_login = True
        if not user.primary_social_provider:
            user.primary_social_provider = provider
    
    db.commit()
    return social_provider

async def unlink_social_provider(
    db: Session,
    user_id: int,
    provider: str
) -> bool:
    """
    Unlink a social provider from user account
    """
    social_provider = db.query(SocialProvider).filter(
        SocialProvider.user_id == user_id,
        SocialProvider.provider == provider
    ).first()
    
    if not social_provider:
        return False
    
    db.delete(social_provider)
    
    # Update user flags if this was the last social provider
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        remaining_providers = db.query(SocialProvider).filter(
            SocialProvider.user_id == user_id
        ).count()
        
        if remaining_providers == 0:
            user.has_social_login = False
            user.primary_social_provider = None
    
    db.commit()
    return True
