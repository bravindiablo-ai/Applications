"""
Comprehensive Music Domain Models for TRENDY App
Replaces the basic Music model with Spotify-level features
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Artist(Base):
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    bio = Column(Text)
    image_url = Column(String(500))
    spotify_id = Column(String(100), unique=True)
    apple_music_id = Column(String(100), unique=True)
    genres = Column(JSON, default=list)
    follower_count = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    popularity_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    albums = relationship("AlbumArtist", back_populates="artist")
    tracks = relationship("TrackArtist", back_populates="artist")
    followers = relationship("ArtistFollower", back_populates="artist", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_artist_spotify_id', 'spotify_id'),
        Index('idx_artist_name', 'name'),
        Index('idx_artist_popularity', 'popularity_score'),
    )
    
    def __repr__(self):
        return f"<Artist(id={self.id}, name={self.name})>"


class Album(Base):
    __tablename__ = "albums"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    release_date = Column(DateTime)
    album_type = Column(String(50), default="album")  # album, single, compilation
    cover_art_url = Column(String(500))
    spotify_id = Column(String(100), unique=True)
    apple_music_id = Column(String(100), unique=True)
    total_tracks = Column(Integer, default=0)
    label = Column(String(255))
    genres = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    artists = relationship("AlbumArtist", back_populates="album")
    tracks = relationship("Track", back_populates="album", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_album_spotify_id', 'spotify_id'),
        Index('idx_album_release_date', 'release_date'),
    )
    
    def __repr__(self):
        return f"<Album(id={self.id}, title={self.title})>"


class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    duration_ms = Column(Integer, nullable=False)
    track_number = Column(Integer)
    disc_number = Column(Integer, default=1)
    explicit = Column(Boolean, default=False)
    preview_url = Column(String(500))
    audio_url = Column(String(500))
    spotify_id = Column(String(100), unique=True)
    apple_music_id = Column(String(100), unique=True)
    isrc = Column(String(50))
    popularity_score = Column(Float, default=0.0)
    audio_features = Column(JSON, default=dict)  # tempo, key, mode, energy, danceability, etc.
    album_id = Column(Integer, ForeignKey("albums.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    album = relationship("Album", back_populates="tracks")
    artists = relationship("TrackArtist", back_populates="track")
    playlists = relationship("PlaylistTrack", back_populates="track")
    user_libraries = relationship("UserLibrary", back_populates="track")
    
    # Indexes
    __table_args__ = (
        Index('idx_track_spotify_id', 'spotify_id'),
        Index('idx_track_title', 'title'),
        Index('idx_track_popularity', 'popularity_score'),
    )
    
    def __repr__(self):
        return f"<Track(id={self.id}, title={self.title})>"


class AlbumArtist(Base):
    __tablename__ = "album_artists"
    
    id = Column(Integer, primary_key=True, index=True)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    role = Column(String(50), default="primary")  # primary, featured, composer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    album = relationship("Album", back_populates="artists")
    artist = relationship("Artist", back_populates="albums")
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('album_id', 'artist_id', name='uq_album_artist'),
    )
    
    def __repr__(self):
        return f"<AlbumArtist(album_id={self.album_id}, artist_id={self.artist_id})>"


class TrackArtist(Base):
    __tablename__ = "track_artists"
    
    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    role = Column(String(50), default="primary")  # primary, featured
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    track = relationship("Track", back_populates="artists")
    artist = relationship("Artist", back_populates="tracks")
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('track_id', 'artist_id', name='uq_track_artist'),
    )
    
    def __repr__(self):
        return f"<TrackArtist(track_id={self.track_id}, artist_id={self.artist_id})>"


class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    cover_image_url = Column(String(500))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=True)
    is_collaborative = Column(Boolean, default=False)
    spotify_id = Column(String(100), unique=True)
    follower_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="playlists")
    tracks = relationship("PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan")
    collaborators = relationship("PlaylistCollaborator", back_populates="playlist", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_playlist_user_id', 'user_id'),
        Index('idx_playlist_is_public', 'is_public'),
        Index('idx_playlist_spotify_id', 'spotify_id'),
    )
    
    def __repr__(self):
        return f"<Playlist(id={self.id}, name={self.name})>"


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    added_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position = Column(Integer, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    playlist = relationship("Playlist", back_populates="tracks")
    track = relationship("Track", back_populates="playlists")
    added_by = relationship("User")
    
    # Composite unique constraint and index
    __table_args__ = (
        UniqueConstraint('playlist_id', 'track_id', name='uq_playlist_track'),
        Index('idx_playlist_track_position', 'playlist_id', 'position'),
    )
    
    def __repr__(self):
        return f"<PlaylistTrack(playlist_id={self.playlist_id}, track_id={self.track_id}, position={self.position})>"


class PlaylistCollaborator(Base):
    __tablename__ = "playlist_collaborators"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    can_edit = Column(Boolean, default=False)
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True))
    
    # Relationships
    playlist = relationship("Playlist", back_populates="collaborators")
    user = relationship("User")
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('playlist_id', 'user_id', name='uq_playlist_collaborator'),
    )
    
    def __repr__(self):
        return f"<PlaylistCollaborator(playlist_id={self.playlist_id}, user_id={self.user_id})>"


class UserLibrary(Base):
    __tablename__ = "user_library"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"))
    album_id = Column(Integer, ForeignKey("albums.id"))
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    library_type = Column(String(50), nullable=False)  # track, album, playlist
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="library_items")
    track = relationship("Track", back_populates="user_libraries")
    album = relationship("Album")
    playlist = relationship("Playlist")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_user_library_user_type', 'user_id', 'library_type'),
        Index('idx_user_library_added_at', 'added_at'),
        # Note: Composite unique constraint on (user_id, track_id, library_type) where track_id is not null
        # This is handled in the migration, but for SQLAlchemy, we can add a check constraint if needed
    )
    
    def __repr__(self):
        return f"<UserLibrary(user_id={self.user_id}, library_type={self.library_type})>"


class PlayHistory(Base):
    __tablename__ = "play_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    played_at = Column(DateTime(timezone=True), server_default=func.now())
    play_duration_ms = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    context_type = Column(String(50))  # playlist, album, artist, search
    context_id = Column(String(100))
    device_type = Column(String(50))
    shuffle_state = Column(Boolean, default=False)
    repeat_state = Column(String(20), default="off")  # off, track, context
    
    # Relationships
    user = relationship("User", back_populates="play_history")
    track = relationship("Track")
    
    # Indexes
    __table_args__ = (
        Index('idx_play_history_user_played', 'user_id', 'played_at'),
        Index('idx_play_history_track', 'track_id'),
    )
    
    def __repr__(self):
        return f"<PlayHistory(user_id={self.user_id}, track_id={self.track_id}, played_at={self.played_at})>"


class Lyrics(Base):
    __tablename__ = "lyrics"
    
    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    language = Column(String(10), default="en")
    lyrics_text = Column(Text)
    synced_lyrics = Column(JSON, default=list)  # array of {time, text}
    source = Column(String(50))  # spotify, musixmatch, genius
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    track = relationship("Track")
    
    # Indexes and unique constraint
    __table_args__ = (
        Index('idx_lyrics_track', 'track_id'),
        Index('idx_lyrics_language', 'language'),
        UniqueConstraint('track_id', 'language', name='uq_track_language'),
    )
    
    def __repr__(self):
        return f"<Lyrics(track_id={self.track_id}, language={self.language})>"


class ArtistFollower(Base):
    __tablename__ = "artist_followers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    followed_at = Column(DateTime(timezone=True), server_default=func.now())
    notification_enabled = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="followed_artists")
    artist = relationship("Artist", back_populates="followers")
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'artist_id', name='uq_user_artist_follow'),
    )
    
    def __repr__(self):
        return f"<ArtistFollower(user_id={self.user_id}, artist_id={self.artist_id})>"


class TrackLike(Base):
    __tablename__ = "track_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    liked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="liked_tracks")
    track = relationship("Track")
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'track_id', name='uq_user_track_like'),
    )
    
    def __repr__(self):
        return f"<TrackLike(user_id={self.user_id}, track_id={self.track_id})>"


class QueueItem(Base):
    __tablename__ = "queue_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    position = Column(Integer, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    played = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="queue_items")
    track = relationship("Track")
    
    # Indexes
    __table_args__ = (
        Index('idx_queue_user_position_played', 'user_id', 'position', 'played'),
    )
    
    def __repr__(self):
        return f"<QueueItem(user_id={self.user_id}, track_id={self.track_id}, position={self.position})>"