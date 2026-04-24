from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.database import get_db
from app.auth.middleware import get_current_user, optional_auth
from app.services.music_service import MusicService
from app.schemas.music import (
    SearchRequest, SearchResponse, RecommendationsResponse, TrackResponse, TrackDetail,
    ArtistResponse, ArtistDetail, AlbumResponse, AlbumDetail, PlaylistResponse, PlaylistDetail,
    PlaylistCreate, PlaylistUpdate, PlaylistTrackAdd, PlaylistTrackRemove, PlaylistReorder,
    CollaboratorAdd, LibraryResponse, PlayHistoryResponse, PlayStatsResponse, QueueResponse,
    QueueAdd, LyricsResponse, AudioFeaturesResponse, ShareRequest, ShareResponse
)
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/music", tags=["music"])

def get_music_service(db: Session = Depends(get_db)) -> MusicService:
    return MusicService(db)

# Search & Discovery Endpoints

@router.get("/search", response_model=SearchResponse)
async def search_music(
    query: str = Query(..., min_length=1),
    search_type: str = Query("all", regex="^(all|track|artist|album|playlist)$"),
    genre: Optional[str] = None,
    year_min: Optional[int] = Query(None, ge=1900, le=datetime.now().year),
    year_max: Optional[int] = Query(None, ge=1900, le=datetime.now().year),
    tempo_min: Optional[float] = Query(None, ge=0, le=300),
    tempo_max: Optional[float] = Query(None, ge=0, le=300),
    mood: Optional[str] = None,
    explicit: Optional[bool] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    music_service: MusicService = Depends(get_music_service),
    current_user: Optional[User] = Depends(optional_auth)
):
    """Advanced search with filters"""
    filters = {
        'genre': genre,
        'year_min': year_min,
        'year_max': year_max,
        'tempo_min': tempo_min,
        'tempo_max': tempo_max,
        'mood': mood,
        'explicit': explicit
    }
    results = music_service.advanced_search(query, search_type, filters)
    
    # Enhance with user data if authenticated
    if current_user:
        for result_list in results.values():
            for item in result_list:
                if hasattr(item, 'is_liked'):
                    item.is_liked = music_service.db.query(music_service.db.query(music_service.models.TrackLike).filter(
                        music_service.models.TrackLike.user_id == current_user.id,
                        music_service.models.TrackLike.track_id == item.id
                    ).exists()).scalar()
                # Similar for other user-specific fields
    
    return SearchResponse(
        results=results,
        total=sum(len(v) for v in results.values()),
        query=query,
        filters=filters
    )

@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    limit: int = Query(20, ge=1, le=100),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Personalized recommendations"""
    tracks = music_service.get_personalized_recommendations(current_user.id, limit)
    return RecommendationsResponse(
        tracks=[TrackResponse.from_orm(track) for track in tracks],
        seed_type="user",
        seed_id=str(current_user.id),
        algorithm="personalized"
    )

@router.get("/recommendations/track/{track_id}", response_model=RecommendationsResponse)
async def get_track_recommendations(
    track_id: int,
    limit: int = Query(20, ge=1, le=100),
    music_service: MusicService = Depends(get_music_service)
):
    """Similar tracks"""
    tracks = music_service.get_track_recommendations(track_id, limit)
    return RecommendationsResponse(
        tracks=[TrackResponse.from_orm(track) for track in tracks],
        seed_type="track",
        seed_id=str(track_id),
        algorithm="audio_features"
    )

@router.get("/recommendations/artist/{artist_id}", response_model=List[ArtistResponse])
async def get_artist_recommendations(
    artist_id: int,
    limit: int = Query(20, ge=1, le=100),
    music_service: MusicService = Depends(get_music_service)
):
    """Similar artists"""
    artists = music_service.get_artist_recommendations(artist_id, limit)
    return [ArtistResponse.from_orm(artist) for artist in artists]

@router.get("/recommendations/mood/{mood}", response_model=RecommendationsResponse)
async def get_mood_recommendations(
    mood: str,
    limit: int = Query(20, ge=1, le=100),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Mood-based discovery"""
    tracks = music_service.get_mood_based_recommendations(current_user.id, mood, limit)
    return RecommendationsResponse(
        tracks=[TrackResponse.from_orm(track) for track in tracks],
        seed_type="mood",
        seed_id=mood,
        algorithm="mood_filter"
    )

@router.get("/trending", response_model=List[TrackResponse])
async def get_trending_tracks(
    genre: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    music_service: MusicService = Depends(get_music_service)
):
    """Trending tracks"""
    tracks = music_service.get_trending_tracks(genre, limit)
    return [TrackResponse.from_orm(track) for track in tracks]

@router.get("/genres")
async def get_genres(music_service: MusicService = Depends(get_music_service)):
    """List available genres"""
    # This could be cached or queried from database
    genres = ["pop", "rock", "hip-hop", "electronic", "jazz", "classical", "country", "r&b", "reggae", "folk"]
    return {"genres": genres}

# Track Endpoints

@router.get("/tracks/{track_id}", response_model=TrackDetail)
async def get_track_details(
    track_id: int,
    music_service: MusicService = Depends(get_music_service),
    current_user: Optional[User] = Depends(optional_auth)
):
    """Track details with audio features"""
    track = music_service.db.query(music_service.models.Track).filter(music_service.models.Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    response = TrackDetail.from_orm(track)
    if current_user:
        response.is_liked = music_service.db.query(music_service.models.TrackLike).filter(
            music_service.models.TrackLike.user_id == current_user.id,
            music_service.models.TrackLike.track_id == track_id
        ).first() is not None
        response.is_in_library = music_service.is_in_library(current_user.id, track_id, 'track')
    
    return response

@router.get("/tracks/{track_id}/lyrics", response_model=LyricsResponse)
async def get_track_lyrics(
    track_id: int,
    language: str = Query("en", min_length=2, max_length=5),
    music_service: MusicService = Depends(get_music_service)
):
    """Get lyrics"""
    lyrics = music_service.get_track_lyrics(track_id, language)
    if not lyrics:
        lyrics = music_service.sync_lyrics_from_api(track_id, language)
    if not lyrics:
        raise HTTPException(status_code=404, detail="Lyrics not found")
    return LyricsResponse.from_orm(lyrics)

@router.post("/tracks/{track_id}/like")
async def like_track(
    track_id: int,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Like/unlike track (toggle)"""
    existing = music_service.db.query(music_service.models.TrackLike).filter(
        music_service.models.TrackLike.user_id == current_user.id,
        music_service.models.TrackLike.track_id == track_id
    ).first()
    
    if existing:
        music_service.unlike_track(current_user.id, track_id)
        return {"action": "unliked"}
    else:
        music_service.like_track(current_user.id, track_id)
        return {"action": "liked"}

@router.get("/tracks/liked", response_model=List[TrackResponse])
async def get_liked_tracks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Get user's liked tracks"""
    tracks = music_service.get_liked_tracks(current_user.id, limit, offset)
    return [TrackResponse.from_orm(track) for track in tracks]

@router.post("/tracks/{track_id}/play")
async def record_play(
    track_id: int,
    play_duration_ms: int = Query(..., ge=0),
    completed: bool = False,
    context_type: str = Query("track"),
    context_id: Optional[str] = None,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Record play event"""
    music_service.record_play(current_user.id, track_id, context_type, context_id, play_duration_ms, completed)
    logger.info(f"Play recorded: user {current_user.id}, track {track_id}")
    return {"status": "recorded"}

# Artist Endpoints

@router.get("/artists/{artist_id}", response_model=ArtistDetail)
async def get_artist_details(
    artist_id: int,
    include_tracks: bool = Query(False),
    include_albums: bool = Query(False),
    music_service: MusicService = Depends(get_music_service),
    current_user: Optional[User] = Depends(optional_auth)
):
    """Artist details"""
    details = music_service.get_artist_details(artist_id, include_tracks, include_albums)
    if not details:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    response = ArtistDetail.from_orm(details['artist'])
    response.follower_count = details['follower_count']
    if include_tracks:
        response.top_tracks = [TrackResponse.from_orm(t) for t in details['tracks']]
    if include_albums:
        response.albums = [AlbumResponse.from_orm(a) for a in details['albums']]
    
    if current_user:
        response.is_following = music_service.is_following_artist(current_user.id, artist_id)
    
    return response

@router.get("/artists/{artist_id}/tracks", response_model=List[TrackResponse])
async def get_artist_tracks(
    artist_id: int,
    limit: int = Query(20, ge=1, le=100),
    music_service: MusicService = Depends(get_music_service)
):
    """Artist's top tracks"""
    tracks = music_service.get_artist_top_tracks(artist_id, limit)
    return [TrackResponse.from_orm(track) for track in tracks]

@router.get("/artists/{artist_id}/albums", response_model=List[AlbumResponse])
async def get_artist_albums(
    artist_id: int,
    album_type: Optional[str] = Query(None, regex="^(album|single|compilation)$"),
    limit: int = Query(20, ge=1, le=100),
    music_service: MusicService = Depends(get_music_service)
):
    """Artist's albums"""
    albums = music_service.get_artist_albums(artist_id, album_type, limit)
    return [AlbumResponse.from_orm(album) for album in albums]

@router.get("/artists/{artist_id}/related", response_model=List[ArtistResponse])
async def get_related_artists(
    artist_id: int,
    limit: int = Query(20, ge=1, le=100),
    music_service: MusicService = Depends(get_music_service)
):
    """Similar artists"""
    artists = music_service.get_artist_recommendations(artist_id, limit)
    return [ArtistResponse.from_orm(artist) for artist in artists]

@router.post("/artists/{artist_id}/follow")
async def follow_artist(
    artist_id: int,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Follow/unfollow artist (toggle)"""
    if music_service.is_following_artist(current_user.id, artist_id):
        music_service.unfollow_artist(current_user.id, artist_id)
        return {"action": "unfollowed"}
    else:
        music_service.follow_artist(current_user.id, artist_id)
        return {"action": "followed"}

@router.get("/artists/following", response_model=List[ArtistResponse])
async def get_followed_artists(
    limit: int = Query(20, ge=1, le=100),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Get followed artists"""
    artists = music_service.get_followed_artists(current_user.id, limit)
    return [ArtistResponse.from_orm(artist) for artist in artists]

# Album Endpoints

@router.get("/albums/{album_id}", response_model=AlbumDetail)
async def get_album_details(
    album_id: int,
    include_tracks: bool = Query(True),
    music_service: MusicService = Depends(get_music_service),
    current_user: Optional[User] = Depends(optional_auth)
):
    """Album details with tracks"""
    details = music_service.get_album_details(album_id, include_tracks)
    if not details:
        raise HTTPException(status_code=404, detail="Album not found")
    
    response = AlbumDetail.from_orm(details['album'])
    if include_tracks:
        response.tracks = [TrackResponse.from_orm(t) for t in details['tracks']]
    
    if current_user:
        response.is_in_library = music_service.is_in_library(current_user.id, album_id, 'album')
    
    return response

@router.get("/albums/{album_id}/tracks", response_model=List[TrackResponse])
async def get_album_tracks(
    album_id: int,
    music_service: MusicService = Depends(get_music_service)
):
    """Album tracks"""
    tracks = music_service.get_album_tracks(album_id)
    return [TrackResponse.from_orm(track) for track in tracks]

@router.post("/albums/{album_id}/save")
async def save_album(
    album_id: int,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Save/unsave album to library (toggle)"""
    if music_service.is_in_library(current_user.id, album_id, 'album'):
        music_service.remove_from_library(current_user.id, album_id, 'album')
        return {"action": "removed"}
    else:
        music_service.add_to_library(current_user.id, album_id, 'album')
        return {"action": "saved"}

# Playlist Endpoints

@router.get("/playlists", response_model=List[PlaylistResponse])
async def get_user_playlists(
    include_collaborative: bool = Query(True),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Get user's playlists"""
    playlists = music_service.get_user_playlists(current_user.id, include_collaborative)
    return [PlaylistResponse.from_orm(p) for p in playlists]

@router.post("/playlists", response_model=PlaylistResponse)
async def create_playlist(
    playlist: PlaylistCreate,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Create playlist"""
    new_playlist = music_service.create_playlist(
        current_user.id, playlist.name, playlist.description, 
        playlist.is_public, playlist.is_collaborative
    )
    logger.info(f"Playlist created: {new_playlist.id} by user {current_user.id}")
    return PlaylistResponse.from_orm(new_playlist)

@router.get("/playlists/{playlist_id}", response_model=PlaylistDetail)
async def get_playlist_details(
    playlist_id: int,
    music_service: MusicService = Depends(get_music_service),
    current_user: Optional[User] = Depends(optional_auth)
):
    """Playlist details with tracks"""
    playlist = music_service.db.query(music_service.models.Playlist).filter(music_service.models.Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # Check permissions
    if not playlist.is_public and (not current_user or playlist.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Playlist is private")
    
    response = PlaylistDetail.from_orm(playlist)
    tracks = music_service.db.query(music_service.models.PlaylistTrack).filter(
        music_service.models.PlaylistTrack.playlist_id == playlist_id
    ).order_by(music_service.models.PlaylistTrack.position).all()
    response.tracks = [TrackResponse.from_orm(t.track) for t in tracks]
    
    if current_user:
        response.is_owner = playlist.user_id == current_user.id
        response.can_edit = response.is_owner or any(c.user_id == current_user.id and c.can_edit for c in playlist.collaborators)
        response.is_in_library = music_service.is_in_library(current_user.id, playlist_id, 'playlist')
    
    return response

@router.put("/playlists/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: int,
    updates: PlaylistUpdate,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Update playlist metadata"""
    playlist = music_service.update_playlist(playlist_id, current_user.id, updates.dict(exclude_unset=True))
    return PlaylistResponse.from_orm(playlist)

@router.delete("/playlists/{playlist_id}")
async def delete_playlist(
    playlist_id: int,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Delete playlist"""
    if music_service.delete_playlist(playlist_id, current_user.id):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Playlist not found or not owned by user")

@router.post("/playlists/{playlist_id}/tracks")
async def add_tracks_to_playlist(
    playlist_id: int,
    track_data: PlaylistTrackAdd,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Add tracks to playlist"""
    if music_service.add_tracks_to_playlist(playlist_id, track_data.track_ids, current_user.id, track_data.position):
        return {"status": "added"}
    raise HTTPException(status_code=403, detail="Cannot modify playlist")

@router.delete("/playlists/{playlist_id}/tracks")
async def remove_tracks_from_playlist(
    playlist_id: int,
    track_data: PlaylistTrackRemove,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Remove tracks from playlist"""
    if music_service.remove_tracks_from_playlist(playlist_id, track_data.track_ids, current_user.id):
        return {"status": "removed"}
    raise HTTPException(status_code=403, detail="Cannot modify playlist")

@router.put("/playlists/{playlist_id}/tracks/reorder")
async def reorder_playlist_tracks(
    playlist_id: int,
    reorder_data: PlaylistReorder,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Reorder playlist tracks"""
    if music_service.reorder_playlist_tracks(playlist_id, current_user.id, reorder_data.track_positions):
        return {"status": "reordered"}
    raise HTTPException(status_code=403, detail="Cannot modify playlist")

@router.post("/playlists/{playlist_id}/collaborators")
async def add_collaborator(
    playlist_id: int,
    collaborator: CollaboratorAdd,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Add collaborator"""
    collab = music_service.add_collaborator(playlist_id, current_user.id, collaborator.user_id, collaborator.can_edit)
    return {"status": "added", "collaborator": collab}

@router.delete("/playlists/{playlist_id}/collaborators/{user_id}")
async def remove_collaborator(
    playlist_id: int,
    user_id: int,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Remove collaborator"""
    if music_service.remove_collaborator(playlist_id, current_user.id, user_id):
        return {"status": "removed"}
    raise HTTPException(status_code=404, detail="Collaborator not found")

@router.get("/playlists/{playlist_id}/collaborators")
async def get_collaborators(
    playlist_id: int,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """List collaborators"""
    playlist = music_service.db.query(music_service.models.Playlist).filter(music_service.models.Playlist.id == playlist_id).first()
    if not playlist or playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"collaborators": playlist.collaborators}

@router.post("/playlists/{playlist_id}/follow")
async def follow_playlist(
    playlist_id: int,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Follow/unfollow playlist (toggle)"""
    if music_service.is_in_library(current_user.id, playlist_id, 'playlist'):
        music_service.remove_from_library(current_user.id, playlist_id, 'playlist')
        return {"action": "unfollowed"}
    else:
        music_service.add_to_library(current_user.id, playlist_id, 'playlist')
        return {"action": "followed"}

# Library Endpoints

@router.get("/library/tracks", response_model=LibraryResponse)
async def get_library_tracks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Saved tracks"""
    items = music_service.get_user_library(current_user.id, 'track', limit, offset)
    return LibraryResponse(
        items=[TrackResponse.from_orm(item) for item in items],
        total=len(items),
        library_type='track'
    )

@router.get("/library/albums", response_model=LibraryResponse)
async def get_library_albums(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Saved albums"""
    items = music_service.get_user_library(current_user.id, 'album', limit, offset)
    return LibraryResponse(
        items=[AlbumResponse.from_orm(item) for item in items],
        total=len(items),
        library_type='album'
    )

@router.get("/library/playlists", response_model=LibraryResponse)
async def get_library_playlists(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Saved playlists"""
    items = music_service.get_user_library(current_user.id, 'playlist', limit, offset)
    return LibraryResponse(
        items=[PlaylistResponse.from_orm(item) for item in items],
        total=len(items),
        library_type='playlist'
    )

@router.post("/library/add")
async def add_to_library(
    item_id: int = Query(..., ge=1),
    library_type: str = Query(..., regex="^(track|album|playlist)$"),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Add to library"""
    music_service.add_to_library(current_user.id, item_id, library_type)
    return {"status": "added"}

@router.delete("/library/remove")
async def remove_from_library(
    item_id: int = Query(..., ge=1),
    library_type: str = Query(..., regex="^(track|album|playlist)$"),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Remove from library"""
    if music_service.remove_from_library(current_user.id, item_id, library_type):
        return {"status": "removed"}
    raise HTTPException(status_code=404, detail="Item not in library")

@router.get("/library/contains")
async def check_library_contains(
    item_ids: List[int] = Query(..., ge=1),
    library_type: str = Query(..., regex="^(track|album|playlist)$"),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Check if items are in library"""
    results = {}
    for item_id in item_ids:
        results[item_id] = music_service.is_in_library(current_user.id, item_id, library_type)
    return {"contains": results}

# Play History Endpoints

@router.get("/history/recent", response_model=List[PlayHistoryResponse])
async def get_recently_played(
    limit: int = Query(20, ge=1, le=100),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Recently played tracks"""
    history = music_service.get_recently_played(current_user.id, limit)
    return [PlayHistoryResponse.from_orm(h) for h in history]

@router.get("/history/stats", response_model=PlayStatsResponse)
async def get_listening_stats(
    time_range: str = Query("short", regex="^(short|medium|long)$"),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Listening statistics"""
    stats = music_service.get_play_stats(current_user.id, time_range)
    return PlayStatsResponse(**stats)

@router.get("/history", response_model=List[PlayHistoryResponse])
async def get_listening_history(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Full listening history"""
    history = music_service.get_listening_history(current_user.id, start_date, end_date)
    return [PlayHistoryResponse.from_orm(h) for h in history[offset:offset+limit]]

# Queue Endpoints

@router.get("/queue", response_model=QueueResponse)
async def get_user_queue(
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Get user's queue"""
    queue = music_service.get_user_queue(current_user.id)
    return QueueResponse(
        items=[{"queue_item_id": q.id, "track": TrackResponse.from_orm(q.track), "position": q.position, "added_at": q.added_at} for q in queue],
        total=len(queue)
    )

@router.post("/queue")
async def add_to_queue(
    queue_data: QueueAdd,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Add track to queue"""
    music_service.add_to_queue(current_user.id, queue_data.track_id, queue_data.position)
    return {"status": "added"}

@router.delete("/queue/{queue_item_id}")
async def remove_from_queue(
    queue_item_id: int,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Remove from queue"""
    if music_service.remove_from_queue(current_user.id, queue_item_id):
        return {"status": "removed"}
    raise HTTPException(status_code=404, detail="Queue item not found")

@router.put("/queue/reorder")
async def reorder_queue(
    item_positions: List[Dict[str, int]] = Query(...),
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Reorder queue"""
    if music_service.reorder_queue(current_user.id, item_positions):
        return {"status": "reordered"}
    raise HTTPException(status_code=400, detail="Reorder failed")

@router.delete("/queue/clear")
async def clear_queue(
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Clear entire queue"""
    if music_service.clear_queue(current_user.id):
        return {"status": "cleared"}
    raise HTTPException(status_code=400, detail="Clear failed")

# Audio Features Endpoints

@router.get("/audio-features/{track_id}", response_model=AudioFeaturesResponse)
async def get_audio_features(
    track_id: int,
    music_service: MusicService = Depends(get_music_service)
):
    """Get audio features for track"""
    features = music_service.get_track_audio_features(track_id)
    if not features:
        raise HTTPException(status_code=404, detail="Audio features not available")
    return AudioFeaturesResponse(track_id=track_id, **features)

@router.post("/audio-features/analyze", response_model=Dict[int, AudioFeaturesResponse])
async def analyze_audio_features(
    track_ids: List[int] = Query(..., ge=1),
    music_service: MusicService = Depends(get_music_service)
):
    """Batch analyze tracks"""
    features = music_service.analyze_audio_features(track_ids)
    return {tid: AudioFeaturesResponse(track_id=tid, **f) for tid, f in features.items()}

# Social/Sharing Endpoints

@router.post("/share/track", response_model=ShareResponse)
async def share_track(
    share_data: ShareRequest,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Share track"""
    result = music_service.share_track(current_user.id, share_data.item_id, share_data.share_type, share_data.recipient_ids)
    return ShareResponse(**result)

@router.post("/share/playlist", response_model=ShareResponse)
async def share_playlist(
    share_data: ShareRequest,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Share playlist"""
    result = music_service.share_playlist(current_user.id, share_data.item_id, share_data.share_type, share_data.recipient_ids)
    return ShareResponse(**result)

# Spotify Integration Endpoints

@router.get("/spotify/authorize")
async def spotify_authorize(
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Initiate Spotify OAuth flow"""
    # Redirect to Spotify authorization URL
    from spotipy.oauth2 import SpotifyOAuth
    sp_oauth = SpotifyOAuth(
        client_id=music_service.settings.spotify_client_id,
        client_secret=music_service.settings.spotify_client_secret,
        redirect_uri=music_service.settings.spotify_redirect_uri,
        scope=music_service.settings.spotify_scopes
    )
    auth_url = sp_oauth.get_authorize_url()
    return {"auth_url": auth_url}

@router.get("/callback")
async def spotify_callback(
    code: str,
    state: Optional[str] = None,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """OAuth callback handler"""
    from spotipy.oauth2 import SpotifyOAuth
    sp_oauth = SpotifyOAuth(
        client_id=music_service.settings.spotify_client_id,
        client_secret=music_service.settings.spotify_client_secret,
        redirect_uri=music_service.settings.spotify_redirect_uri,
        scope=music_service.settings.spotify_scopes
    )
    token_info = sp_oauth.get_access_token(code)
    music_service._cache_spotify_token(current_user.id, token_info)
    return {"status": "authorized"}

@router.post("/spotify/sync/track/{spotify_id}")
async def sync_spotify_track(
    spotify_id: str,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Import track from Spotify"""
    track = music_service.sync_spotify_track(spotify_id)
    return TrackResponse.from_orm(track)

@router.post("/spotify/sync/playlist/{spotify_id}")
async def sync_spotify_playlist(
    spotify_id: str,
    music_service: MusicService = Depends(get_music_service),
    current_user: User = Depends(get_current_user)
):
    """Import playlist from Spotify"""
    playlist = music_service.sync_spotify_playlist(spotify_id, current_user.id)
    return PlaylistResponse.from_orm(playlist)