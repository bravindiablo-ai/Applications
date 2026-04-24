from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.post import Post
from app.models.user import User
from sqlalchemy import desc, func, or_
from app.core.config import get_settings

router = APIRouter(prefix="/api/movies", tags=["movies"])

settings = get_settings()

# Mock data enhancements
MOCK_GENRES = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller", "Documentary", "Animation", "Adventure"]
MOCK_CAST = [
    {"name": "John Doe", "role": "Lead Actor"},
    {"name": "Jane Smith", "role": "Supporting Actress"},
    {"name": "Bob Johnson", "role": "Director"},
    {"name": "Alice Brown", "role": "Producer"},
    {"name": "Charlie Wilson", "role": "Writer"}
]
MOCK_CREW = [
    {"name": "Director Name", "job": "Director"},
    {"name": "Producer Name", "job": "Producer"},
    {"name": "Writer Name", "job": "Writer"},
    {"name": "Cinematographer Name", "job": "Cinematographer"}
]

def enhance_movie_response(movie, db):
    """Enhance movie response with mock data"""
    import random
    title = movie.content.split("\n")[0] if movie.content else "Mock Movie Title"
    return {
        "id": movie.id,
        "title": title,
        "description": movie.content,
        "image_url": movie.image_url,
        "category": "movies",
        "genre": random.choice(MOCK_GENRES),
        "year": random.randint(1990, 2023),
        "rating": round(random.uniform(5.0, 10.0), 1),
        "cast": random.sample(MOCK_CAST, random.randint(1, 3)),
        "crew": random.sample(MOCK_CREW, random.randint(1, 2)),
        "created_at": movie.created_at.isoformat(),
        "user": {
            "id": movie.user.id,
            "username": movie.user.username,
            "avatar_url": None
        },
        "likes": len(movie.comments),
        "comments": len(movie.comments)
    }

def enhance_tv_response(post, db):
    """Enhance TV show response with mock data"""
    import random
    title = post.content.split("\n")[0] if post.content else "Mock TV Show Title"
    return {
        "id": post.id,
        "title": title,
        "description": post.content,
        "image_url": post.image_url,
        "category": "tv",
        "genre": random.choice(MOCK_GENRES),
        "first_air_date": f"{random.randint(1990, 2023)}-01-01",
        "rating": round(random.uniform(5.0, 10.0), 1),
        "cast": random.sample(MOCK_CAST, random.randint(1, 3)),
        "crew": random.sample(MOCK_CREW, random.randint(1, 2)),
        "created_at": post.created_at.isoformat(),
        "user": {
            "id": post.user.id,
            "username": post.user.username,
            "avatar_url": None
        },
        "likes": len(post.comments),
        "comments": len(post.comments)
    }

@router.get("/")
async def get_movies(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get movie-like posts (parsed from content) with pagination and filtering"""
    if settings.has_tmdb:
        return {"message": "TMDB API is configured. Please use the enhanced movie API endpoints for full features."}
    
    query = db.query(Post).filter(
        or_(Post.content.contains("Director:"), Post.content.contains("Rating:"))
    )
    
    # Optional filters operate on content since schema doesn't have explicit fields
    if category:
        query = query.filter(Post.content.contains(category))
    
    if search:
        query = query.filter(Post.content.contains(search))
    
    movies = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    enhanced_movies = [enhance_movie_response(movie, db) for movie in movies]
    
    return {
        "movies": enhanced_movies,
        "total": query.count(),
        "warning": "Using database posts. Configure TMDB API for full features."
    }

@router.get("/trending")
async def get_trending_movies(db: Session = Depends(get_db)):
    """Get trending movies based on recency (comments used as proxy for engagement)"""
    if settings.has_tmdb:
        return {"message": "TMDB API is configured. Please use the enhanced movie API endpoints for full features."}
    
    movies = db.query(Post).filter(
        or_(Post.content.contains("Director:"), Post.content.contains("Rating:"))
    ).order_by(
        desc(Post.created_at)
    ).limit(10).all()
    
    enhanced_movies = [enhance_movie_response(movie, db) for movie in movies]
    
    return {
        "movies": enhanced_movies,
        "warning": "Using database posts. Configure TMDB API for full features."
    }

@router.get("/{movie_id}")
async def get_movie_detail(movie_id: str, db: Session = Depends(get_db)):
    """Get detailed movie information"""
    if settings.has_tmdb:
        return {"message": "TMDB API is configured. Please use the enhanced movie API endpoints for full features."}
    
    movie = db.query(Post).filter(Post.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    enhanced_movie = enhance_movie_response(movie, db)
    enhanced_movie["comments"] = [
        {
            "id": comment.id,
            "content": comment.text,
            "created_at": None,
            "user": {
                "id": comment.owner.id if comment.owner else None,
                "username": comment.owner.username if comment.owner else None
            }
        }
        for comment in movie.comments
    ]
    
    return {
        **enhanced_movie,
        "warning": "Using database posts. Configure TMDB API for full features."
    }

@router.get("/tv/")
async def get_tv_shows(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get TV show-like posts (parsed from content) with pagination and filtering"""
    if settings.has_tmdb:
        return {"message": "TMDB API is configured. Please use the enhanced movie API endpoints for full features."}
    
    query = db.query(Post).filter(
        or_(Post.content.contains("Director:"), Post.content.contains("Rating:"))
    )
    
    # Optional filters operate on content since schema doesn't have explicit fields
    if category:
        query = query.filter(Post.content.contains(category))
    
    if search:
        query = query.filter(Post.content.contains(search))
    
    tv_shows = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    enhanced_tv_shows = [enhance_tv_response(tv_show, db) for tv_show in tv_shows]
    
    return {
        "tv_shows": enhanced_tv_shows,
        "total": query.count(),
        "warning": "Using database posts. Configure TMDB API for full features."
    }