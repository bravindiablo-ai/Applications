from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
import random
from app.core.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)

settings = get_settings()

# Enhanced mock music dataset with diverse tracks
GENRES = ["Pop", "Rock", "Hip-Hop", "Jazz", "Classical", "EDM", "Country", "R&B", "Reggae", "Blues", "Folk", "Metal", "Punk", "Indie", "Alternative"]
MOODS = ["Happy", "Sad", "Energetic", "Calm", "Romantic", "Angry", "Melancholic", "Uplifting", "Chill", "Intense"]
ARTISTS = ["DJ Pulse", "Luna Sky", "The Vibes", "Electro Wave", "Soul Singer", "Rock Star", "Jazz Master", "Classical Composer", "Hip-Hop Artist", "Country Singer", "Reggae King", "Blues Legend", "Folk Troubadour", "Metal Head", "Punk Rocker", "Indie Dreamer", "Alternative Voice", "EDM Producer", "R&B Sensation", "Pop Icon"]
ALBUMS = ["City Lights", "Horizons", "Routes", "Electric Dreams", "Soulful Nights", "Rock Revolution", "Jazz Journeys", "Classical Masterpieces", "Hip-Hop Hits", "Country Roads", "Reggae Rhythms", "Blues Ballads", "Folk Tales", "Metal Mayhem", "Punk Protest", "Indie Vibes", "Alternative Realities", "EDM Explosions", "R&B Romance", "Pop Perfection"]

MOCK_MUSIC = []
for i in range(1, 51):
    tempo = random.uniform(60, 200)
    energy = random.uniform(0, 1)
    danceability = random.uniform(0, 1)
    valence = random.uniform(0, 1)
    track = {
        "id": i,
        "title": f"Track {i}",
        "artist": random.choice(ARTISTS),
        "album": random.choice(ALBUMS),
        "genre": random.choice(GENRES),
        "mood": random.choice(MOODS),
        "tempo": tempo,
        "energy": energy,
        "danceability": danceability,
        "valence": valence,
        "image_url": f"https://picsum.photos/seed/track{i}/400/300",
        "audio_url": "https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav",
        "duration": f"{random.randint(2,5)}:{random.randint(10,59):02d}",
        "created_at": datetime.utcnow().isoformat(),
        "user": {"id": i % 5 + 1, "username": f"user{i % 5}", "avatar_url": None},
        "likes": random.randint(10, 1000),
        "plays": random.randint(100, 10000),
        "audio_features": {
            "tempo": tempo,
            "energy": energy,
            "danceability": danceability,
            "valence": valence,
            "key": random.randint(0, 11),
            "mode": random.choice([0, 1]),
            "loudness": random.uniform(-20, 0),
            "speechiness": random.uniform(0, 1),
            "acousticness": random.uniform(0, 1),
            "instrumentalness": random.uniform(0, 1),
            "liveness": random.uniform(0, 1),
        }
    }
    MOCK_MUSIC.append(track)

# Mock artists data
MOCK_ARTISTS = [
    {
        "id": i,
        "name": artist,
        "bio": f"Bio for {artist}",
        "image_url": f"https://picsum.photos/seed/artist{i}/400/400",
        "genres": random.sample(GENRES, random.randint(1, 3)),
        "follower_count": random.randint(1000, 100000),
        "verified": random.choice([True, False]),
        "popularity_score": random.uniform(0, 100)
    }
    for i, artist in enumerate(ARTISTS, 1)
]

# Mock albums data
MOCK_ALBUMS = [
    {
        "id": i,
        "title": album,
        "release_date": datetime.utcnow().replace(year=random.randint(2000, 2023)).isoformat(),
        "album_type": random.choice(["album", "single", "compilation"]),
        "cover_art_url": f"https://picsum.photos/seed/album{i}/400/400",
        "genres": random.sample(GENRES, random.randint(1, 2)),
        "total_tracks": random.randint(8, 20),
        "label": f"Label {i}",
        "artists": [random.choice(MOCK_ARTISTS)["name"] for _ in range(random.randint(1, 2))]
    }
    for i, album in enumerate(ALBUMS, 1)
]

from typing import Optional

@router.get("/")
async def get_music(skip: int = 0, limit: int = 20, genre: Optional[str] = None, search: Optional[str] = None):
    if settings.has_spotify:
        return {"message": "Spotify API is configured. Please use the enhanced music API at /api/music for full features."}
    items = MOCK_MUSIC
    if genre:
        items = [m for m in items if m.get("genre", "").lower() == genre.lower()]
    if search:
        q = search.lower()
        items = [m for m in items if q in m["title"].lower() or q in m["artist"].lower()]
    total = len(items)
    items = items[skip: skip + limit]
    return {"music": items, "total": total, "warning": "Using mock data. Configure Spotify API for full features."}

@router.get("/trending")
async def get_trending_music():
    if settings.has_spotify:
        return {"message": "Spotify API is configured. Please use the enhanced music API at /api/music for full features."}
    # Simple sort by plays/likes
    items = sorted(MOCK_MUSIC, key=lambda m: (m.get("plays", 0), m.get("likes", 0)), reverse=True)
    return {"music": items[:10], "warning": "Using mock data. Configure Spotify API for full features."}

@router.get("/genres")
async def get_genres():
    """Get music genres - hardened against unexpected errors"""
    try:
        logger.info("Fetching music genres")
        if settings.has_spotify:
            return {"genres": GENRES, "message": "Spotify API is configured. Please use the enhanced music API at /api/music for full features."}
        return {"genres": GENRES, "warning": "Using mock data. Configure Spotify API for full features."}
    except Exception as e:
        logger.error(f"Error fetching genres: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")