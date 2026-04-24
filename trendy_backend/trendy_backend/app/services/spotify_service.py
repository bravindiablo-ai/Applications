"""
Spotify Service for TRENDY App
Handles Spotify API integration for music search and recommendations
"""

import logging
from typing import List, Dict, Any, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class SpotifyService:
    def __init__(self):
        self.settings = get_settings()
        self.client_id = self.settings.spotify_client_id
        self.client_secret = self.settings.spotify_client_secret
        self.spotify = None

        if self.client_id and self.client_secret and self.client_id != "your_spotify_client_id_here":
            try:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                logger.info("Spotify service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Spotify service: {str(e)}")
                self.spotify = None
        else:
            logger.warning("Spotify credentials not configured")

    def is_configured(self) -> bool:
        """Check if Spotify service is properly configured"""
        return self.spotify is not None

    def search(self, query: str, search_type: str = "track", limit: int = 20) -> Dict[str, Any]:
        """
        Search Spotify for tracks, artists, albums, or playlists

        Args:
            query: Search query
            search_type: Type of search (track, artist, album, playlist)
            limit: Maximum number of results

        Returns:
            Dict containing search results
        """
        if not self.is_configured():
            raise Exception("Spotify service not configured")

        try:
            results = self.spotify.search(q=query, type=search_type, limit=limit)

            # Format results based on search type
            if search_type == "track":
                tracks = []
                for item in results['tracks']['items']:
                    track = {
                        'id': item['id'],
                        'name': item['name'],
                        'artists': [{'name': artist['name'], 'id': artist['id']} for artist in item['artists']],
                        'album': {
                            'name': item['album']['name'],
                            'id': item['album']['id'],
                            'images': item['album']['images']
                        },
                        'duration_ms': item['duration_ms'],
                        'preview_url': item['preview_url'],
                        'external_urls': item['external_urls'],
                        'popularity': item['popularity']
                    }
                    tracks.append(track)
                return {'tracks': tracks}

            elif search_type == "artist":
                artists = []
                for item in results['artists']['items']:
                    artist = {
                        'id': item['id'],
                        'name': item['name'],
                        'genres': item['genres'],
                        'followers': item['followers']['total'] if item['followers'] else 0,
                        'images': item['images'],
                        'external_urls': item['external_urls'],
                        'popularity': item['popularity']
                    }
                    artists.append(artist)
                return {'artists': artists}

            elif search_type == "album":
                albums = []
                for item in results['albums']['items']:
                    album = {
                        'id': item['id'],
                        'name': item['name'],
                        'artists': [{'name': artist['name'], 'id': artist['id']} for artist in item['artists']],
                        'release_date': item['release_date'],
                        'total_tracks': item['total_tracks'],
                        'images': item['images'],
                        'external_urls': item['external_urls']
                    }
                    albums.append(album)
                return {'albums': albums}

            elif search_type == "playlist":
                playlists = []
                for item in results['playlists']['items']:
                    if item:  # Some results might be None
                        playlist = {
                            'id': item['id'],
                            'name': item['name'],
                            'description': item['description'],
                            'owner': {
                                'id': item['owner']['id'],
                                'display_name': item['owner']['display_name']
                            },
                            'tracks': item['tracks']['total'],
                            'images': item['images'],
                            'external_urls': item['external_urls']
                        }
                        playlists.append(playlist)
                return {'playlists': playlists}

            return results

        except Exception as e:
            logger.error(f"Spotify search error: {str(e)}")
            raise Exception(f"Failed to search Spotify: {str(e)}")

    def get_recommendations(
        self,
        seed_tracks: Optional[str] = None,
        seed_artists: Optional[str] = None,
        seed_genres: Optional[str] = None,
        limit: int = 20,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get music recommendations from Spotify

        Args:
            seed_tracks: Comma-separated track IDs
            seed_artists: Comma-separated artist IDs
            seed_genres: Comma-separated genres
            limit: Number of recommendations
            **kwargs: Additional parameters (target_danceability, target_energy, etc.)

        Returns:
            Dict containing recommended tracks
        """
        if not self.is_configured():
            raise Exception("Spotify service not configured")

        try:
            # Build seed parameters
            seed_params = {}
            if seed_tracks:
                seed_params['seed_tracks'] = seed_tracks.split(',')[:5]  # Max 5 seeds
            if seed_artists:
                seed_params['seed_artists'] = seed_artists.split(',')[:5]
            if seed_genres:
                seed_params['seed_genres'] = seed_genres.split(',')[:5]

            if not seed_params:
                # If no seeds provided, use some popular genres as default
                seed_params['seed_genres'] = ['pop', 'hip-hop', 'rock']

            # Get recommendations
            results = self.spotify.recommendations(limit=limit, **seed_params, **kwargs)

            tracks = []
            for item in results['tracks']:
                track = {
                    'id': item['id'],
                    'name': item['name'],
                    'artists': [{'name': artist['name'], 'id': artist['id']} for artist in item['artists']],
                    'album': {
                        'name': item['album']['name'],
                        'id': item['album']['id'],
                        'images': item['album']['images']
                    },
                    'duration_ms': item['duration_ms'],
                    'preview_url': item['preview_url'],
                    'external_urls': item['external_urls'],
                    'popularity': item['popularity']
                }
                tracks.append(track)

            return {'tracks': tracks}

        except Exception as e:
            logger.error(f"Spotify recommendations error: {str(e)}")
            raise Exception(f"Failed to get Spotify recommendations: {str(e)}")

    def get_track_details(self, track_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific track"""
        if not self.is_configured():
            raise Exception("Spotify service not configured")

        try:
            track = self.spotify.track(track_id)
            return {
                'id': track['id'],
                'name': track['name'],
                'artists': [{'name': artist['name'], 'id': artist['id']} for artist in track['artists']],
                'album': {
                    'name': track['album']['name'],
                    'id': track['album']['id'],
                    'images': track['album']['images'],
                    'release_date': track['album']['release_date']
                },
                'duration_ms': track['duration_ms'],
                'preview_url': track['preview_url'],
                'external_urls': track['external_urls'],
                'popularity': track['popularity'],
                'explicit': track['explicit']
            }
        except Exception as e:
            logger.error(f"Spotify track details error: {str(e)}")
            raise Exception(f"Failed to get track details: {str(e)}")

    def get_artist_details(self, artist_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific artist"""
        if not self.is_configured():
            raise Exception("Spotify service not configured")

        try:
            artist = self.spotify.artist(artist_id)
            top_tracks = self.spotify.artist_top_tracks(artist_id)

            return {
                'id': artist['id'],
                'name': artist['name'],
                'genres': artist['genres'],
                'followers': artist['followers']['total'] if artist['followers'] else 0,
                'images': artist['images'],
                'external_urls': artist['external_urls'],
                'popularity': artist['popularity'],
                'top_tracks': [
                    {
                        'id': track['id'],
                        'name': track['name'],
                        'preview_url': track['preview_url'],
                        'external_urls': track['external_urls']
                    } for track in top_tracks['tracks'][:5]  # Top 5 tracks
                ]
            }
        except Exception as e:
            logger.error(f"Spotify artist details error: {str(e)}")
            raise Exception(f"Failed to get artist details: {str(e)}")
