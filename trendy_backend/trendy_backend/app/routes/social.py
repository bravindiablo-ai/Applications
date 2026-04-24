from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from sqlalchemy.orm import Session
from app.services.social_service import follow_user, unfollow_user, get_followers
from app.services.user_sync import get_current_user

router = APIRouter(prefix="/api/v1/social", tags=["social"])

@router.post("/follow/{user_id}")
def follow(user_id: str, db: Session = Depends(get_db), me=Depends(get_current_user)):
    if not me:
        raise HTTPException(401, "Auth required")
    return follow_user(db, str(me.id), user_id)

@router.post("/unfollow/{user_id}")
def unfollow(user_id: str, db: Session = Depends(get_db), me=Depends(get_current_user)):
    if not me:
        raise HTTPException(401, "Auth required")
    return unfollow_user(db, str(me.id), user_id)

@router.get("/followers/{user_id}")
def followers(user_id: str, db: Session = Depends(get_db), limit: int = 50):
    return get_followers(db, user_id, limit=limit)
