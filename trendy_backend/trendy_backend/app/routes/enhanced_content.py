"""
Enhanced Content API Routes for TRENDY App
Handles music, movies, and football hub enhancements
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db
from app.models.enhanced_post import Music, Movie, FootballMatch
from app.auth.middleware import get_current_user

router = APIRouter(prefix="/content", tags=["enhanced-content"])

class MusicResponse(BaseModel):
    id: int
    title: str
    artist: str
    album: str
    duration: int
    genre: str
    cover_art_url: str
    audio_url: str
    is_trending: bool
    play_count: int

class MovieResponse(BaseModel):
    id: int
    title: str
    year: int
    genre: str
    director: str
    poster_url: str
    trailer_url: str
    rating: float
    runtime: int
    plot: str
    is_trending: bool

class FootballMatchResponse(BaseModel):
    id: int
    home_team: str
    away_team: str
    match_date: str
    competition: str
    venue: str
    home_score: Optional[int]
    away_score: Optional[int]
    status: str
    highlights_url: Optional[str]
    is_featured: bool

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    offset: int = 0

@router.get("/music/trending", response_model=List[MusicResponse])
async def get_trending_music(
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get trending music with optional genre filtering"""
    
    query = db.query(Music).filter(Music.is_trending == True)
    
    if genre:
        query = query.filter(Music.genre.ilike(f"%{genre}%"))
    
    music = query.order_by(desc(Music.play_count)).limit(limit).all()
    
    return [
        MusicResponse(
            id=m.id,
            title=m.title,
            artist=m.artist,
            album=m.album,
            duration=m.duration,
            genre=m.genre,
            cover_art_url=m.cover_art_url,
            audio_url=m.audio_url,
            is_trending=m.is_trending,
            play_count=m.play_count
        )
        for m in music
    ]

@router.get("/music/search")
async def search_music(
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search music by title, artist, or album"""
    
    search_query = db.query(Music).filter(
        func.lower(Music.title).contains(func.lower(query)) |
        func.lower(Music.artist).contains(func.lower(query)) |
        func.lower(Music.album).contains(func.lower(query))
    )
    
    if genre:
        search_query = search_query.filter(Music.genre.ilike(f"%{genre}%"))
    
    music = search_query.order_by(desc(Music.play_count)).limit(limit).all()
    
    return {
        "results": [
            {
                "id": m.id,
                "title": m.title,
                "artist": m.artist,
                "album": m.album,
                "duration": m.duration,
                "genre": m.genre,
                "cover_art_url": m.cover_art_url,
                "audio_url": m.audio_url,
                "is_trending": m.is_trending,
                "play_count": m.play_count
            }
            for m in music
        ],
        "count": len(music)
    }

@router.get("/movies/trending", response_model=List[MovieResponse])
async def get_trending_movies(
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get trending movies with filtering options"""
    
    query = db.query(Movie).filter(Movie.is_trending == True)
    
    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    
    if year:
        query = query.filter(Movie.year == year)
    
    movies = query.order_by(desc(Movie.rating)).limit(limit).all()
    
    return [
        MovieResponse(
            id=m.id,
            title=m.title,
            year=m.year,
            genre=m.genre,
            director=m.director,
            poster_url=m.poster_url,
            trailer_url=m.trailer_url,
            rating=m.rating,
            runtime=m.runtime,
            plot=m.plot,
            is_trending=m.is_trending
        )
        for m in movies
    ]

@router.get("/movies/search")
async def search_movies(
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Search movies by title, director, or genre"""
    
    search_query = db.query(Movie).filter(
        func.lower(Movie.title).contains(func.lower(query)) |
        func.lower(Movie.director).contains(func.lower(query)) |
        func.lower(Movie.genre).contains(func.lower(query))
    )
    
    if genre:
        search_query = search_query.filter(Movie.genre.ilike(f"%{genre}%"))
    
    if year:
        search_query = search_query.filter(Movie.year == year)
    
    movies = search_query.order_by(desc(Movie.rating)).limit(limit).all()
    
    return {
        "results": [
            {
                "id": m.id,
                "title": m.title,
                "year": m.year,
                "genre": m.genre,
                "director": m.director,
                "poster_url": m.poster_url,
                "trailer_url": m.trailer_url,
                "rating": m.rating,
                "runtime": m.runtime,
                "plot": m.plot,
                "is_trending": m.is_trending
            }
            for m in movies
        ],
        "count": len(movies)
    }

@router.get("/football/matches")
async def get_football_matches(
    limit: int = Query(20, ge=1, le=100),
    team: Optional[str] = None,
    competition: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get football matches with filtering options"""
    
    query = db.query(FootballMatch)
    
    if team:
        query = query.filter(
            func.lower(FootballMatch.home_team).contains(func.lower(team)) |
            func.lower(FootballMatch.away_team).contains(func.lower(team))
        )
    
    if competition:
        query = query.filter(FootballMatch.competition.ilike(f"%{competition}%"))
    
    if status:
        query = query.filter(FootballMatch.status == status)
    
    matches = query.order_by(FootballMatch.match_date.desc()).limit(limit).all()
    
    return {
        "matches": [
            {
                "id": m.id,
                "home_team": m.home_team,
                "away_team": m.away_team,
                "match_date": m.match_date.isoformat(),
                "competition": m.competition,
                "venue": m.venue,
                "home_score": m.home_score,
                "away_score": m.away_score,
                "status": m.status,
                "highlights_url": m.highlights_url,
                "is_featured": m.is_featured
            }
            for m in matches
        ],
        "count": len(matches)
    }

@router.get("/football/matches/search")
async def search_football_matches(
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search football matches by team or competition"""
    
    matches = db.query(FootballMatch).filter(
        func.lower(FootballMatch.home_team).contains(func.lower(query)) |
        func.lower(FootballMatch.away_team).contains(func.lower(query)) |
        func.lower(FootballMatch.competition).contains(func.lower(query))
    ).order_by(FootballMatch.match_date.desc()).limit(limit).all()
    
    return {
        "results": [
            {
                "id": m.id,
                "home_team": m.home_team,
                "away_team": m.away_team,
                "match_date": m.match_date.isoformat(),
                "competition": m.competition,
                "venue": m.venue,
                "home_score": m.home_score,
                "away_score": m.away_score,
                "status": m.status,
                "highlights_url": m.highlights_url,
                "is_featured": m.is_featured
            }
            for m in matches
        ],
        "count": len(matches)
    }

@router.get("/music/{music_id}")
async def get_music_by_id(
    music_id: int,
    db: Session = Depends(get_db)
):
    """Get music details by ID"""
    
    music = db.query(Music).filter(Music.id == music_id).first()
    if not music:
        raise HTTPException(status_code=404, detail="Music not found")
    
    return {
        "id": music.id,
        "title": music.title,
        "artist": music.artist,
        "album": music.album,
        "duration": music.duration,
        "genre": music.genre,
        "spotify_id": music.spotify_id,
        "apple_music_id": music.apple_music_id,
        "youtube_music_id": music.youtube_music_id,
        "cover_art_url": music.cover_art_url,
        "audio_url": music.audio_url,
        "is_trending": music.is_trending,
        "play_count": music.play_count
    }

@router.get("/movies/{movie_id}")
async def get_movie_by_id(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """Get movie details by ID"""
    
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return {
        "id": movie.id,
        "title": movie.title,
        "year": movie.year,
        "genre": movie.genre,
        "director": movie.director,
        "poster_url": movie.poster_url,
        "trailer_url": movie.trailer_url,
        "imdb_id": movie.imdb_id,
        "tmdb_id": movie.tmdb_id,
        "rating": movie.rating,
        "runtime": movie.runtime,
        "plot": movie.plot,
        "is_trending": movie.is_trending
    }

@router.get("/football/matches/{match_id}")
async def get_football_match_by_id(
    match_id: int,
    db: Session = Depends(get_db)
):
    """Get football match details by ID"""
    
    match = db.query(FootballMatch).filter(FootballMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    return {
        "id": match.id,
        "home_team": match.home_team,
        "away_team": match.away_team,
        "match_date": match.match_date.isoformat(),
        "competition": match.competition,
        "venue": match.venue,
        "home_score": match.home_score,
        "away_score": match.away_score,
        "status": match.status,
        "highlights_url": match.highlights_url,
        "is_featured": match.is_featured
    }
