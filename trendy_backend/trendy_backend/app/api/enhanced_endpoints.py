from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..database import get_db
from ..models.enhanced_user import EnhancedUser
from ..models.enhanced_post import EnhancedPost

router = APIRouter(prefix="/api/v2", tags=["enhanced"])

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    bio: Optional[str] = None

class PostCreate(BaseModel):
    user_id: int
    post_type: str = "text"
    content: Optional[str] = None
    media_urls: Optional[List[str]] = None
    is_reel: bool = False
    is_story: bool = False
    is_tweet: bool = False
    location_name: Optional[str] = None
    spotify_track_id: Optional[str] = None

class PostResponse(BaseModel):
    id: int
    user_id: int
    post_type: str
    content: Optional[str]
    media_urls: Optional[List[str]]
    likes_count: int
    comments_count: int
    shares_count: int
    views_count: int
    created_at: datetime

@router.post("/users", response_model=dict)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new enhanced user with all social media features"""
    db_user = EnhancedUser(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "message": "User created successfully"}

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user profile with all social media integrations"""
    user = db.query(EnhancedUser).filter(EnhancedUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/posts", response_model=dict)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """Create a post with all social media features"""
    db_post = EnhancedPost(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {"id": db_post.id, "message": "Post created successfully"}

@router.get("/posts", response_model=List[dict])
async def get_posts(
    skip: int = 0,
    limit: int = 20,
    post_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get posts with filtering by type"""
    query = db.query(EnhancedPost)
    if post_type and post_type != 'all':
        query = query.filter(EnhancedPost.post_type == post_type)
    posts = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": post.id,
            "user_id": post.user_id,
            "post_type": post.post_type,
            "content": post.content,
            "media_urls": post.media_urls,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "shares_count": post.shares_count,
            "views_count": post.views_count,
            "created_at": post.created_at
        }
        for post in posts
    ]

@router.get("/posts/trending")
async def get_trending_posts(db: Session = Depends(get_db)):
    """Get trending posts across all platforms"""
    posts = db.query(EnhancedPost).filter(
        EnhancedPost.is_published == True
    ).order_by(
        EnhancedPost.views_count.desc(),
        EnhancedPost.likes_count.desc()
    ).limit(50).all()
    
    return [
        {
            "id": post.id,
            "user_id": post.user_id,
            "post_type": post.post_type,
            "content": post.content,
            "media_urls": post.media_urls,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "shares_count": post.shares_count,
            "views_count": post.views_count,
            "created_at": post.created_at
        }
        for post in posts
    ]

@router.post("/posts/{post_id}/like")
async def like_post(post_id: int, db: Session = Depends(get_db)):
    """Like a post (works for all post types)"""
    post = db.query(EnhancedPost).filter(EnhancedPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.likes_count += 1
    db.commit()
    return {"message": "Post liked successfully"}

@router.get("/users/{user_id}/analytics")
async def get_user_analytics(user_id: int, db: Session = Depends(get_db)):
    """Get comprehensive analytics for creators"""
    user = db.query(EnhancedUser).filter(EnhancedUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    posts = db.query(EnhancedPost).filter(EnhancedPost.user_id == user_id).all()
    
    analytics = {
        "total_posts": len(posts),
        "total_likes": sum(post.likes_count for post in posts),
        "total_comments": sum(post.comments_count for post in posts),
        "total_shares": sum(post.shares_count for post in posts),
        "total_views": sum(post.views_count for post in posts),
        "total_earnings": sum(post.earnings for post in posts),
        "post_breakdown": {
            "text_posts": len([p for p in posts if p.post_type == "text"]),
            "image_posts": len([p for p in posts if p.post_type == "image"]),
            "video_posts": len([p for p in posts if p.post_type == "video"]),
            "reels": len([p for p in posts if p.is_reel]),
            "stories": len([p for p in posts if p.is_story]),
            "tweets": len([p for p in posts if p.is_tweet])
        }
    }
    return analytics

@router.get("/spotify/connect")
async def connect_spotify(user_id: int, spotify_user_id: str, db: Session = Depends(get_db)):
    """Connect Spotify account to user profile"""
    user = db.query(EnhancedUser).filter(EnhancedUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.spotify_connected = True
    user.spotify_user_id = spotify_user_id
    db.commit()
    return {"message": "Spotify account connected successfully"}

@router.get("/tiktok/enable")
async def enable_tiktok_creator(user_id: int, db: Session = Depends(get_db)):
    """Enable TikTok creator features for user"""
    user = db.query(EnhancedUser).filter(EnhancedUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_tiktok_creator = True
    db.commit()
    return {"message": "TikTok creator features enabled"}

@router.get("/instagram/stories")
async def get_instagram_stories(user_id: int, db: Session = Depends(get_db)):
    """Get Instagram-style stories for user"""
    stories = db.query(EnhancedPost).filter(
        EnhancedPost.user_id == user_id,
        EnhancedPost.is_story == True,
        EnhancedPost.is_published == True
    ).order_by(EnhancedPost.created_at.desc()).all()
    
    return stories

@router.get("/twitter/timeline")
async def get_twitter_timeline(user_id: int, db: Session = Depends(get_db)):
    """Get Twitter-style timeline for user"""
    tweets = db.query(EnhancedPost).filter(
        EnhancedPost.is_tweet == True,
        EnhancedPost.is_published == True
    ).order_by(EnhancedPost.created_at.desc()).limit(50).all()
    
    return tweets

@router.get("/facebook/feed")
async def get_facebook_feed(user_id: int, db: Session = Depends(get_db)):
    """Get Facebook-style feed for user"""
    posts = db.query(EnhancedPost).filter(
        EnhancedPost.is_facebook_post == True,
        EnhancedPost.is_published == True
    ).order_by(EnhancedPost.created_at.desc()).limit(50).all()
    
    return posts

@router.post("/posts/{post_id}/monetize")
async def monetize_post(post_id: int, price: float, db: Session = Depends(get_db)):
    """Monetize a post with pay-per-view"""
    post = db.query(EnhancedPost).filter(EnhancedPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post.is_monetized = True
    post.price = price
    db.commit()
    return {"message": "Post monetized successfully"}

@router.get("/search")
async def search_posts(query: str, db: Session = Depends(get_db)):
    """Search posts across all platforms"""
    posts = db.query(EnhancedPost).filter(
        EnhancedPost.content.contains(query),
        EnhancedPost.is_published == True
    ).order_by(EnhancedPost.created_at.desc()).limit(20).all()
    
    return posts
