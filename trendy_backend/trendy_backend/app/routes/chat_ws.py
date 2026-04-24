from fastapi import APIRouter, WebSocket, WebSocketDisconnect
router = APIRouter()

# lightweight public chat WebSocket endpoint
@router.websocket("/ws/chat/public")
async def ws_chat_public(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            # echo in this simple implementation; production should route to rooms
            await ws.send_text(f"ECHO: {data}")
    except WebSocketDisconnect:
        try:
            await ws.close()
        except:
            pass
