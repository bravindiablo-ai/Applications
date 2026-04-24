from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/notifications")
def get_notifications():
    now = datetime.utcnow().isoformat()
    return {
        "notifications": [
            {"id": 1, "type": "like", "title": "New like", "message": "Alice liked your post", "created_at": now, "is_read": False},
            {"id": 2, "type": "comment", "title": "New comment", "message": "Bob commented: Nice!", "created_at": now, "is_read": False},
            {"id": 3, "type": "follow", "title": "New follower", "message": "Charlie started following you", "created_at": now, "is_read": True},
        ]
    }
