from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from .user import UserResponse

class MusicBase(BaseModel):
    title: str
    artist: str
    genre: Optional[str] = None
    year: int

class MusicCreate(MusicBase):
    pass

class MusicResponse(MusicBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# Alias MusicOut to MusicResponse for compatibility
MusicOut = MusicResponse

# Artist Schemas
class ArtistBase(BaseModel):
    name: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
    genres: Optional[List[str]] = None

class ArtistCreate(ArtistBase):
    pass

class ArtistResponse(ArtistBase):
    id: int
    spotify_id: Optional[str] = None
    follower_count: int
    verified: bool
    popularity_score: float
    is_following: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)

class ArtistDetail(ArtistResponse):
    albums: List['AlbumResponse']
    top_tracks: List['TrackResponse']
    similar_artists: List[ArtistResponse]

# Album Schemas
class AlbumBase(BaseModel):
    title: str
    release_date: datetime
    album_type: str = Field(..., pattern=r'^(album|single|compilation)$')
    cover_art_url: Optional[str] = None
    genres: Optional[List[str]] = None

class AlbumCreate(AlbumBase):
    pass

class AlbumResponse(AlbumBase):
    id: int
    spotify_id: Optional[str] = None
    total_tracks: int
    artists: List[ArtistResponse]
    is_in_library: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)

class AlbumDetail(AlbumResponse):
    tracks: List['TrackResponse']

# Track Schemas
class TrackBase(BaseModel):
    title: str
    duration_ms: int = Field(gt=0)
    explicit: bool
    preview_url: Optional[str] = None
    
    @validator('duration_ms')
    def duration_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('duration_ms must be positive')
        return v

class TrackCreate(TrackBase):
    pass

class TrackResponse(TrackBase):
    id: int
    spotify_id: Optional[str] = None
    album: AlbumResponse
    artists: List[ArtistResponse]
    popularity_score: float
    is_liked: Optional[bool] = None
    is_in_library: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)

class TrackDetail(TrackResponse):
    audio_features: Optional['AudioFeaturesResponse'] = None
    lyrics_available: bool

# Playlist Schemas
class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_public: bool
    is_collaborative: bool

class PlaylistCreate(PlaylistBase):
    pass

class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_public: Optional[bool] = None
    is_collaborative: Optional[bool] = None

class PlaylistResponse(PlaylistBase):
    id: int
    owner: UserResponse
    track_count: int
    follower_count: int
    collaborators: List[UserResponse]
    is_owner: Optional[bool] = None
    can_edit: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)

class PlaylistDetail(PlaylistResponse):
    tracks: List[Dict[str, Any]]  # List of {track: TrackResponse, position: int, added_at: datetime}

# Request Schemas
class SearchRequest(BaseModel):
    query: str
    search_type: str = Field(..., pattern=r'^(track|artist|album|playlist)$')
    filters: Optional[Dict[str, Any]] = None
    limit: int = Field(20, gt=0, le=100)
    offset: int = Field(0, ge=0)

class SearchFilters(BaseModel):
    genre: Optional[str] = None
    year_min: Optional[int] = Field(None, ge=1900, le=2100)
    year_max: Optional[int] = Field(None, ge=1900, le=2100)
    tempo_min: Optional[float] = Field(None, ge=0, le=300)
    tempo_max: Optional[float] = Field(None, ge=0, le=300)
    mood: Optional[str] = None
    explicit: Optional[bool] = None
    popularity_min: Optional[float] = Field(None, ge=0, le=100)
    
    @validator('year_max')
    def year_max_must_be_greater_or_equal(cls, v, values):
        if 'year_min' in values and values['year_min'] is not None and v is not None and v < values['year_min']:
            raise ValueError('year_max must be greater than or equal to year_min')
        return v
    
    @validator('tempo_max')
    def tempo_max_must_be_greater_or_equal(cls, v, values):
        if 'tempo_min' in values and values['tempo_min'] is not None and v is not None and v < values['tempo_min']:
            raise ValueError('tempo_max must be greater than or equal to tempo_min')
        return v

class PlaylistTrackAdd(BaseModel):
    track_ids: List[int] = Field(..., min_items=1)
    position: Optional[int] = Field(None, ge=0)

class PlaylistTrackRemove(BaseModel):
    track_ids: List[int] = Field(..., min_items=1)

class TrackPosition(BaseModel):
    track_id: int
    new_position: int = Field(ge=0)

class PlaylistReorder(BaseModel):
    track_positions: List[TrackPosition] = Field(..., min_items=1)

class CollaboratorAdd(BaseModel):
    user_id: int
    can_edit: bool

class PlayHistoryCreate(BaseModel):
    track_id: int
    play_duration_ms: int = Field(gt=0)
    completed: bool
    context_type: str = Field(..., pattern=r'^(playlist|album|artist|search)$')
    context_id: Optional[str] = None
    device_type: Optional[str] = None

class QueueAdd(BaseModel):
    track_id: int
    position: Optional[int] = Field(None, ge=0)

class LyricsCreate(BaseModel):
    track_id: int
    lyrics_text: str
    language: str = Field(..., min_length=2, max_length=5)
    synced_lyrics: Optional[Dict[str, Any]] = None

class ShareRequest(BaseModel):
    item_id: int
    item_type: str = Field(..., pattern=r'^(track|playlist)$')
    share_type: str = Field(..., pattern=r'^(link|message)$')
    recipient_ids: Optional[List[int]] = None

# Response Schemas
class SearchResponse(BaseModel):
    results: List[Union[TrackResponse, ArtistResponse, AlbumResponse, PlaylistResponse]]
    total: int
    query: str
    filters: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)

class RecommendationsResponse(BaseModel):
    tracks: List[TrackResponse]
    seed_type: str
    seed_id: str
    algorithm: str
    
    model_config = ConfigDict(from_attributes=True)

class LibraryResponse(BaseModel):
    items: List[Union[TrackResponse, AlbumResponse, PlaylistResponse]]
    total: int
    library_type: str
    
    model_config = ConfigDict(from_attributes=True)

class PlayHistoryResponse(BaseModel):
    track: TrackResponse
    played_at: datetime
    play_duration_ms: int
    completed: bool
    context_type: str
    
    model_config = ConfigDict(from_attributes=True)

class QueueItem(BaseModel):
    queue_item_id: int
    track: TrackResponse
    position: int
    added_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class QueueResponse(BaseModel):
    items: List[QueueItem]
    total: int
    
    model_config = ConfigDict(from_attributes=True)

class LyricsResponse(BaseModel):
    track_id: int
    language: str
    lyrics_text: str
    synced_lyrics: Optional[Dict[str, Any]] = None
    source: str
    verified: bool
    
    model_config = ConfigDict(from_attributes=True)

class AudioFeaturesResponse(BaseModel):
    track_id: int
    tempo: float
    key: int
    mode: int
    time_signature: int
    energy: float
    danceability: float
    valence: float
    acousticness: float
    instrumentalness: float
    liveness: float
    speechiness: float
    loudness: float
    
    model_config = ConfigDict(from_attributes=True)

class PlayStatsResponse(BaseModel):
    time_range: str
    top_tracks: List[TrackResponse]
    top_artists: List[ArtistResponse]
    top_genres: List[str]
    total_plays: int
    total_duration_ms: int
    
    model_config = ConfigDict(from_attributes=True)

class ShareResponse(BaseModel):
    share_url: str
    share_type: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
