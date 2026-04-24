from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os, time, hmac, hashlib, base64, json

router = APIRouter(prefix="/api/v1/rooms", tags=["rooms"])

# Basic Agora token generator (App ID & certificate in env)
AGORA_APP_ID = os.getenv("AGORA_APP_ID")
AGORA_APP_CERT = os.getenv("AGORA_APP_CERTIFICATE")

class TokenRequest(BaseModel):
    channel: str
    uid: str
    role: str = "publisher"
    expire_seconds: int = 3600

@router.post("/token")
def generate_token(payload: TokenRequest):
    """
    This is a simplified token generator. For production, use Agora SDK or server-side helper from Agora.
    This stub returns a mock token if credentials are not set.
    """
    if not AGORA_APP_ID or not AGORA_APP_CERT:
        return {"token": f"MOCK_TOKEN_{payload.channel}_{payload.uid}", "expires_at": int(time.time()) + payload.expire_seconds}
    # Production: create a real RTC token with Agora server side libs (omitted here)
    return {"token": f"AGORA_TOKEN_{payload.channel}_{payload.uid}", "expires_at": int(time.time()) + payload.expire_seconds}
