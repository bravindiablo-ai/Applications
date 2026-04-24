import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pydantic import BaseModel
import time

# Initialize FastAPI with CORS
app = FastAPI(title="Trendy API Verification")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# Trends discover endpoint
@app.get("/api/v1/trends/discover")
async def trends_discover():
    return {
        "trends": [
            {"id": "1", "name": "Summer2025", "count": 1500},
            {"id": "2", "name": "TrendyVibes", "count": 1200}
        ]
    }

# AI recommend endpoint
@app.post("/api/v1/ai/recommend")
async def ai_recommend(request: dict):
    return {
        "recommendations": [
            {"id": "1", "type": "video", "title": "Summer fun"},
            {"id": "2", "type": "music", "title": "Chill vibes"}
        ]
    }

# Agora token endpoint
class TokenRequest(BaseModel):
    channel: str
    uid: str
    role: str = "publisher"
    expire_seconds: int = 3600

@app.post("/api/v1/rooms/token")
async def get_token(req: TokenRequest):
    AGORA_APP_ID = os.getenv("AGORA_APP_ID")
    AGORA_APP_CERT = os.getenv("AGORA_APP_CERTIFICATE")
    if not AGORA_APP_ID or not AGORA_APP_CERT:
        return {"token": f"MOCK_TOKEN_{req.channel}_{req.uid}", "expires_at": int(time.time()) + req.expire_seconds}
    return {"token": f"AGORA_TOKEN_{req.channel}_{req.uid}", "expires_at": int(time.time()) + req.expire_seconds}

# Stripe webhook endpoint
@app.post("/api/v1/payments/stripe/webhook")
async def stripe_webhook():
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    if not STRIPE_SECRET_KEY:
        return {"error": "Stripe key not configured"}
    return {"received": True, "timestamp": time.time()}

# WebSocket chat endpoint
@app.websocket("/ws/chat/public")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except Exception:
        pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)