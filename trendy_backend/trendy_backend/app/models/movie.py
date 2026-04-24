"""
Comprehensive Movie Domain Models for TRENDY App
Replaces the basic Movie model with Netflix-level features
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class MovieDetail(Base):
    __tablename__ = "movie_details"
    
    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, nullable=False)
    imdb_id = Column(String(20), unique=True)
    title = Column(String(255), nullable=False)
    original_title = Column(String(255))
    overview = Column(Text)
    tagline = Column(String(500))
    release_date = Column(DateTime)
    runtime_minutes = Column(Integer)
    budget = Column(Integer)
    revenue = Column(Integer)
    status = Column(String(50), default="released")  # released, post_production, etc.
    original_language = Column(String(10))
    spoken_languages = Column(JSON, default=list)
    poster_path = Column(String(500))
    backdrop_path = Column(String(500))
    trailer_url = Column(String(500))
    homepage = Column(String(500))
    popularity_score = Column(Float, default=0.0)
    vote_average = Column(Float, default=0.0)
    vote_count = Column(Integer, default=0)
    adult = Column(Boolean, default=False)
    genres = Column(JSON, default=list)
    production_companies = Column(JSON, default=list)
    production_countries = Column(JSON, default=list)
    is_trending = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cast = relationship("MovieCast", back_populates="movie", cascade="all, delete-orphan")
    crew = relationship("MovieCrew", back_populates="movie", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")
    watchlist_items = relationship("Watchlist", back_populates="movie", cascade="all, delete-orphan")
    viewing_history = relationship("ViewingHistory", back_populates="movie", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_movie_tmdb_id', 'tmdb_id'),
        Index('idx_movie_imdb_id', 'imdb_id'),
        Index('idx_movie_title', 'title'),
        Index('idx_movie_release_date', 'release_date'),
        Index('idx_movie_popularity', 'popularity_score'),
    )
    
    def __repr__(self):
        return f"<MovieDetail(id={self.id}, title={self.title}, tmdb_id={self.tmdb_id})>"


class TVShow(Base):
    __tablename__ = "tv_shows"
    
    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    original_name = Column(String(255))
    overview = Column(Text)
    first_air_date = Column(DateTime)
    last_air_date = Column(DateTime)
    status = Column(String(50), default="returning")  # returning, ended, canceled
    type = Column(String(50), default="scripted")  # scripted, reality, etc.
    number_of_seasons = Column(Integer, default=0)
    number_of_episodes = Column(Integer, default=0)
    episode_run_time = Column(JSON, default=list)  # array of integers
    poster_path = Column(String(500))
    backdrop_path = Column(String(500))
    homepage = Column(String(500))
    popularity_score = Column(Float, default=0.0)
    vote_average = Column(Float, default=0.0)
    vote_count = Column(Integer, default=0)
    adult = Column(Boolean, default=False)
    genres = Column(JSON, default=list)
    networks = Column(JSON, default=list)
    production_companies = Column(JSON, default=list)
    created_by = Column(JSON, default=list)
    in_production = Column(Boolean, default=False)
    languages = Column(JSON, default=list)
    origin_country = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    seasons = relationship("Season", back_populates="tv_show", cascade="all, delete-orphan")
    cast = relationship("TVShowCast", back_populates="tv_show", cascade="all, delete-orphan")
    crew = relationship("TVShowCrew", back_populates="tv_show", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="tv_show", cascade="all, delete-orphan")
    watchlist_items = relationship("Watchlist", back_populates="tv_show", cascade="all, delete-orphan")
    viewing_history = relationship("ViewingHistory", back_populates="tv_show", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_tv_show_tmdb_id', 'tmdb_id'),
        Index('idx_tv_show_name', 'name'),
        Index('idx_tv_show_first_air_date', 'first_air_date'),
        Index('idx_tv_show_popularity', 'popularity_score'),
    )
    
    def __repr__(self):
        return f"<TVShow(id={self.id}, name={self.name}, tmdb_id={self.tmdb_id})>"


class Season(Base):
    __tablename__ = "seasons"
    
    id = Column(Integer, primary_key=True, index=True)
    tv_show_id = Column(Integer, ForeignKey("tv_shows.id"), nullable=False)
    tmdb_id = Column(Integer, unique=True, nullable=False)
    season_number = Column(Integer, nullable=False)
    name = Column(String(255))
    overview = Column(Text)
    air_date = Column(DateTime)
    episode_count = Column(Integer, default=0)
    poster_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tv_show = relationship("TVShow", back_populates="seasons")
    episodes = relationship("Episode", back_populates="season", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_season_tv_show_season', 'tv_show_id', 'season_number'),
        UniqueConstraint('tv_show_id', 'season_number', name='uq_tv_show_season'),
    )
    
    def __repr__(self):
        return f"<Season(id={self.id}, tv_show_id={self.tv_show_id}, season_number={self.season_number})>"


class Episode(Base):
    __tablename__ = "episodes"
    
    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    tmdb_id = Column(Integer, unique=True, nullable=False)
    episode_number = Column(Integer, nullable=False)
    name = Column(String(255))
    overview = Column(Text)
    air_date = Column(DateTime)
    runtime_minutes = Column(Integer)
    still_path = Column(String(500))
    vote_average = Column(Float, default=0.0)
    vote_count = Column(Integer, default=0)
    production_code = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    season = relationship("Season", back_populates="episodes")
    viewing_history = relationship("ViewingHistory", back_populates="episode", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_episode_season_episode', 'season_id', 'episode_number'),
        UniqueConstraint('season_id', 'episode_number', name='uq_season_episode'),
    )
    
    def __repr__(self):
        return f"<Episode(id={self.id}, season_id={self.season_id}, episode_number={self.episode_number})>"


class Person(Base):
    __tablename__ = "people"
    
    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    biography = Column(Text)
    birthday = Column(DateTime)
    deathday = Column(DateTime)
    place_of_birth = Column(String(255))
    profile_path = Column(String(500))
    known_for_department = Column(String(50))
    popularity_score = Column(Float, default=0.0)
    adult = Column(Boolean, default=False)
    imdb_id = Column(String(20))
    homepage = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    movie_cast_credits = relationship("MovieCast", back_populates="person", cascade="all, delete-orphan")
    movie_crew_credits = relationship("MovieCrew", back_populates="person", cascade="all, delete-orphan")
    tv_show_cast_credits = relationship("TVShowCast", back_populates="person", cascade="all, delete-orphan")
    tv_show_crew_credits = relationship("TVShowCrew", back_populates="person", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_person_tmdb_id', 'tmdb_id'),
        Index('idx_person_name', 'name'),
        Index('idx_person_popularity', 'popularity_score'),
    )
    
    def __repr__(self):
        return f"<Person(id={self.id}, name={self.name}, tmdb_id={self.tmdb_id})>"


class MovieCast(Base):
    __tablename__ = "movie_cast"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movie_details.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False)
    character_name = Column(String(255))
    order = Column(Integer, default=0)
    credit_id = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    movie = relationship("MovieDetail", back_populates="cast")
    person = relationship("Person", back_populates="movie_cast_credits")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('movie_id', 'person_id', 'character_name', name='uq_movie_cast'),
    )
    
    def __repr__(self):
        return f"<MovieCast(movie_id={self.movie_id}, person_id={self.person_id}, character_name={self.character_name})>"


class MovieCrew(Base):
    __tablename__ = "movie_crew"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movie_details.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False)
    job = Column(String(100))
    department = Column(String(100))
    credit_id = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    movie = relationship("MovieDetail", back_populates="crew")
    person = relationship("Person", back_populates="movie_crew_credits")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('movie_id', 'person_id', 'job', name='uq_movie_crew'),
    )
    
    def __repr__(self):
        return f"<MovieCrew(movie_id={self.movie_id}, person_id={self.person_id}, job={self.job})>"


class TVShowCast(Base):
    __tablename__ = "tv_show_cast"
    
    id = Column(Integer, primary_key=True, index=True)
    tv_show_id = Column(Integer, ForeignKey("tv_shows.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False)
    character_name = Column(String(255))
    order = Column(Integer, default=0)
    credit_id = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tv_show = relationship("TVShow", back_populates="cast")
    person = relationship("Person", back_populates="tv_show_cast_credits")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('tv_show_id', 'person_id', 'character_name', name='uq_tv_show_cast'),
    )
    
    def __repr__(self):
        return f"<TVShowCast(tv_show_id={self.tv_show_id}, person_id={self.person_id}, character_name={self.character_name})>"


class TVShowCrew(Base):
    __tablename__ = "tv_show_crew"
    
    id = Column(Integer, primary_key=True, index=True)
    tv_show_id = Column(Integer, ForeignKey("tv_shows.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False)
    job = Column(String(100))
    department = Column(String(100))
    credit_id = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tv_show = relationship("TVShow", back_populates="crew")
    person = relationship("Person", back_populates="tv_show_crew_credits")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('tv_show_id', 'person_id', 'job', name='uq_tv_show_crew'),
    )
    
    def __repr__(self):
        return f"<TVShowCrew(tv_show_id={self.tv_show_id}, person_id={self.person_id}, job={self.job})>"


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movie_details.id"))
    tv_show_id = Column(Integer, ForeignKey("tv_shows.id"))
    rating = Column(Integer, nullable=False)  # 1-10
    review_text = Column(Text)
    is_spoiler = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    movie = relationship("MovieDetail", back_populates="reviews")
    tv_show = relationship("TVShow", back_populates="reviews")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_review_user_movie', 'user_id', 'movie_id'),
        Index('idx_review_user_tv_show', 'user_id', 'tv_show_id'),
        CheckConstraint('(movie_id IS NOT NULL AND tv_show_id IS NULL) OR (movie_id IS NULL AND tv_show_id IS NOT NULL)', name='chk_review_content'),
    )
    
    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, rating={self.rating})>"


class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movie_details.id"))
    tv_show_id = Column(Integer, ForeignKey("tv_shows.id"))
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    priority = Column(Integer, default=3)  # 1-5
    notes = Column(Text)
    
    # Relationships
    user_profile = relationship("UserProfile", back_populates="watchlist_items")
    movie = relationship("MovieDetail", back_populates="watchlist_items")
    tv_show = relationship("TVShow", back_populates="watchlist_items")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_watchlist_user_movie', 'user_profile_id', 'movie_id'),
        Index('idx_watchlist_user_tv_show', 'user_profile_id', 'tv_show_id'),
        CheckConstraint('(movie_id IS NOT NULL AND tv_show_id IS NULL) OR (movie_id IS NULL AND tv_show_id IS NOT NULL)', name='chk_watchlist_content'),
    )
    
    def __repr__(self):
        return f"<Watchlist(id={self.id}, user_profile_id={self.user_profile_id})>"


class ViewingHistory(Base):
    __tablename__ = "viewing_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movie_details.id"))
    tv_show_id = Column(Integer, ForeignKey("tv_shows.id"))
    episode_id = Column(Integer, ForeignKey("episodes.id"))
    watched_at = Column(DateTime(timezone=True), server_default=func.now())
    progress_seconds = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    watch_count = Column(Integer, default=1)
    last_position_seconds = Column(Integer, default=0)
    device_type = Column(String(50))
    quality_setting = Column(String(20))
    
    # Relationships
    user_profile = relationship("UserProfile", back_populates="viewing_history")
    movie = relationship("MovieDetail", back_populates="viewing_history")
    tv_show = relationship("TVShow", back_populates="viewing_history")
    episode = relationship("Episode", back_populates="viewing_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_viewing_history_user_watched', 'user_profile_id', 'watched_at'),
        Index('idx_viewing_history_user_movie', 'user_profile_id', 'movie_id'),
        Index('idx_viewing_history_user_episode', 'user_profile_id', 'episode_id'),
    )
    
    def __repr__(self):
        return f"<ViewingHistory(id={self.id}, user_profile_id={self.user_profile_id}, watched_at={self.watched_at})>"


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    profile_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500))
    is_kids_profile = Column(Boolean, default=False)
    maturity_rating = Column(String(10), default="G")  # G, PG, PG13, R, NC17
    language_preference = Column(String(10), default="en")
    autoplay_next = Column(Boolean, default=True)
    autoplay_previews = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profiles")
    watchlist_items = relationship("Watchlist", back_populates="user_profile", cascade="all, delete-orphan")
    viewing_history = relationship("ViewingHistory", back_populates="user_profile", cascade="all, delete-orphan")
    watch_parties_created = relationship("WatchParty", back_populates="host_profile", cascade="all, delete-orphan")
    watch_party_participants = relationship("WatchPartyParticipant", back_populates="user_profile", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_profile_user_name', 'user_id', 'profile_name'),
        UniqueConstraint('user_id', 'profile_name', name='uq_user_profile_name'),
    )
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, profile_name={self.profile_name})>"


class WatchParty(Base):
    __tablename__ = "watch_parties"
    
    id = Column(Integer, primary_key=True, index=True)
    host_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movie_details.id"))
    tv_show_id = Column(Integer, ForeignKey("tv_shows.id"))
    episode_id = Column(Integer, ForeignKey("episodes.id"))
    party_code = Column(String(6), unique=True, nullable=False)
    status = Column(String(20), default="waiting")  # waiting, playing, paused, ended
    current_position_seconds = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    max_participants = Column(Integer, default=10)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    host_profile = relationship("UserProfile", back_populates="watch_parties_created")
    movie = relationship("MovieDetail")
    tv_show = relationship("TVShow")
    episode = relationship("Episode")
    participants = relationship("WatchPartyParticipant", back_populates="watch_party", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_watch_party_code', 'party_code'),
        Index('idx_watch_party_host', 'host_profile_id'),
        Index('idx_watch_party_status', 'status'),
    )
    
    def __repr__(self):
        return f"<WatchParty(id={self.id}, party_code={self.party_code}, status={self.status})>"


class WatchPartyParticipant(Base):
    __tablename__ = "watch_party_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    watch_party_id = Column(Integer, ForeignKey("watch_parties.id"), nullable=False)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    watch_party = relationship("WatchParty", back_populates="participants")
    user_profile = relationship("UserProfile", back_populates="watch_party_participants")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('watch_party_id', 'user_profile_id', name='uq_watch_party_participant'),
    )
    
    def __repr__(self):
        return f"<WatchPartyParticipant(watch_party_id={self.watch_party_id}, user_profile_id={self.user_profile_id})>"


class VideoQuality(Base):
    __tablename__ = "video_qualities"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movie_details.id"))
    episode_id = Column(Integer, ForeignKey("episodes.id"))
    quality_label = Column(String(20), nullable=False)  # 360p, 480p, 720p, 1080p, 4K
    video_url = Column(String(500), nullable=False)
    file_size_mb = Column(Float, default=0.0)
    bitrate_kbps = Column(Integer, default=0)
    codec = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    movie = relationship("MovieDetail")
    episode = relationship("Episode")
    
    # Indexes
    __table_args__ = (
        Index('idx_video_quality_movie', 'movie_id', 'quality_label'),
        Index('idx_video_quality_episode', 'episode_id', 'quality_label'),
    )
    
    def __repr__(self):
        return f"<VideoQuality(id={self.id}, quality_label={self.quality_label})>"