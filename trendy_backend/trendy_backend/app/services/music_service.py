"""
Music Service for TRENDY App
Provides comprehensive music functionality with Spotify/Apple Music integration
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union

import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_, or_, text

from app.core.config import get_settings
from app.services.cache_service import CacheService
from app.services.personalization_service import PersonalizationService
from app.models.music import (
    Artist, Album, Track, AlbumArtist, TrackArtist, Playlist, PlaylistTrack,
    PlaylistCollaborator, UserLibrary, PlayHistory, Lyrics, ArtistFollower,
    TrackLike, QueueItem
)

logger = logging.getLogger(__name__)

class MusicService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.cache_service = CacheService()
        self.personalization_service = PersonalizationService(db)

    # Spotify Integration Methods

    def _get_spotify_client(self, user_id: Optional[int] = None) -> spotipy.Spotify:
        """Initialize Spotify client with user auth or client credentials"""
        if user_id:
            # User-specific client with OAuth
            token_info = self._get_cached_spotify_token(user_id)
            if token_info:
                return spotipy.Spotify(auth=token_info['access_token'])
            else:
                # Fall back to client credentials
                pass
        
        # Client credentials flow for general access
        if self.settings.has_spotify:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=self.settings.spotify_client_id,
                client_secret=self.settings.spotify_client_secret
            )
            return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        else:
            raise ValueError("Spotify credentials not configured")

    def _cache_spotify_token(self, user_id: int, token_info: dict):
        """Cache user's Spotify OAuth tokens in Redis"""
        key = f"spotify_token:{user_id}"
        # Since CacheService is async, we'll use a sync approach for now
        # In production, this should be async
        import redis
        r = redis.Redis.from_url(self.settings.redis_url)
        r.setex(key, 3600, json.dumps(token_info))  # 1 hour TTL

    def _get_cached_spotify_token(self, user_id: int) -> Optional[dict]:
        """Retrieve cached tokens"""
        import redis
        r = redis.Redis.from_url(self.settings.redis_url)
        token_data = r.get(f"spotify_token:{user_id}")
        if token_data:
            return json.loads(token_data)
        return None

    def sync_spotify_track(self, spotify_id: str) -> Track:
        """Fetch track from Spotify API and sync to database"""
        try:
            sp = self._get_spotify_client()
            track_data = sp.track(spotify_id)
            
            # Check if track exists
            track = self.db.query(Track).filter(Track.spotify_id == spotify_id).first()
            if track:
                return track
            
            # Create track
            track = Track(
                title=track_data['name'],
                duration_ms=track_data['duration_ms'],
                explicit=track_data['explicit'],
                preview_url=track_data.get('preview_url'),
                spotify_id=spotify_id,
                isrc=track_data.get('external_ids', {}).get('isrc'),
                popularity_score=track_data.get('popularity', 0),
                audio_features=self._get_audio_features(sp, spotify_id)
            )
            
            # Sync album
            album = self.sync_spotify_album(track_data['album']['id'])
            track.album = album
            
            # Sync artists
            for artist_data in track_data['artists']:
                artist = self.sync_spotify_artist(artist_data['id'])
                track_artist = TrackArtist(track=track, artist=artist, role='primary')
                self.db.add(track_artist)
            
            self.db.add(track)
            self.db.commit()
            self.db.refresh(track)
            
            # Cache the track
            self._cache_music_data(f"track:{track.id}", track, self.settings.music_cache_ttl)
            
            return track
        except Exception as e:
            logger.error(f"Error syncing Spotify track {spotify_id}: {str(e)}")
            raise

    def sync_spotify_album(self, spotify_id: str) -> Album:
        """Fetch album from Spotify API and sync to database"""
        try:
            sp = self._get_spotify_client()
            album_data = sp.album(spotify_id)
            
            album = self.db.query(Album).filter(Album.spotify_id == spotify_id).first()
            if album:
                return album
            
            album = Album(
                title=album_data['name'],
                release_date=album_data['release_date'],
                album_type=album_data['album_type'],
                cover_art_url=album_data['images'][0]['url'] if album_data['images'] else None,
                spotify_id=spotify_id,
                total_tracks=album_data['total_tracks'],
                genres=album_data.get('genres', [])
            )
            
            # Sync artists
            for artist_data in album_data['artists']:
                artist = self.sync_spotify_artist(artist_data['id'])
                album_artist = AlbumArtist(album=album, artist=artist, role='primary')
                self.db.add(album_artist)
            
            self.db.add(album)
            self.db.commit()
            self.db.refresh(album)
            
            self._cache_music_data(f"album:{album.id}", album, self.settings.music_cache_ttl)
            
            return album
        except Exception as e:
            logger.error(f"Error syncing Spotify album {spotify_id}: {str(e)}")
            raise

    def sync_spotify_artist(self, spotify_id: str) -> Artist:
        """Fetch artist from Spotify API and sync to database"""
        try:
            sp = self._get_spotify_client()
            artist_data = sp.artist(spotify_id)
            
            artist = self.db.query(Artist).filter(Artist.spotify_id == spotify_id).first()
            if artist:
                return artist
            
            artist = Artist(
                name=artist_data['name'],
                bio="",  # Spotify doesn't provide bio
                image_url=artist_data['images'][0]['url'] if artist_data['images'] else None,
                spotify_id=spotify_id,
                genres=artist_data.get('genres', []),
                popularity_score=artist_data.get('popularity', 0),
                verified=False  # Assume not verified unless checked
            )
            
            self.db.add(artist)
            self.db.commit()
            self.db.refresh(artist)
            
            self._cache_music_data(f"artist:{artist.id}", artist, self.settings.music_cache_ttl)
            
            return artist
        except Exception as e:
            logger.error(f"Error syncing Spotify artist {spotify_id}: {str(e)}")
            raise

    def sync_spotify_playlist(self, spotify_id: str, user_id: int) -> Playlist:
        """Import Spotify playlist"""
        try:
            sp = self._get_spotify_client(user_id)
            playlist_data = sp.playlist(spotify_id)
            
            playlist = self.db.query(Playlist).filter(Playlist.spotify_id == spotify_id).first()
            if playlist:
                return playlist
            
            playlist = Playlist(
                name=playlist_data['name'],
                description=playlist_data.get('description'),
                cover_image_url=playlist_data['images'][0]['url'] if playlist_data['images'] else None,
                user_id=user_id,
                is_public=playlist_data['public'],
                is_collaborative=playlist_data['collaborative'],
                spotify_id=spotify_id
            )
            
            self.db.add(playlist)
            self.db.commit()
            self.db.refresh(playlist)
            
            # Add tracks
            tracks_data = sp.playlist_tracks(spotify_id)
            position = 0
            for item in tracks_data['items']:
                track = self.sync_spotify_track(item['track']['id'])
                playlist_track = PlaylistTrack(
                    playlist=playlist,
                    track=track,
                    added_by_user_id=user_id,
                    position=position
                )
                self.db.add(playlist_track)
                position += 1
            
            self.db.commit()
            
            return playlist
        except Exception as e:
            logger.error(f"Error syncing Spotify playlist {spotify_id}: {str(e)}")
            raise

    # Search Methods

    def search_tracks(self, query: str, filters: dict, limit: int) -> List[Track]:
        """Search tracks with filters"""
        try:
            # Check cache first
            query_hash = hashlib.md5(f"{query}:{filters}:{limit}".encode()).hexdigest()
            cache_key = f"music:search:tracks:{query_hash}"
            cached = self._get_cached_music_data(cache_key)
            if cached:
                return cached
            
            # Build query
            q = self.db.query(Track)
            
            if query:
                q = q.filter(or_(
                    Track.title.ilike(f"%{query}%"),
                    Track.artists.any(Artist.name.ilike(f"%{query}%"))
                ))
            
            # Apply filters
            if filters.get('genre'):
                q = q.filter(Track.album.has(Album.genres.contains([filters['genre']])))
            if filters.get('year_min'):
                q = q.filter(Track.album.has(func.extract('year', Album.release_date) >= filters['year_min']))
            if filters.get('year_max'):
                q = q.filter(Track.album.has(func.extract('year', Album.release_date) <= filters['year_max']))
            if filters.get('explicit') is not None:
                q = q.filter(Track.explicit == filters['explicit'])
            if filters.get('tempo_min') or filters.get('tempo_max'):
                # Filter by audio features
                if filters.get('tempo_min'):
                    q = q.filter(Track.audio_features['tempo'].astext.cast(float) >= filters['tempo_min'])
                if filters.get('tempo_max'):
                    q = q.filter(Track.audio_features['tempo'].astext.cast(float) <= filters['tempo_max'])
            
            results = q.limit(limit).all()
            
            # Cache results
            self._cache_music_data(cache_key, results, self.settings.music_cache_ttl)
            
            return results
        except Exception as e:
            logger.error(f"Error searching tracks: {str(e)}")
            return []

    def search_artists(self, query: str, limit: int) -> List[Artist]:
        """Search artists"""
        try:
            cache_key = f"music:search:artists:{hashlib.md5(query.encode()).hexdigest()}"
            cached = self._get_cached_music_data(cache_key)
            if cached:
                return cached
            
            results = self.db.query(Artist).filter(
                Artist.name.ilike(f"%{query}%")
            ).limit(limit).all()
            
            self._cache_music_data(cache_key, results, self.settings.music_cache_ttl)
            return results
        except Exception as e:
            logger.error(f"Error searching artists: {str(e)}")
            return []

    def search_albums(self, query: str, limit: int) -> List[Album]:
        """Search albums"""
        try:
            cache_key = f"music:search:albums:{hashlib.md5(query.encode()).hexdigest()}"
            cached = self._get_cached_music_data(cache_key)
            if cached:
                return cached
            
            results = self.db.query(Album).filter(
                or_(
                    Album.title.ilike(f"%{query}%"),
                    Album.artists.any(Artist.name.ilike(f"%{query}%"))
                )
            ).limit(limit).all()
            
            self._cache_music_data(cache_key, results, self.settings.music_cache_ttl)
            return results
        except Exception as e:
            logger.error(f"Error searching albums: {str(e)}")
            return []

    def search_playlists(self, query: str, limit: int) -> List[Playlist]:
        """Search playlists"""
        try:
            results = self.db.query(Playlist).filter(
                and_(
                    Playlist.is_public == True,
                    or_(
                        Playlist.name.ilike(f"%{query}%"),
                        Playlist.description.ilike(f"%{query}%")
                    )
                )
            ).limit(limit).all()
            return results
        except Exception as e:
            logger.error(f"Error searching playlists: {str(e)}")
            return []

    def advanced_search(self, query: str, search_type: str, filters: dict) -> dict:
        """Unified search with type filtering"""
        try:
            results = {}
            if search_type in ['all', 'track']:
                results['tracks'] = self.search_tracks(query, filters, 20)
            if search_type in ['all', 'artist']:
                results['artists'] = self.search_artists(query, 20)
            if search_type in ['all', 'album']:
                results['albums'] = self.search_albums(query, 20)
            if search_type in ['all', 'playlist']:
                results['playlists'] = self.search_playlists(query, 20)
            return results
        except Exception as e:
            logger.error(f"Error in advanced search: {str(e)}")
            return {}

    # Recommendation Methods

    def get_personalized_recommendations(self, user_id: int, limit: int) -> List[Track]:
        """Use play history and likes for recommendations"""
        try:
            cache_key = f"music:recommendations:{user_id}:personalized"
            cached = self._get_cached_music_data(cache_key)
            if cached:
                return cached
            
            # Get user's liked tracks and play history
            liked_track_ids = self.db.query(TrackLike.track_id).filter(TrackLike.user_id == user_id).all()
            liked_track_ids = [t[0] for t in liked_track_ids]
            
            played_track_ids = self.db.query(PlayHistory.track_id).filter(PlayHistory.user_id == user_id).all()
            played_track_ids = [t[0] for t in played_track_ids]
            
            # Get similar tracks based on artists/genres
            similar_tracks = []
            if liked_track_ids or played_track_ids:
                track_ids = list(set(liked_track_ids + played_track_ids))
                artists = self.db.query(TrackArtist.artist_id).filter(TrackArtist.track_id.in_(track_ids)).all()
                artist_ids = list(set([a[0] for a in artists]))
                
                similar_tracks = self.db.query(Track).filter(
                    Track.id.notin_(track_ids),
                    or_(
                        Track.artists.any(Artist.id.in_(artist_ids)),
                        Track.album.has(Album.genres.overlap(
                            self.db.query(Album.genres).filter(Album.tracks.any(Track.id.in_(track_ids))).first()[0]
                        ))
                    )
                ).limit(limit * 2).all()
            
            # Score and sort
            scored_tracks = []
            for track in similar_tracks:
                score = 0
                if track.artists.filter(Artist.id.in_(artist_ids)).count() > 0:
                    score += 1
                # Add more scoring logic here
                scored_tracks.append((track, score))
            
            scored_tracks.sort(key=lambda x: x[1], reverse=True)
            results = [t[0] for t in scored_tracks[:limit]]
            
            self._cache_music_data(cache_key, results, self.settings.music_cache_ttl)
            return results
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {str(e)}")
            return []

    def get_track_recommendations(self, track_id: int, limit: int) -> List[Track]:
        """Similar tracks based on audio features"""
        try:
            track = self.db.query(Track).filter(Track.id == track_id).first()
            if not track or not track.audio_features:
                return []
            
            features = track.audio_features
            # Simple similarity based on tempo, energy, danceability
            similar_tracks = self.db.query(Track).filter(
                Track.id != track_id,
                Track.audio_features.isnot(None)
            ).all()
            
            scored = []
            for t in similar_tracks:
                if t.audio_features:
                    score = (
                        abs(features.get('tempo', 0) - t.audio_features.get('tempo', 0)) +
                        abs(features.get('energy', 0) - t.audio_features.get('energy', 0)) +
                        abs(features.get('danceability', 0) - t.audio_features.get('danceability', 0))
                    )
                    scored.append((t, score))
            
            scored.sort(key=lambda x: x[1])
            return [t[0] for t in scored[:limit]]
        except Exception as e:
            logger.error(f"Error getting track recommendations: {str(e)}")
            return []

    def get_artist_recommendations(self, artist_id: int, limit: int) -> List[Artist]:
        """Similar artists"""
        try:
            artist = self.db.query(Artist).filter(Artist.id == artist_id).first()
            if not artist:
                return []
            
            # Simple genre-based similarity
            similar_artists = self.db.query(Artist).filter(
                Artist.id != artist_id,
                Artist.genres.overlap(artist.genres)
            ).limit(limit).all()
            
            return similar_artists
        except Exception as e:
            logger.error(f"Error getting artist recommendations: {str(e)}")
            return []

    def get_mood_based_recommendations(self, user_id: int, mood: str, limit: int) -> List[Track]:
        """Filter by mood/energy"""
        try:
            # Map mood to energy/danceability ranges
            mood_filters = {
                'energetic': {'energy_min': 0.7, 'danceability_min': 0.6},
                'calm': {'energy_max': 0.4, 'danceability_max': 0.5},
                'happy': {'valence_min': 0.6, 'energy_min': 0.5},
                'sad': {'valence_max': 0.4, 'energy_max': 0.5}
            }
            
            filters = mood_filters.get(mood, {})
            if not filters:
                return []
            
            q = self.db.query(Track).filter(Track.audio_features.isnot(None))
            
            if 'energy_min' in filters:
                q = q.filter(Track.audio_features['energy'].astext.cast(float) >= filters['energy_min'])
            if 'energy_max' in filters:
                q = q.filter(Track.audio_features['energy'].astext.cast(float) <= filters['energy_max'])
            if 'danceability_min' in filters:
                q = q.filter(Track.audio_features['danceability'].astext.cast(float) >= filters['danceability_min'])
            if 'danceability_max' in filters:
                q = q.filter(Track.audio_features['danceability'].astext.cast(float) <= filters['danceability_max'])
            if 'valence_min' in filters:
                q = q.filter(Track.audio_features['valence'].astext.cast(float) >= filters['valence_min'])
            if 'valence_max' in filters:
                q = q.filter(Track.audio_features['valence'].astext.cast(float) <= filters['valence_max'])
            
            return q.limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting mood-based recommendations: {str(e)}")
            return []

    def get_trending_tracks(self, genre: Optional[str], limit: int) -> List[Track]:
        """Trending based on play counts"""
        try:
            q = self.db.query(Track).join(PlayHistory)
            
            if genre:
                q = q.filter(Track.album.has(Album.genres.contains([genre])))
            
            # Count plays in last 7 days
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            trending = q.filter(PlayHistory.played_at >= seven_days_ago).group_by(Track.id).order_by(
                func.count(PlayHistory.id).desc()
            ).limit(limit).all()
            
            return trending
        except Exception as e:
            logger.error(f"Error getting trending tracks: {str(e)}")
            return []

    # Playlist Management Methods

    def create_playlist(self, user_id: int, name: str, description: str, is_public: bool, is_collaborative: bool) -> Playlist:
        """Create a new playlist"""
        try:
            playlist = Playlist(
                name=name,
                description=description,
                user_id=user_id,
                is_public=is_public,
                is_collaborative=is_collaborative
            )
            self.db.add(playlist)
            self.db.commit()
            self.db.refresh(playlist)
            return playlist
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating playlist: {str(e)}")
            raise

    def update_playlist(self, playlist_id: int, user_id: int, updates: dict) -> Playlist:
        """Update playlist metadata"""
        try:
            playlist = self.db.query(Playlist).filter(
                Playlist.id == playlist_id,
                Playlist.user_id == user_id
            ).first()
            if not playlist:
                raise ValueError("Playlist not found or not owned by user")
            
            for key, value in updates.items():
                if hasattr(playlist, key):
                    setattr(playlist, key, value)
            
            self.db.commit()
            self.db.refresh(playlist)
            
            # Invalidate cache
            self._invalidate_cache(f"playlist:{playlist_id}")
            
            return playlist
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating playlist: {str(e)}")
            raise

    def delete_playlist(self, playlist_id: int, user_id: int) -> bool:
        """Delete playlist"""
        try:
            playlist = self.db.query(Playlist).filter(
                Playlist.id == playlist_id,
                Playlist.user_id == user_id
            ).first()
            if not playlist:
                return False
            
            self.db.delete(playlist)
            self.db.commit()
            
            self._invalidate_cache(f"playlist:{playlist_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting playlist: {str(e)}")
            return False

    def add_tracks_to_playlist(self, playlist_id: int, track_ids: List[int], user_id: int, position: Optional[int]) -> bool:
        """Add tracks to playlist"""
        try:
            playlist = self.db.query(Playlist).filter(Playlist.id == playlist_id).first()
            if not playlist:
                return False
            
            # Check permissions
            if playlist.user_id != user_id and not playlist.is_collaborative:
                return False
            
            if position is None:
                # Add to end
                max_pos = self.db.query(func.max(PlaylistTrack.position)).filter(
                    PlaylistTrack.playlist_id == playlist_id
                ).scalar() or -1
                position = max_pos + 1
            
            for i, track_id in enumerate(track_ids):
                playlist_track = PlaylistTrack(
                    playlist_id=playlist_id,
                    track_id=track_id,
                    added_by_user_id=user_id,
                    position=position + i
                )
                self.db.add(playlist_track)
            
            self.db.commit()
            
            self._invalidate_cache(f"playlist:{playlist_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding tracks to playlist: {str(e)}")
            return False

    def remove_tracks_from_playlist(self, playlist_id: int, track_ids: List[int], user_id: int) -> bool:
        """Remove tracks from playlist"""
        try:
            playlist = self.db.query(Playlist).filter(Playlist.id == playlist_id).first()
            if not playlist:
                return False
            
            # Check permissions
            if playlist.user_id != user_id and not playlist.is_collaborative:
                return False
            
            self.db.query(PlaylistTrack).filter(
                PlaylistTrack.playlist_id == playlist_id,
                PlaylistTrack.track_id.in_(track_ids)
            ).delete()
            
            self.db.commit()
            
            self._invalidate_cache(f"playlist:{playlist_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing tracks from playlist: {str(e)}")
            return False

    def reorder_playlist_tracks(self, playlist_id: int, user_id: int, track_positions: List[dict]) -> bool:
        """Reorder playlist tracks"""
        try:
            playlist = self.db.query(Playlist).filter(Playlist.id == playlist_id).first()
            if not playlist:
                return False
            
            # Check permissions
            if playlist.user_id != user_id and not playlist.is_collaborative:
                return False
            
            for item in track_positions:
                self.db.query(PlaylistTrack).filter(
                    PlaylistTrack.playlist_id == playlist_id,
                    PlaylistTrack.track_id == item['track_id']
                ).update({'position': item['position']})
            
            self.db.commit()
            
            self._invalidate_cache(f"playlist:{playlist_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error reordering playlist tracks: {str(e)}")
            return False

    def add_collaborator(self, playlist_id: int, owner_id: int, collaborator_id: int, can_edit: bool) -> PlaylistCollaborator:
        """Add collaborator to playlist"""
        try:
            playlist = self.db.query(Playlist).filter(
                Playlist.id == playlist_id,
                Playlist.user_id == owner_id,
                Playlist.is_collaborative == True
            ).first()
            if not playlist:
                raise ValueError("Playlist not found or not collaborative")
            
            collaborator = PlaylistCollaborator(
                playlist_id=playlist_id,
                user_id=collaborator_id,
                can_edit=can_edit
            )
            self.db.add(collaborator)
            self.db.commit()
            self.db.refresh(collaborator)
            return collaborator
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding collaborator: {str(e)}")
            raise

    def remove_collaborator(self, playlist_id: int, owner_id: int, collaborator_id: int) -> bool:
        """Remove collaborator from playlist"""
        try:
            deleted = self.db.query(PlaylistCollaborator).filter(
                PlaylistCollaborator.playlist_id == playlist_id,
                PlaylistCollaborator.user_id == collaborator_id
            ).delete()
            self.db.commit()
            return deleted > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing collaborator: {str(e)}")
            return False

    def get_user_playlists(self, user_id: int, include_collaborative: bool) -> List[Playlist]:
        """Get user's playlists"""
        try:
            q = self.db.query(Playlist).filter(Playlist.user_id == user_id)
            
            if include_collaborative:
                collaborative_ids = self.db.query(PlaylistCollaborator.playlist_id).filter(
                    PlaylistCollaborator.user_id == user_id
                ).all()
                collaborative_ids = [p[0] for p in collaborative_ids]
                q = q.union(
                    self.db.query(Playlist).filter(Playlist.id.in_(collaborative_ids))
                )
            
            return q.all()
        except Exception as e:
            logger.error(f"Error getting user playlists: {str(e)}")
            return []

    # Library Management Methods

    def add_to_library(self, user_id: int, item_id: int, library_type: str) -> UserLibrary:
        """Add item to library"""
        try:
            library_item = UserLibrary(
                user_id=user_id,
                library_type=library_type,
                added_at=datetime.utcnow()
            )
            
            if library_type == 'track':
                library_item.track_id = item_id
            elif library_type == 'album':
                library_item.album_id = item_id
            elif library_type == 'playlist':
                library_item.playlist_id = item_id
            
            self.db.add(library_item)
            self.db.commit()
            self.db.refresh(library_item)
            return library_item
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding to library: {str(e)}")
            raise

    def remove_from_library(self, user_id: int, item_id: int, library_type: str) -> bool:
        """Remove item from library"""
        try:
            query = self.db.query(UserLibrary).filter(
                UserLibrary.user_id == user_id,
                UserLibrary.library_type == library_type
            )
            
            if library_type == 'track':
                query = query.filter(UserLibrary.track_id == item_id)
            elif library_type == 'album':
                query = query.filter(UserLibrary.album_id == item_id)
            elif library_type == 'playlist':
                query = query.filter(UserLibrary.playlist_id == item_id)
            
            deleted = query.delete()
            self.db.commit()
            return deleted > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing from library: {str(e)}")
            return False

    def get_user_library(self, user_id: int, library_type: str, limit: int, offset: int) -> List[Union[Track, Album, Playlist]]:
        """Get user's library items"""
        try:
            query = self.db.query(UserLibrary).filter(
                UserLibrary.user_id == user_id,
                UserLibrary.library_type == library_type
            ).order_by(UserLibrary.added_at.desc()).offset(offset).limit(limit)
            
            items = []
            for lib_item in query.all():
                if library_type == 'track' and lib_item.track:
                    items.append(lib_item.track)
                elif library_type == 'album' and lib_item.album:
                    items.append(lib_item.album)
                elif library_type == 'playlist' and lib_item.playlist:
                    items.append(lib_item.playlist)
            
            return items
        except Exception as e:
            logger.error(f"Error getting user library: {str(e)}")
            return []

    def is_in_library(self, user_id: int, item_id: int, library_type: str) -> bool:
        """Check if item is in library"""
        try:
            query = self.db.query(UserLibrary).filter(
                UserLibrary.user_id == user_id,
                UserLibrary.library_type == library_type
            )
            
            if library_type == 'track':
                query = query.filter(UserLibrary.track_id == item_id)
            elif library_type == 'album':
                query = query.filter(UserLibrary.album_id == item_id)
            elif library_type == 'playlist':
                query = query.filter(UserLibrary.playlist_id == item_id)
            
            return query.first() is not None
        except Exception as e:
            logger.error(f"Error checking library: {str(e)}")
            return False

    # Play History Methods

    def record_play(self, user_id: int, track_id: int, context_type: str, context_id: Optional[str], play_duration_ms: int, completed: bool) -> PlayHistory:
        """Record play event"""
        try:
            play_history = PlayHistory(
                user_id=user_id,
                track_id=track_id,
                played_at=datetime.utcnow(),
                play_duration_ms=play_duration_ms,
                completed=completed,
                context_type=context_type,
                context_id=context_id
            )
            self.db.add(play_history)
            self.db.commit()
            self.db.refresh(play_history)
            return play_history
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recording play: {str(e)}")
            raise

    def get_recently_played(self, user_id: int, limit: int) -> List[PlayHistory]:
        """Get recently played tracks"""
        try:
            return self.db.query(PlayHistory).filter(
                PlayHistory.user_id == user_id
            ).order_by(PlayHistory.played_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting recently played: {str(e)}")
            return []

    def get_play_stats(self, user_id: int, time_range: str) -> dict:
        """Get listening statistics"""
        try:
            # Define time range
            if time_range == 'short':
                days = 4
            elif time_range == 'medium':
                days = 6 * 7  # 6 weeks
            elif time_range == 'long':
                days = 12 * 7  # 12 weeks
            else:
                days = 4
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            plays = self.db.query(PlayHistory).filter(
                PlayHistory.user_id == user_id,
                PlayHistory.played_at >= start_date
            ).all()
            
            if not plays:
                return {}
            
            # Top tracks
            track_counts = {}
            for play in plays:
                track_counts[play.track_id] = track_counts.get(play.track_id, 0) + 1
            
            top_tracks = sorted(track_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_tracks = [(self.db.query(Track).filter(Track.id == tid).first(), count) for tid, count in top_tracks]
            
            # Top artists
            artist_counts = {}
            for play in plays:
                track = self.db.query(Track).filter(Track.id == play.track_id).first()
                if track and track.artists:
                    for artist in track.artists:
                        artist_counts[artist.id] = artist_counts.get(artist.id, 0) + 1
            
            top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_artists = [(self.db.query(Artist).filter(Artist.id == aid).first(), count) for aid, count in top_artists]
            
            # Top genres (simplified)
            genre_counts = {}
            for play in plays:
                track = self.db.query(Track).filter(Track.id == play.track_id).first()
                if track and track.album and track.album.genres:
                    for genre in track.album.genres:
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            total_plays = len(plays)
            total_duration = sum(p.play_duration_ms for p in plays)
            
            return {
                'time_range': time_range,
                'top_tracks': [{'track': t[0], 'play_count': t[1]} for t in top_tracks if t[0]],
                'top_artists': [{'artist': a[0], 'play_count': a[1]} for a in top_artists if a[0]],
                'top_genres': [{'genre': g[0], 'play_count': g[1]} for g in top_genres],
                'total_plays': total_plays,
                'total_duration_ms': total_duration
            }
        except Exception as e:
            logger.error(f"Error getting play stats: {str(e)}")
            return {}

    def get_listening_history(self, user_id: int, start_date: datetime, end_date: datetime) -> List[PlayHistory]:
        """Get listening history in date range"""
        try:
            return self.db.query(PlayHistory).filter(
                PlayHistory.user_id == user_id,
                PlayHistory.played_at >= start_date,
                PlayHistory.played_at <= end_date
            ).order_by(PlayHistory.played_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting listening history: {str(e)}")
            return []

    # Queue Management Methods

    def add_to_queue(self, user_id: int, track_id: int, position: Optional[int]) -> QueueItem:
        """Add track to queue"""
        try:
            if position is None:
                # Add to end
                max_pos = self.db.query(func.max(QueueItem.position)).filter(
                    QueueItem.user_id == user_id,
                    QueueItem.played == False
                ).scalar() or -1
                position = max_pos + 1
            
            queue_item = QueueItem(
                user_id=user_id,
                track_id=track_id,
                position=position,
                added_at=datetime.utcnow(),
                played=False
            )
            self.db.add(queue_item)
            self.db.commit()
            self.db.refresh(queue_item)
            return queue_item
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding to queue: {str(e)}")
            raise

    def remove_from_queue(self, user_id: int, queue_item_id: int) -> bool:
        """Remove from queue"""
        try:
            deleted = self.db.query(QueueItem).filter(
                QueueItem.id == queue_item_id,
                QueueItem.user_id == user_id
            ).delete()
            self.db.commit()
            return deleted > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing from queue: {str(e)}")
            return False

    def get_user_queue(self, user_id: int) -> List[QueueItem]:
        """Get user's queue"""
        try:
            return self.db.query(QueueItem).filter(
                QueueItem.user_id == user_id,
                QueueItem.played == False
            ).order_by(QueueItem.position).all()
        except Exception as e:
            logger.error(f"Error getting user queue: {str(e)}")
            return []

    def clear_queue(self, user_id: int) -> bool:
        """Clear user's queue"""
        try:
            deleted = self.db.query(QueueItem).filter(
                QueueItem.user_id == user_id,
                QueueItem.played == False
            ).delete()
            self.db.commit()
            return deleted > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error clearing queue: {str(e)}")
            return False

    def reorder_queue(self, user_id: int, item_positions: List[dict]) -> bool:
        """Reorder queue"""
        try:
            for item in item_positions:
                self.db.query(QueueItem).filter(
                    QueueItem.id == item['queue_item_id'],
                    QueueItem.user_id == user_id
                ).update({'position': item['position']})
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error reordering queue: {str(e)}")
            return False

    # Lyrics Methods

    def get_track_lyrics(self, track_id: int, language: str) -> Optional[Lyrics]:
        """Get track lyrics"""
        try:
            return self.db.query(Lyrics).filter(
                Lyrics.track_id == track_id,
                Lyrics.language == language
            ).first()
        except Exception as e:
            logger.error(f"Error getting track lyrics: {str(e)}")
            return None

    def sync_lyrics_from_api(self, track_id: int, language: str) -> Optional[Lyrics]:
        """Fetch lyrics from external API"""
        try:
            track = self.db.query(Track).filter(Track.id == track_id).first()
            if not track:
                return None
            
            # Placeholder for lyrics API integration
            # In real implementation, call Musixmatch or Genius API
            lyrics_text = "Lyrics not available"  # Placeholder
            
            lyrics = Lyrics(
                track_id=track_id,
                language=language,
                lyrics_text=lyrics_text,
                source="api",
                verified=False
            )
            self.db.add(lyrics)
            self.db.commit()
            self.db.refresh(lyrics)
            return lyrics
        except Exception as e:
            logger.error(f"Error syncing lyrics: {str(e)}")
            return None

    def add_lyrics(self, track_id: int, lyrics_text: str, language: str, synced_lyrics: Optional[dict]) -> Lyrics:
        """Add lyrics manually"""
        try:
            lyrics = Lyrics(
                track_id=track_id,
                language=language,
                lyrics_text=lyrics_text,
                synced_lyrics=synced_lyrics,
                source="manual",
                verified=False
            )
            self.db.add(lyrics)
            self.db.commit()
            self.db.refresh(lyrics)
            return lyrics
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding lyrics: {str(e)}")
            raise

    # Social Features Methods

    def follow_artist(self, user_id: int, artist_id: int) -> ArtistFollower:
        """Follow artist"""
        try:
            follower = ArtistFollower(
                user_id=user_id,
                artist_id=artist_id,
                followed_at=datetime.utcnow()
            )
            self.db.add(follower)
            self.db.commit()
            self.db.refresh(follower)
            return follower
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error following artist: {str(e)}")
            raise

    def unfollow_artist(self, user_id: int, artist_id: int) -> bool:
        """Unfollow artist"""
        try:
            deleted = self.db.query(ArtistFollower).filter(
                ArtistFollower.user_id == user_id,
                ArtistFollower.artist_id == artist_id
            ).delete()
            self.db.commit()
            return deleted > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error unfollowing artist: {str(e)}")
            return False

    def get_followed_artists(self, user_id: int, limit: int) -> List[Artist]:
        """Get followed artists"""
        try:
            followed = self.db.query(ArtistFollower).filter(
                ArtistFollower.user_id == user_id
            ).order_by(ArtistFollower.followed_at.desc()).limit(limit).all()
            
            artist_ids = [f.artist_id for f in followed]
            return self.db.query(Artist).filter(Artist.id.in_(artist_ids)).all()
        except Exception as e:
            logger.error(f"Error getting followed artists: {str(e)}")
            return []

    def is_following_artist(self, user_id: int, artist_id: int) -> bool:
        """Check if following artist"""
        try:
            return self.db.query(ArtistFollower).filter(
                ArtistFollower.user_id == user_id,
                ArtistFollower.artist_id == artist_id
            ).first() is not None
        except Exception as e:
            logger.error(f"Error checking follow status: {str(e)}")
            return False

    def like_track(self, user_id: int, track_id: int) -> TrackLike:
        """Like track"""
        try:
            like = TrackLike(
                user_id=user_id,
                track_id=track_id,
                liked_at=datetime.utcnow()
            )
            self.db.add(like)
            self.db.commit()
            self.db.refresh(like)
            return like
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error liking track: {str(e)}")
            raise

    def unlike_track(self, user_id: int, track_id: int) -> bool:
        """Unlike track"""
        try:
            deleted = self.db.query(TrackLike).filter(
                TrackLike.user_id == user_id,
                TrackLike.track_id == track_id
            ).delete()
            self.db.commit()
            return deleted > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error unliking track: {str(e)}")
            return False

    def get_liked_tracks(self, user_id: int, limit: int, offset: int) -> List[Track]:
        """Get liked tracks"""
        try:
            liked = self.db.query(TrackLike).filter(
                TrackLike.user_id == user_id
            ).order_by(TrackLike.liked_at.desc()).offset(offset).limit(limit).all()
            
            track_ids = [l.track_id for l in liked]
            return self.db.query(Track).filter(Track.id.in_(track_ids)).all()
        except Exception as e:
            logger.error(f"Error getting liked tracks: {str(e)}")
            return []

    def share_track(self, user_id: int, track_id: int, share_type: str, recipient_ids: List[int]) -> dict:
        """Share track"""
        try:
            # Placeholder implementation
            share_url = f"https://trendy.app/track/{track_id}"
            return {
                'share_url': share_url,
                'share_type': share_type,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(days=7)
            }
        except Exception as e:
            logger.error(f"Error sharing track: {str(e)}")
            raise

    def share_playlist(self, user_id: int, playlist_id: int, share_type: str, recipient_ids: List[int]) -> dict:
        """Share playlist"""
        try:
            # Placeholder implementation
            share_url = f"https://trendy.app/playlist/{playlist_id}"
            return {
                'share_url': share_url,
                'share_type': share_type,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(days=7)
            }
        except Exception as e:
            logger.error(f"Error sharing playlist: {str(e)}")
            raise

    # Artist/Album Detail Methods

    def get_artist_details(self, artist_id: int, include_tracks: bool, include_albums: bool) -> dict:
        """Get artist details"""
        try:
            artist = self.db.query(Artist).filter(Artist.id == artist_id).first()
            if not artist:
                return {}
            
            details = {
                'artist': artist,
                'follower_count': self.db.query(func.count(ArtistFollower.id)).filter(ArtistFollower.artist_id == artist_id).scalar(),
                'tracks': [],
                'albums': []
            }
            
            if include_tracks:
                details['tracks'] = self.get_artist_top_tracks(artist_id, 10)
            
            if include_albums:
                details['albums'] = self.get_artist_albums(artist_id, None, 10)
            
            return details
        except Exception as e:
            logger.error(f"Error getting artist details: {str(e)}")
            return {}

    def get_artist_top_tracks(self, artist_id: int, limit: int) -> List[Track]:
        """Get artist's top tracks"""
        try:
            return self.db.query(Track).join(TrackArtist).filter(
                TrackArtist.artist_id == artist_id
            ).order_by(Track.popularity_score.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting artist top tracks: {str(e)}")
            return []

    def get_artist_albums(self, artist_id: int, album_type: Optional[str], limit: int) -> List[Album]:
        """Get artist's albums"""
        try:
            q = self.db.query(Album).join(AlbumArtist).filter(
                AlbumArtist.artist_id == artist_id
            )
            
            if album_type:
                q = q.filter(Album.album_type == album_type)
            
            return q.order_by(Album.release_date.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting artist albums: {str(e)}")
            return []

    def get_album_details(self, album_id: int, include_tracks: bool) -> dict:
        """Get album details"""
        try:
            album = self.db.query(Album).filter(Album.id == album_id).first()
            if not album:
                return {}
            
            details = {'album': album, 'tracks': []}
            
            if include_tracks:
                details['tracks'] = self.get_album_tracks(album_id)
            
            return details
        except Exception as e:
            logger.error(f"Error getting album details: {str(e)}")
            return {}

    def get_album_tracks(self, album_id: int) -> List[Track]:
        """Get album tracks"""
        try:
            return self.db.query(Track).filter(Track.album_id == album_id).order_by(Track.track_number).all()
        except Exception as e:
            logger.error(f"Error getting album tracks: {str(e)}")
            return []

    # Audio Features Methods

    def get_track_audio_features(self, track_id: int) -> dict:
        """Get audio features for track"""
        try:
            track = self.db.query(Track).filter(Track.id == track_id).first()
            if track and track.audio_features:
                return track.audio_features
            return {}
        except Exception as e:
            logger.error(f"Error getting audio features: {str(e)}")
            return {}

    def analyze_audio_features(self, track_ids: List[int]) -> dict:
        """Batch analyze audio features"""
        try:
            tracks = self.db.query(Track).filter(Track.id.in_(track_ids)).all()
            features = {}
            for track in tracks:
                features[track.id] = track.audio_features or {}
            return features
        except Exception as e:
            logger.error(f"Error analyzing audio features: {str(e)}")
            return {}

    # Helper Methods

    def _get_audio_features(self, sp: spotipy.Spotify, spotify_id: str) -> dict:
        """Get audio features from Spotify"""
        try:
            features = sp.audio_features([spotify_id])[0]
            return features if features else {}
        except Exception:
            return {}

    def _cache_music_data(self, key: str, data: Any, ttl: int):
        """Cache music data"""
        try:
            import redis
            r = redis.Redis.from_url(self.settings.redis_url)
            r.setex(f"music:{key}", ttl, json.dumps(data, default=str))
        except Exception:
            pass  # Ignore cache errors

    def _get_cached_music_data(self, key: str) -> Optional[Any]:
        """Get cached music data"""
        try:
            import redis
            r = redis.Redis.from_url(self.settings.redis_url)
            data = r.get(f"music:{key}")
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None

    def _invalidate_cache(self, key: str):
        """Invalidate cache"""
        try:
            import redis
            r = redis.Redis.from_url(self.settings.redis_url)
            r.delete(f"music:{key}")
        except Exception:
            pass