from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.post import Post
from app.models.user import User
from sqlalchemy import desc, func

router = APIRouter(prefix="/api/football", tags=["football"])

@router.get("/")
async def get_football(
    skip: int = 0,
    limit: int = 20,
    league: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get real football data with pagination and filtering"""
    query = db.query(Post).filter(Post.category == "sports")
    
    if search:
        query = query.filter(Post.content.contains(search))
    
    matches = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    return {
        "matches": [
            {
                "id": match.id,
                "title": match.content.split("\n")[0],
                "description": match.content,
                "image_url": match.image_url,
                "category": match.category,
                "created_at": match.created_at.isoformat(),
                "user": {
                    "id": match.user.id,
                    "username": match.user.username,
                    "avatar_url": match.user.avatar_url
                },
                "likes": match.likes_count
            }
            for match in matches
        ],
        "total": query.count()
    }

@router.get("/matches/today")
async def get_today_matches(db: Session = Depends(get_db)):
    """Get today's football matches"""
    matches = db.query(Post).filter(
        Post.category == "sports"
    ).order_by(
        desc(Post.created_at)
    ).limit(5).all()
    
    return {
        "matches": [
            {
                "id": match.id,
                "title": match.content.split("\n")[0],
                "description": match.content,
                "image_url": match.image_url,
                "created_at": match.created_at.isoformat()
            }
            for match in matches
        ]
    }

@router.get("/live")
async def get_live_matches(db: Session = Depends(get_db)):
    """Get live football matches"""
    matches = db.query(Post).filter(
        Post.category == "sports"
    ).order_by(
        desc(Post.created_at)
    ).limit(3).all()
    
    return {
        "matches": [
            {
                "id": match.id,
                "title": match.content.split("\n")[0],
                "status": "live",
                "image_url": match.image_url
            }
            for match in matches
        ]
    }
