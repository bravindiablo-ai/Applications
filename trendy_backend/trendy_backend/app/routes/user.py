from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import logging
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.auth.middleware import get_current_user
from pydantic import BaseModel

router = APIRouter()

logger = logging.getLogger(__name__)

class UserLogin(BaseModel):
    identifier: str  # can be email or username
    password: str

# Registration and login are handled by Firebase authentication
# These endpoints are deprecated and will be removed in future versions

@router.get("/welcome")
def welcome(request: Request):
    """
    Returns a welcome message and logs request metadata.
    """
    logger.info(f"Request received: {request.method} {request.url.path}")
    return {"message": "Welcome to the TRENDY API Service!"}

@router.get("/me", response_model=UserResponse)
def get_me(db: Session = Depends(get_db), user_id=Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/posts")
def get_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get user posts with pagination - matches Flutter client expectations"""
    from app.models.post import Post
    from sqlalchemy import desc
    
    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Query posts with pagination
    query = db.query(Post).filter(Post.user_id == user_id)
    total = query.count()
    posts = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    return {
        "posts": [
            {
                "id": post.id,
                "content": post.content,
                "image_url": post.image_url,
                "created_at": post.created_at.isoformat(),
                "user": {
                    "id": post.user.id,
                    "username": post.user.username
                },
                "likes": len(post.comments),
                "comments": len(post.comments)
            }
            for post in posts
        ],
        "total": total
    }
