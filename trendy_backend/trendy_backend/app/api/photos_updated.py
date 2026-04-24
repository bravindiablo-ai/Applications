from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.post import Post
from app.models.user import User
from sqlalchemy import desc, func

router = APIRouter(prefix="/api/photos", tags=["photos"])

@router.get("/")
async def get_photos(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get real photography data with pagination and filtering"""
    query = db.query(Post).filter(Post.category == "photography")
    
    if search:
        query = query.filter(Post.content.contains(search))
    
    photos = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    return {
        "photos": [
            {
                "id": photo.id,
                "title": photo.content.split("\n")[0],
                "description": photo.content,
                "image_url": photo.image_url,
                "category": photo.category,
                "created_at": photo.created_at.isoformat(),
                "user": {
                    "id": photo.user.id,
                    "username": photo.user.username,
                    "avatar_url": photo.user.avatar_url
                },
                "likes": photo.likes_count,
                "trending_score": photo.likes_count + photo.views_count
            }
            for photo in photos
        ],
        "total": query.count()
    }

@router.get("/trending")
async def get_trending_photos(db: Session = Depends(get_db)):
    """Get trending photos based on engagement"""
    photos = db.query(Post).filter(
        Post.category == "photography"
    ).order_by(
        desc(Post.likes_count),
        desc(Post.created_at)
    ).limit(10).all()
    
    return {
        "photos": [
            {
                "id": photo.id,
                "title": photo.content.split("\n")[0],
                "image_url": photo.image_url,
                "trending_score": photo.likes_count + photo.views_count,
                "user": {
                    "id": photo.user.id,
                    "username": photo.user.username
                }
            }
            for photo in photos
        ]
    }

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get unique photography categories"""
    categories = db.query(Post.category).filter(Post.category == "photography").distinct().all()
    return {"categories": [c[0] for c in categories]}
