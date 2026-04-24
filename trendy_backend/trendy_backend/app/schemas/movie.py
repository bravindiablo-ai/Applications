from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# Base Schemas
class MovieBase(BaseModel):
    title: str
    overview: str
    release_date: datetime
    runtime_minutes: int
    genres: List[str]
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None

class MovieCreate(MovieBase):
    tmdb_id: int

class MovieResponse(MovieBase):
    id: int
    tmdb_id: Optional[int] = None
    imdb_id: Optional[str] = None
    popularity_score: float
    vote_average: float
    vote_count: int
    trailer_url: Optional[str] = None
    is_in_watchlist: Optional[bool] = None
    user_rating: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)

class MovieDetail(MovieResponse):
    cast: List['CastMember']
    crew: List['CrewMember']
    similar_movies: List[MovieResponse]
    reviews_summary: Dict[str, Any]
    available_qualities: List['VideoQualityResponse']

class TVShowBase(BaseModel):
    name: str
    overview: str
    first_air_date: datetime
    number_of_seasons: int
    number_of_episodes: int
    genres: List[str]
    poster_path: Optional[str] = None

class TVShowCreate(TVShowBase):
    tmdb_id: int

class TVShowResponse(TVShowBase):
    id: int
    tmdb_id: Optional[int] = None
    status: str
    popularity_score: float
    vote_average: float
    is_in_watchlist: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)

class TVShowDetail(TVShowResponse):
    seasons: List['SeasonResponse']
    cast: List['CastMember']
    crew: List['CrewMember']
    similar_shows: List[TVShowResponse]

class SeasonBase(BaseModel):
    season_number: int
    name: str
    overview: str
    air_date: datetime
    episode_count: int

class SeasonResponse(SeasonBase):
    id: int
    poster_path: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class SeasonDetail(SeasonResponse):
    episodes: List['EpisodeResponse']

class EpisodeBase(BaseModel):
    episode_number: int
    name: str
    overview: str
    air_date: datetime
    runtime_minutes: int

class EpisodeResponse(EpisodeBase):
    id: int
    still_path: Optional[str] = None
    vote_average: float
    
    model_config = ConfigDict(from_attributes=True)

class PersonBase(BaseModel):
    name: str
    biography: Optional[str] = None
    birthday: Optional[datetime] = None
    place_of_birth: Optional[str] = None
    profile_path: Optional[str] = None

class PersonResponse(PersonBase):
    id: int
    tmdb_id: Optional[int] = None
    known_for_department: str
    popularity_score: float
    
    model_config = ConfigDict(from_attributes=True)

class PersonDetail(PersonResponse):
    movie_credits: List[Dict[str, Any]]
    tv_credits: List[Dict[str, Any]]

class CastMember(BaseModel):
    person_id: int
    name: str
    character_name: str
    profile_path: Optional[str] = None
    order: int

class CrewMember(BaseModel):
    person_id: int
    name: str
    job: str
    department: str
    profile_path: Optional[str] = None

# Request Schemas
class SearchRequest(BaseModel):
    query: str
    content_type: str = Field(..., pattern=r'^(movie|tv|person)$')
    filters: Optional[Dict[str, Any]] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

class SearchFilters(BaseModel):
    genre_ids: Optional[List[int]] = None
    year: Optional[int] = Field(None, ge=1900, le=2100)
    min_rating: Optional[float] = Field(None, ge=0, le=10)
    max_rating: Optional[float] = Field(None, ge=0, le=10)
    language: Optional[str] = None
    sort_by: Optional[str] = None
    
    @validator('max_rating')
    def max_rating_must_be_greater_or_equal(cls, v, values):
        if 'min_rating' in values and values['min_rating'] is not None and v is not None and v < values['min_rating']:
            raise ValueError('max_rating must be greater than or equal to min_rating')
        return v

class WatchlistAdd(BaseModel):
    movie_id: Optional[int] = None
    tv_show_id: Optional[int] = None
    priority: int = Field(1, ge=1, le=5)
    notes: Optional[str] = None

class WatchlistUpdate(BaseModel):
    priority: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None

class ViewingProgressUpdate(BaseModel):
    progress_seconds: int = Field(0, ge=0)
    duration_seconds: int = Field(0, ge=0)
    completed: bool
    device_type: Optional[str] = None
    quality_setting: Optional[str] = None

class ReviewCreate(BaseModel):
    movie_id: Optional[int] = None
    tv_show_id: Optional[int] = None
    rating: float = Field(..., ge=1, le=10)
    review_text: str
    is_spoiler: bool = False

class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1, le=10)
    review_text: Optional[str] = None
    is_spoiler: Optional[bool] = None

class ProfileCreate(BaseModel):
    profile_name: str
    avatar_url: Optional[str] = None
    is_kids_profile: bool = False
    maturity_rating: str = Field(..., pattern=r'^(G|PG|PG13|R|NC17)$')

class ProfileUpdate(BaseModel):
    profile_name: Optional[str] = None
    avatar_url: Optional[str] = None
    autoplay_next: Optional[bool] = None
    autoplay_previews: Optional[bool] = None
    language_preference: Optional[str] = None

class WatchPartyCreate(BaseModel):
    movie_id: Optional[int] = None
    tv_show_id: Optional[int] = None
    episode_id: Optional[int] = None
    max_participants: int = Field(1, ge=1, le=10)
    is_public: bool = False

class WatchPartyJoin(BaseModel):
    party_code: str

class WatchPartyUpdate(BaseModel):
    position_seconds: int = Field(0, ge=0)
    status: str = Field(..., pattern=r'^(playing|paused)$')

class VideoQualityCreate(BaseModel):
    movie_id: Optional[int] = None
    episode_id: Optional[int] = None
    quality_label: str
    video_url: str
    file_size_mb: float = Field(0, ge=0)
    bitrate_kbps: int = Field(0, ge=0)
    codec: str

# Response Schemas
class SearchResponse(BaseModel):
    results: List[Union[MovieResponse, TVShowResponse, PersonResponse]]
    total_results: int
    total_pages: int
    page: int
    
    model_config = ConfigDict(from_attributes=True)

class RecommendationsResponse(BaseModel):
    items: List[Union[MovieResponse, TVShowResponse]]
    recommendation_type: str
    seed_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class WatchlistResponse(BaseModel):
    items: List[Union[MovieResponse, TVShowResponse]]
    total: int
    content_type: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ViewingHistoryResponse(BaseModel):
    item: Union[MovieResponse, TVShowResponse, EpisodeResponse]
    watched_at: datetime
    progress_seconds: int
    duration_seconds: int
    completed: bool
    progress_percent: float
    
    model_config = ConfigDict(from_attributes=True)

class ContinueWatchingResponse(BaseModel):
    items: List[ViewingHistoryResponse]
    total: int
    
    model_config = ConfigDict(from_attributes=True)

class ReviewResponse(BaseModel):
    id: int
    user: Dict[str, Any]
    movie_id: Optional[int] = None
    tv_show_id: Optional[int] = None
    rating: float
    review_text: str
    is_spoiler: bool
    helpful_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProfileResponse(BaseModel):
    id: int
    profile_name: str
    avatar_url: Optional[str] = None
    is_kids_profile: bool
    maturity_rating: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class WatchPartyResponse(BaseModel):
    id: int
    party_code: str
    host_profile: Dict[str, Any]
    content: Union[MovieResponse, EpisodeResponse]
    status: str
    current_position_seconds: int
    participants: List[Dict[str, Any]]
    max_participants: int
    is_public: bool
    started_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class WatchPartyParticipantResponse(BaseModel):
    id: int
    user_profile: Dict[str, Any]
    joined_at: datetime
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class VideoQualityResponse(BaseModel):
    id: int
    quality_label: str
    video_url: str
    file_size_mb: float
    bitrate_kbps: int
    codec: str
    
    model_config = ConfigDict(from_attributes=True)

class WatchStatsResponse(BaseModel):
    total_watch_time_hours: float
    total_movies_watched: int
    total_episodes_watched: int
    favorite_genres: List[str]
    top_actors: List[str]
    watch_streak_days: int
    
    model_config = ConfigDict(from_attributes=True)

class GenreResponse(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class TrailerResponse(BaseModel):
    key: str
    name: str
    site: str
    type: str
    official: bool
    
    model_config = ConfigDict(from_attributes=True)
