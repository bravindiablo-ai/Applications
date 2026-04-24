import json
import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from app.services.movie_service import MovieService
from app.auth.middleware import get_current_user  # Assuming this exists for token verification
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)

class WatchPartyConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # party_code -> list of websockets
        self.user_to_party: Dict[int, str] = {}  # user_profile_id -> party_code

    async def connect(self, party_code: str, user_profile_id: int, websocket: WebSocket):
        await websocket.accept()
        if party_code not in self.active_connections:
            self.active_connections[party_code] = []
        self.active_connections[party_code].append(websocket)
        self.user_to_party[user_profile_id] = party_code

    def disconnect(self, user_profile_id: int, websocket: WebSocket):
        party_code = self.user_to_party.get(user_profile_id)
        if party_code and party_code in self.active_connections:
            if websocket in self.active_connections[party_code]:
                self.active_connections[party_code].remove(websocket)
            if not self.active_connections[party_code]:
                del self.active_connections[party_code]
        if user_profile_id in self.user_to_party:
            del self.user_to_party[user_profile_id]

    async def broadcast_to_party(self, party_code: str, message: dict, exclude_user: Optional[int] = None):
        if party_code not in self.active_connections:
            return
        for conn in list(self.active_connections[party_code]):
            try:
                if exclude_user and self._get_user_from_conn(conn) == exclude_user:
                    continue
                await conn.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to party {party_code}: {e}")
                try:
                    await conn.close()
                except:
                    pass

    async def send_to_user(self, user_profile_id: int, message: dict):
        party_code = self.user_to_party.get(user_profile_id)
        if not party_code or party_code not in self.active_connections:
            return
        for conn in list(self.active_connections[party_code]):
            if self._get_user_from_conn(conn) == user_profile_id:
                try:
                    await conn.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_profile_id}: {e}")
                break

    def get_party_participants(self, party_code: str) -> List[int]:
        if party_code not in self.active_connections:
            return []
        return [self._get_user_from_conn(conn) for conn in self.active_connections[party_code]]

    def _get_user_from_conn(self, websocket: WebSocket) -> Optional[int]:
        # This is a placeholder; in practice, you'd store user_id with the websocket
        # For now, assume we can retrieve it from the websocket object or a mapping
        # You might need to modify this based on how you store user info
        return getattr(websocket, 'user_profile_id', None)

manager = WatchPartyConnectionManager()

@router.websocket("/ws/watch-party/{party_code}")
async def watch_party_websocket(
    websocket: WebSocket,
    party_code: str,
    profile_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    # Authenticate user via token
    try:
        user = await get_current_user(token)  # Assuming this function verifies Firebase token
    except Exception as e:
        await websocket.close(code=1008)  # Policy violation
        return

    movie_service = MovieService(db)

    # Validate party exists and user has access
    try:
        party = movie_service.get_watch_party(party_code)
        if not party:
            await websocket.close(code=1008)
            return
        # Check if user is participant
        participant = next((p for p in party.participants if p.user_profile_id == profile_id), None)
        if not participant:
            await websocket.close(code=1008)
            return
    except Exception as e:
        logger.error(f"Error validating party {party_code}: {e}")
        await websocket.close(code=1011)  # Internal error
        return

    # Set user_profile_id on websocket for later retrieval
    websocket.user_profile_id = profile_id

    await manager.connect(party_code, profile_id, websocket)

    # Send initial state
    try:
        initial_state = {
            "type": "initial_state",
            "party_code": party_code,
            "current_position_seconds": party.current_position_seconds,
            "status": party.status,
            "participants": [{"profile_id": p.user_profile_id, "name": p.user_profile.profile_name} for p in party.participants if p.is_active]
        }
        await websocket.send_json(initial_state)
    except Exception as e:
        logger.error(f"Error sending initial state: {e}")

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_message(message, party_code, profile_id, movie_service, party)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await websocket.send_json({"type": "error", "message": "Internal error"})
    except WebSocketDisconnect:
        manager.disconnect(profile_id, websocket)
        # Update participant status
        try:
            movie_service.leave_watch_party(party.id, profile_id)
        except Exception as e:
            logger.error(f"Error updating participant status: {e}")
        # Broadcast leave event
        await manager.broadcast_to_party(party_code, {"type": "leave", "profile_id": profile_id}, exclude_user=profile_id)
        # If host disconnects, pause party
        if party.host_profile_id == profile_id:
            try:
                movie_service.update_watch_party_position(party.id, party.current_position_seconds, "paused")
                await manager.broadcast_to_party(party_code, {"type": "pause", "position": party.current_position_seconds})
            except Exception as e:
                logger.error(f"Error pausing party on host disconnect: {e}")

async def handle_message(message: dict, party_code: str, profile_id: int, movie_service: MovieService, party):
    msg_type = message.get("type")
    if not msg_type:
        return

    if msg_type == "join":
        # Already handled in connect
        pass
    elif msg_type == "leave":
        await manager.disconnect(profile_id, None)  # Disconnect will be handled in except block
        movie_service.leave_watch_party(party.id, profile_id)
        await manager.broadcast_to_party(party_code, {"type": "leave", "profile_id": profile_id}, exclude_user=profile_id)
    elif msg_type in ["play", "pause", "seek"]:
        # Check if user is host
        if party.host_profile_id != profile_id:
            await manager.send_to_user(profile_id, {"type": "error", "message": "Only host can control playback"})
            return
        position = message.get("position", party.current_position_seconds)
        movie_service.update_watch_party_position(party.id, position, msg_type)
        await manager.broadcast_to_party(party_code, {"type": msg_type, "position": position}, exclude_user=profile_id)
    elif msg_type == "sync_request":
        state = {
            "type": "sync_response",
            "current_position_seconds": party.current_position_seconds,
            "status": party.status
        }
        await manager.send_to_user(profile_id, state)
    elif msg_type == "chat":
        chat_msg = message.get("message", "")
        if chat_msg:
            await manager.broadcast_to_party(party_code, {"type": "chat", "profile_id": profile_id, "message": chat_msg})
    elif msg_type == "ping":
        await manager.send_to_user(profile_id, {"type": "pong"})
    else:
        await manager.send_to_user(profile_id, {"type": "error", "message": "Unknown message type"})