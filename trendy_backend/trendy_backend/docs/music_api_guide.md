# Spotify Music Integration
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/music/callback
SPOTIFY_SCOPES=user-library-read,user-library-modify,playlist-read-private,playlist-modify-public,playlist-modify-private,user-read-recently-played,user-top-read,user-follow-read,user-follow-modify

# Apple Music Integration (Optional)
APPLE_MUSIC_TEAM_ID=your_team_id
APPLE_MUSIC_KEY_ID=your_key_id
APPLE_MUSIC_PRIVATE_KEY_PATH=/path/to/private-key.p8

# Lyrics Service (Optional)
LYRICS_API_KEY=your_musixmatch_or_genius_api_key

# Music Service Configuration
MUSIC_CACHE_TTL=3600
```

### OAuth Flow Explanation

The Spotify integration uses Authorization Code Flow with PKCE:

1. User initiates OAuth via `GET /api/music/spotify/authorize`
2. Backend redirects to Spotify with client ID, scopes, and code challenge
3. User authorizes the app on Spotify
4. Spotify redirects back with authorization code
5. Backend exchanges code for access/refresh tokens
6. Tokens are cached in Redis for future API calls

## API Endpoints Reference

### Search & Discovery

#### Advanced Search
- **Method**: GET
- **Path**: `/api/music/search`
- **Parameters**: 
  - `query` (string, required): Search term
  - `search_type` (string, optional): track/artist/album/playlist (default: all)
  - `genre` (string, optional): Filter by genre
  - `year_min` (int, optional): Minimum release year
  - `year_max` (int, optional): Maximum release year
  - `tempo_min` (float, optional): Minimum tempo (BPM)
  - `tempo_max` (float, optional): Maximum tempo (BPM)
  - `mood` (string, optional): energetic/calm/happy/sad
  - `explicit` (bool, optional): Include explicit content
  - `limit` (int, optional): Results per page (default: 20)
  - `offset` (int, optional): Pagination offset (default: 0)
- **Response**: `SearchResponse` with results array and total count
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/music/search?query=rock&genre=pop&limit=10" \
    -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
  ```

#### Personalized Recommendations
- **Method**: GET
- **Path**: `/api/music/recommendations`
- **Parameters**: `limit` (int, optional, default: 20)
- **Response**: `RecommendationsResponse` with track list
- **Auth Required**: Yes
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/music/recommendations?limit=10" \
    -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
  ```

#### Similar Tracks
- **Method**: GET
- **Path**: `/api/music/recommendations/track/{track_id}`
- **Parameters**: `limit` (int, optional, default: 20)
- **Response**: `RecommendationsResponse`

#### Mood-Based Discovery
- **Method**: GET
- **Path**: `/api/music/recommendations/mood/{mood}`
- **Parameters**: `limit` (int, optional, default: 20)
- **Response**: `RecommendationsResponse`

#### Trending Tracks
- **Method**: GET
- **Path**: `/api/music/trending`
- **Parameters**: `genre` (string, optional), `limit` (int, optional, default: 20)
- **Response**: List of `TrackResponse`

### Tracks

#### Track Details
- **Method**: GET
- **Path**: `/api/music/tracks/{track_id}`
- **Response**: `TrackDetail` with audio features

#### Track Lyrics
- **Method**: GET
- **Path**: `/api/music/tracks/{track_id}/lyrics`
- **Parameters**: `language` (string, optional, default: 'en')
- **Response**: `LyricsResponse`

#### Like/Unlike Track
- **Method**: POST
- **Path**: `/api/music/tracks/{track_id}/like`
- **Response**: Success message

#### Liked Tracks
- **Method**: GET
- **Path**: `/api/music/tracks/liked`
- **Parameters**: `limit`, `offset`
- **Response**: Paginated `TrackResponse` list

#### Record Play
- **Method**: POST
- **Path**: `/api/music/tracks/{track_id}/play`
- **Body**: `PlayHistoryCreate`
- **Response**: `PlayHistoryResponse`

### Artists

#### Artist Details
- **Method**: GET
- **Path**: `/api/music/artists/{artist_id}`
- **Response**: `ArtistDetail`

#### Artist Top Tracks
- **Method**: GET
- **Path**: `/api/music/artists/{artist_id}/tracks`
- **Parameters**: `limit`
- **Response**: List of `TrackResponse`

#### Follow/Unfollow Artist
- **Method**: POST
- **Path**: `/api/music/artists/{artist_id}/follow`
- **Response**: Success message

### Albums

#### Album Details
- **Method**: GET
- **Path**: `/api/music/albums/{album_id}`
- **Response**: `AlbumDetail`

#### Save/Unsave Album
- **Method**: POST
- **Path**: `/api/music/albums/{album_id}/save`
- **Response**: Success message

### Playlists

#### User Playlists
- **Method**: GET
- **Path**: `/api/music/playlists`
- **Parameters**: `include_collaborative` (bool)
- **Response**: List of `PlaylistResponse`

#### Create Playlist
- **Method**: POST
- **Path**: `/api/music/playlists`
- **Body**: `PlaylistCreate`
- **Response**: `PlaylistResponse`

#### Playlist Details
- **Method**: GET
- **Path**: `/api/music/playlists/{playlist_id}`
- **Response**: `PlaylistDetail`

#### Update Playlist
- **Method**: PUT
- **Path**: `/api/music/playlists/{playlist_id}`
- **Body**: `PlaylistUpdate`
- **Response**: `PlaylistResponse`

#### Add Tracks to Playlist
- **Method**: POST
- **Path**: `/api/music/playlists/{playlist_id}/tracks`
- **Body**: `PlaylistTrackAdd`
- **Response**: Success message

### Library

#### Saved Tracks
- **Method**: GET
- **Path**: `/api/music/library/tracks`
- **Parameters**: `limit`, `offset`
- **Response**: `LibraryResponse`

#### Add to Library
- **Method**: POST
- **Path**: `/api/music/library/add`
- **Body**: `{"item_id": int, "library_type": "track/album/playlist"}`
- **Response**: Success message

### Play History

#### Recently Played
- **Method**: GET
- **Path**: `/api/music/history/recent`
- **Parameters**: `limit`
- **Response**: List of `PlayHistoryResponse`

#### Listening Stats
- **Method**: GET
- **Path**: `/api/music/history/stats`
- **Parameters**: `time_range` (short/medium/long)
- **Response**: `PlayStatsResponse`

### Queue

#### Get Queue
- **Method**: GET
- **Path**: `/api/music/queue`
- **Response**: `QueueResponse`

#### Add to Queue
- **Method**: POST
- **Path**: `/api/music/queue`
- **Body**: `QueueAdd`
- **Response**: Success message

### Social/Sharing

#### Share Track
- **Method**: POST
- **Path**: `/api/music/share/track`
- **Body**: `ShareRequest`
- **Response**: `ShareResponse`

### Spotify Integration

#### Initiate OAuth
- **Method**: GET
- **Path**: `/api/music/spotify/authorize`
- **Response**: Redirect to Spotify

#### OAuth Callback
- **Method**: GET
- **Path**: `/api/music/callback`
- **Parameters**: `code`, `state`
- **Response**: Redirect to frontend with tokens

## Data Models

### Entity Relationship Diagram (Text-based)

```
User --1:N--> Playlist (owner)
User --1:N--> UserLibrary
User --1:N--> PlayHistory
User --1:N--> ArtistFollower
User --1:N--> TrackLike
User --1:N--> QueueItem

Artist --1:N--> Album (via AlbumArtist)
Artist --1:N--> Track (via TrackArtist)
Artist --1:N--> ArtistFollower

Album --1:N--> Track
Album --N:M--> Artist (AlbumArtist)

Track --N:M--> Artist (TrackArtist)
Track --N:M--> Playlist (PlaylistTrack)

Playlist --1:N--> PlaylistTrack
Playlist --1:N--> PlaylistCollaborator

PlaylistTrack --N:1--> Track
PlaylistTrack --N:1--> User (added_by)

PlaylistCollaborator --N:1--> User
```

### Model Descriptions

- **Artist**: Represents music artists with bio, image, genres, and follower counts
- **Album**: Music albums with release info, cover art, and track listings
- **Track**: Individual songs with metadata, audio features, and relationships
- **Playlist**: User-created collections of tracks with collaboration features
- **UserLibrary**: User's saved music items (tracks, albums, playlists)
- **PlayHistory**: Records of track plays with context and duration
- **Lyrics**: Text and synchronized lyrics for tracks
- **ArtistFollower**: User-artist follow relationships
- **TrackLike**: User-track like relationships
- **QueueItem**: Tracks in user's playback queue

## Features Guide

### Implementing Personalized Recommendations

Use the `/api/music/recommendations` endpoint to get tracks tailored to user preferences. The system analyzes play history, liked tracks, and followed artists using collaborative filtering.

### Creating and Managing Playlists

1. Create via `POST /api/music/playlists`
2. Add tracks with `POST /api/music/playlists/{id}/tracks`
3. Reorder using `PUT /api/music/playlists/{id}/tracks/reorder`

### Collaborative Playlists

Enable collaboration by setting `is_collaborative: true` when creating. Add collaborators via `POST /api/music/playlists/{id}/collaborators`.

### Tracking Play History

Record plays with `POST /api/music/tracks/{id}/play`, including context (playlist/album) and completion status.

### Queue Management

Add tracks to queue with position control, reorder items, and clear the entire queue.

### Adding Lyrics Support

Fetch lyrics via `GET /api/music/tracks/{id}/lyrics`. Supports multiple languages and synchronized lyrics.

### Social Features

Follow artists, like tracks, and share music with other users in the platform.

## Integration Examples

### Python Client

```python
import requests

class MusicAPIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def search_tracks(self, query, limit=20):
        response = requests.get(
            f'{self.base_url}/api/music/search',
            params={'query': query, 'search_type': 'track', 'limit': limit},
            headers=self.headers
        )
        return response.json()
    
    def create_playlist(self, name, description, is_public=False):
        data = {
            'name': name,
            'description': description,
            'is_public': is_public,
            'is_collaborative': False
        }
        response = requests.post(
            f'{self.base_url}/api/music/playlists',
            json=data,
            headers=self.headers
        )
        return response.json()
```

### JavaScript/TypeScript Client

```typescript
class MusicAPI {
    constructor(private baseURL: string, private token: string) {}
    
    async searchTracks(query: string, limit = 20) {
        const response = await fetch(
            `${this.baseURL}/api/music/search?query=${query}&search_type=track&limit=${limit}`,
            {
                headers: { 'Authorization': `Bearer ${this.token}` }
            }
        );
        return response.json();
    }
    
    async likeTrack(trackId: number) {
        const response = await fetch(
            `${this.baseURL}/api/music/tracks/${trackId}/like`,
            {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.token}` }
            }
        );
        return response.json();
    }
}
```

### Flutter/Dart Client

```dart
class MusicService {
    final String baseUrl;
    final String token;
    
    Future<List<dynamic>> getRecommendations({int limit = 20}) async {
        final response = await http.get(
            Uri.parse('$baseUrl/api/music/recommendations?limit=$limit'),
            headers: {'Authorization': 'Bearer $token'}
        );
        return json.decode(response.body)['tracks'];
    }
    
    Future<void> addToQueue(int trackId, {int? position}) async {
        await http.post(
            Uri.parse('$baseUrl/api/music/queue'),
            headers: {'Authorization': 'Bearer $token', 'Content-Type': 'application/json'},
            body: json.encode({'track_id': trackId, 'position': position})
        );
    }
}