from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.post import Post
from app.models.user import User
from sqlalchemy import desc, func

router = APIRouter(prefix="/api/movies", tags=["movies"])

@router.get("/")
async def get_movies(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get real movie data with pagination and filtering"""
    query = db.query(Post).filter(Post.category == "movies")
    
    if search:
        query = query.filter(Post.content.contains(search))
    
    movies = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    return {
        "movies": [
            {
                "id": movie.id,
                "title": movie.content.split("\n")[0],  # First line is title
                "description": movie.content,
                "image_url": movie.image_url,
                "category": movie.category,
                "created_at": movie.created_at.isoformat(),
                "user": {
                    "id": movie.user.id,
                    "username": movie.user.username,
                    "avatar_url": movie.user.avatar_url
                },
                "likes": movie.likes_count,
                "comments": len(movie.comments)
            }
            for movie in movies
        ],
        "total": query.count()
    }

@router.get("/trending")
async def get_trending_movies(db: Session = Depends(get_db)):
    """Get trending movies based on likes and views"""
    movies = db.query(Post).filter(
        Post.category == "movies"
    ).order_by(
        desc(Post.likes_count),
        desc(Post.created_at)
    ).limit(10).all()
    
    return {
        "movies": [
            {
                "id": movie.id,
                "title": movie.content.split("\n")[0],
                "description": movie.content,
                "image_url": movie.image_url,
                "likes": movie.likes_count,
                "views": movie.views_count,
                "user": {
                    "id": movie.user.id,
                    "username": movie.user.username
                }
            }
            for movie in movies
        ]
    }

@router.get("/{movie_id}")
async def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    """Get detailed movie information"""
    movie = db.query(Post).filter(Post.id == movie_id, Post.category == "movies").first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return {
        "id": movie.id,
        "title": movie.content.split("\n")[0],
        "description": movie.content,
        "image_url": movie.image_url,
        "category": movie.category,
        "created_at": movie.created_at.isoformat(),
        "user": {
            "id": movie.user.id,
            "username": movie.user.username,
            "avatar_url": movie.user.avatar_url
        },
        "likes": movie.likes_count,
        "comments": [
            {
                "id": comment.id,
                "content": comment.text,
                "created_at": comment.created_at.isoformat(),
                "user": {
                    "id": comment.owner.id,
                    "username": comment.owner.username
                }
            }
            for comment in movie.comments
        ]
    }
