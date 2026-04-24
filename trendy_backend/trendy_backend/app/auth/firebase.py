"""
Firebase Authentication Utilities for TRENDY App
DEPRECATED - Use app.auth.middleware instead for unified authentication
"""

import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import get_settings

settings = get_settings()

# Initialize Firebase Admin with error handling for missing credentials
if not firebase_admin._apps:
    try:
        if settings.firebase_credentials_json_path and os.path.exists(settings.firebase_credentials_json_path):
            cred = credentials.Certificate(settings.firebase_credentials_json_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin initialized successfully")
        else:
            print("⚠️  Firebase credentials not found. Firebase authentication will be disabled.")
            # Set a flag to indicate Firebase is not available
            firebase_available = False
    except Exception as e:
        print(f"⚠️  Failed to initialize Firebase: {e}")
        firebase_available = False

security = HTTPBearer()

async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify Firebase JWT token and return user info."""
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

async def get_current_user(token_data: dict = Depends(verify_firebase_token)) -> dict:
    """Get current authenticated user from Firebase token."""
    return {
        "uid": token_data["uid"],
        "email": token_data.get("email"),
        "name": token_data.get("name"),
        "picture": token_data.get("picture"),
    }

async def get_current_user_id(current_user: dict = Depends(get_current_user)) -> str:
    """Get current user ID from Firebase token."""
    return current_user["uid"]

async def get_current_user_email(current_user: dict = Depends(get_current_user)) -> str:
    """Get current user email from Firebase token."""
    return current_user["email"]
