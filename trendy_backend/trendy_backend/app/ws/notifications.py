from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: dict):
        for conn in list(self.active):
            try:
                await conn.send_json(message)
            except:
                try:
                    conn.close()
                except:
                    pass

manager = ConnectionManager()

@router.websocket("/ws/notifications")
async def websocket_notifications(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            # echo for now
            await manager.broadcast({"type":"message","payload":data})
    except WebSocketDisconnect:
        manager.disconnect(ws)
