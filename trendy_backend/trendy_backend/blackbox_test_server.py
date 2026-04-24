from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import time, os

app = FastAPI()


class TokenRequest(BaseModel):
    channel: str
    uid: str
    role: str = "publisher"
    expire_seconds: int = 3600


@app.post("/api/v1/ai/recommend")
def ai_recommend(payload: dict):
    return {"results": ["sample1", "sample2", "sample3"]}


@app.post("/api/v1/rooms/token")
def rooms_token(req: TokenRequest):
    AGORA_APP_ID = os.getenv("AGORA_APP_ID")
    AGORA_APP_CERT = os.getenv("AGORA_APP_CERTIFICATE")
    if not AGORA_APP_ID or not AGORA_APP_CERT:
        return {"token": f"MOCK_TOKEN_{req.channel}_{req.uid}", "expires_at": int(time.time()) + req.expire_seconds}
    return {"token": f"AGORA_TOKEN_{req.channel}_{req.uid}", "expires_at": int(time.time()) + req.expire_seconds}


@app.get("/api/v1/analytics/summary")
def analytics_summary():
    return {"users": 10, "posts": 5}


@app.post("/api/v1/payments/stripe/webhook")
def stripe_webhook():
    return {"received": True}


@app.websocket("/ws/chat/public")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            await ws.send_text(msg)
    except Exception:
        try:
            await ws.close()
        except Exception:
            pass


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
