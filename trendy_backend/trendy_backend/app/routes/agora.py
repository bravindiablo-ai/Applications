from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import os
from app.auth.middleware import verify_firebase_token
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

# Agora configuration
AGORA_APP_ID = os.getenv("AGORA_APP_ID") or settings.agora_app_id
AGORA_APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE") or settings.agora_app_certificate

class TokenRequest(BaseModel):
    channel_name: str
    uid: int

@router.post("/agora/token")
async def generate_agora_token(request: TokenRequest, authorization: Optional[str] = Header(default=None)):
    """Generate Agora token for voice/video calls and live streaming. Accepts any Bearer token (e.g., Firebase) in dev."""
    try:
        # Optional: validate provided bearer token in development
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ", 1)[1]
            # Verify Firebase token
            await verify_firebase_token(token)
        
        # Check if Agora credentials are configured
        if not AGORA_APP_ID or not AGORA_APP_CERTIFICATE:
            raise HTTPException(status_code=500, detail="Agora credentials not configured")
        
        # Import Agora token builder
        from agora_token_builder import RtcTokenBuilder
        
        # Generate token with 24-hour expiration
        expiration_time_in_seconds = 3600 * 24
        current_timestamp = int(os.environ.get("CURRENT_TIMESTAMP", "0"))
        privilege_expired_ts = current_timestamp + expiration_time_in_seconds
        
        # Generate RTC token
        token = RtcTokenBuilder.buildTokenWithUid(
            AGORA_APP_ID,
            AGORA_APP_CERTIFICATE,
            request.channel_name,
            request.uid,
            1,  # Role_Publisher = 1
            privilege_expired_ts
        )
        
        return {"token": token}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate token: {str(e)}")
