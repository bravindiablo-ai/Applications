"""
External APIs Router for TRENDY App
Handles integrations with TMDB, Spotify, Agora, AdMob, and other external services
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.config import get_settings
from app.services.movie_service import MovieService
from app.auth.middleware import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

# TMDB Endpoints
@router.get("/tmdb/search/movies")
async def search_tmdb_movies(
    query: str = Query(..., description="Search query"),
    year: Optional[int] = Query(None, description="Release year"),
    page: int = Query(1, ge=1, le=1000, description="Page number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search movies via TMDB API"""
    try:
        movie_service = MovieService(db)
        results = movie_service.search_movies(query, year, page)
        return results
    except Exception as e:
        logger.error(f"TMDB movie search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search movies")

@router.get("/tmdb/search/tv")
async def search_tmdb_tv_shows(
    query: str = Query(..., description="Search query"),
    first_air_date_year: Optional[int] = Query(None, description="First air date year"),
    page: int = Query(1, ge=1, le=1000, description="Page number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search TV shows via TMDB API"""
    try:
        movie_service = MovieService(db)
        results = movie_service.search_tv_shows(query, first_air_date_year, page)
        return results
    except Exception as e:
        logger.error(f"TMDB TV search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search TV shows")

@router.get("/tmdb/search/people")
async def search_tmdb_people(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, le=1000, description="Page number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search people via TMDB API"""
    try:
        movie_service = MovieService(db)
        results = movie_service.search_people(query, page)
        return results
    except Exception as e:
        logger.error(f"TMDB people search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search people")

@router.get("/tmdb/trending/movies/{time_window}")
async def get_trending_movies(
    time_window: str,
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trending movies from TMDB"""
    try:
        movie_service = MovieService(db)
        movies = movie_service.get_trending_movies(time_window, limit)
        return {"results": [movie.__dict__ for movie in movies]}
    except Exception as e:
        logger.error(f"Trending movies error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get trending movies")

@router.get("/tmdb/trending/tv/{time_window}")
async def get_trending_tv_shows(
    time_window: str,
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trending TV shows from TMDB"""
    try:
        movie_service = MovieService(db)
        tv_shows = movie_service.get_trending_tv_shows(time_window, limit)
        return {"results": [tv.__dict__ for tv in tv_shows]}
    except Exception as e:
        logger.error(f"Trending TV shows error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get trending TV shows")

@router.get("/tmdb/movie/{tmdb_id}")
async def get_movie_details(
    tmdb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed movie information from TMDB"""
    try:
        movie_service = MovieService(db)
        movie = movie_service.sync_movie_from_tmdb(tmdb_id)
        return movie.__dict__
    except Exception as e:
        logger.error(f"Movie details error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get movie details")

@router.get("/tmdb/tv/{tmdb_id}")
async def get_tv_show_details(
    tmdb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed TV show information from TMDB"""
    try:
        movie_service = MovieService(db)
        tv_show = movie_service.sync_tv_show_from_tmdb(tmdb_id)
        return tv_show.__dict__
    except Exception as e:
        logger.error(f"TV show details error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get TV show details")

@router.get("/tmdb/genres")
async def get_genres(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all movie and TV genres from TMDB"""
    try:
        movie_service = MovieService(db)
        genres = movie_service.get_genres()
        return {"genres": genres}
    except Exception as e:
        logger.error(f"Genres error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get genres")

# Spotify Endpoints (Placeholder - would need Spotify service)
@router.get("/spotify/search")
async def search_spotify(
    query: str = Query(..., description="Search query"),
    type: str = Query("track", regex="^(track|artist|album|playlist)$", description="Search type"),
    limit: int = Query(20, ge=1, le=50, description="Number of results"),
    current_user: User = Depends(get_current_user)
):
    """Search Spotify (placeholder - needs Spotify service implementation)"""
    # TODO: Implement Spotify service and integrate
    raise HTTPException(status_code=501, detail="Spotify integration not yet implemented")

@router.get("/spotify/recommendations")
async def get_spotify_recommendations(
    seed_tracks: Optional[str] = Query(None, description="Seed track IDs"),
    seed_artists: Optional[str] = Query(None, description="Seed artist IDs"),
    seed_genres: Optional[str] = Query(None, description="Seed genres"),
    limit: int = Query(20, ge=1, le=100, description="Number of recommendations"),
    current_user: User = Depends(get_current_user)
):
    """Get Spotify recommendations (placeholder)"""
    raise HTTPException(status_code=501, detail="Spotify integration not yet implemented")

# Agora Endpoints
@router.post("/agora/token")
async def generate_agora_token(
    channel_name: str,
    uid: Optional[int] = None,
    role: str = Query("publisher", regex="^(publisher|subscriber)$", description="User role"),
    current_user: User = Depends(get_current_user)
):
    """Generate Agora RTC token for video/audio calls"""
    try:
        # TODO: Implement Agora service
        # This would require Agora SDK and proper token generation
        raise HTTPException(status_code=501, detail="Agora token generation not yet implemented")
    except Exception as e:
        logger.error(f"Agora token error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate Agora token")

@router.get("/agora/channels/{channel_name}/users")
async def get_channel_users(
    channel_name: str,
    current_user: User = Depends(get_current_user)
):
    """Get users in an Agora channel (placeholder)"""
    # TODO: Implement channel user tracking
    raise HTTPException(status_code=501, detail="Channel user tracking not yet implemented")

# AdMob Endpoints
@router.get("/admob/config")
async def get_admob_config(
    platform: str = Query(..., regex="^(android|ios)$", description="Platform"),
    current_user: User = Depends(get_current_user)
):
    """Get AdMob configuration for the specified platform"""
    try:
        # Use settings from config
        if platform.lower() == "android":
            config = {
                "app_id": settings.admob_app_id or "ca-app-pub-3940256099942544~3347511713",  # Test ID
                "banner_unit_id": settings.admob_banner_unit or "ca-app-pub-3940256099942544/6300978111",
                "native_unit_id": settings.admob_native_unit or "ca-app-pub-3940256099942544/2247696110",
                "rewarded_unit_id": settings.admob_rewarded_unit or "ca-app-pub-3940256099942544/5224354917"
            }
        else:  # iOS
            config = {
                "app_id": settings.admob_app_id or "ca-app-pub-3940256099942544~1458002511",  # Test ID
                "banner_unit_id": settings.admob_banner_unit or "ca-app-pub-3940256099942544/2934735716",
                "native_unit_id": settings.admob_native_unit or "ca-app-pub-3940256099942544/3986624511",
                "rewarded_unit_id": settings.admob_rewarded_unit or "ca-app-pub-3940256099942544/1712485313"
            }
        return config
    except Exception as e:
        logger.error(f"AdMob config error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get AdMob configuration")

# Firebase Endpoints (if needed for external access)
@router.post("/firebase/custom-token")
async def create_firebase_custom_token(
    uid: str,
    claims: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
):
    """Create Firebase custom token (admin only or specific use cases)"""
    try:
        # TODO: Implement Firebase custom token creation if needed
        raise HTTPException(status_code=501, detail="Firebase custom token creation not yet implemented")
    except Exception as e:
        logger.error(f"Firebase token error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create Firebase token")

# Stripe External Endpoints (additional to existing stripe_webhooks)
@router.get("/stripe/config")
async def get_stripe_config(
    current_user: User = Depends(get_current_user)
):
    """Get Stripe publishable key for frontend"""
    try:
        return {
            "publishable_key": settings.stripe_publishable_key,
            "environment": "production" if settings.ENV == "production" else "test"
        }
    except Exception as e:
        logger.error(f"Stripe config error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get Stripe configuration")

# Health check for external APIs
@router.get("/health")
async def external_apis_health():
    """Health check for external API integrations"""
    health_status = {
        "tmdb": "unknown",
        "spotify": "unknown",
        "agora": "unknown",
        "admob": "unknown",
        "stripe": "unknown"
    }

    # Check TMDB
    try:
        if settings.tmdb_api_key and settings.tmdb_api_key != "your_tmdb_api_key_here":
            health_status["tmdb"] = "configured"
        else:
            health_status["tmdb"] = "not_configured"
    except:
        health_status["tmdb"] = "error"

    # Check Spotify
    try:
        if settings.spotify_client_id and settings.spotify_client_id != "your_spotify_client_id_here":
            health_status["spotify"] = "configured"
        else:
            health_status["spotify"] = "not_configured"
    except:
        health_status["spotify"] = "error"

    # Check Agora
    try:
        if settings.agora_app_id:
            health_status["agora"] = "configured"
        else:
            health_status["agora"] = "not_configured"
    except:
        health_status["agora"] = "error"

    # Check AdMob
    try:
        if settings.admob_app_id:
            health_status["admob"] = "configured"
        else:
            health_status["admob"] = "not_configured"
    except:
        health_status["admob"] = "error"

    # Check Stripe
    try:
        if settings.stripe_publishable_key:
            health_status["stripe"] = "configured"
        else:
            health_status["stripe"] = "not_configured"
    except:
        health_status["stripe"] = "error"

    return {
        "service": "TRENDY External APIs",
        "status": "healthy",
        "integrations": health_status
    }
