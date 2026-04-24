# Movie API Guide

## Overview

### Introduction to Netflix-Level Movie Features

The Movie API provides comprehensive Netflix-style functionality for movies and TV shows, including TMDB integration, personalized recommendations, multi-profile support, watch parties, and advanced viewing tracking. Built on FastAPI with PostgreSQL and Redis caching, it offers a complete entertainment platform backend.

Key features include:
- **TMDB Integration**: Real-time movie/TV data from The Movie Database API
- **Multi-Profile Support**: User profiles with separate watchlists and viewing history
- **Watch Parties**: Real-time synchronized viewing with WebSocket support
- **Continue Watching**: Resume playback from last position
- **Personalized Recommendations**: Collaborative filtering and content-based suggestions
- **Video Streaming**: Quality management and CDN integration
- **Reviews & Ratings**: User-generated content with spoiler warnings
- **Advanced Search**: Filter by genre, year, rating, and more

### Architecture Overview

The movie system follows a layered architecture:

```
┌─────────────────┐
│   API Layer     │  FastAPI routers (movies_updated.py)
│   (Endpoints)   │
├─────────────────┤
│ Service Layer   │  MovieService (business logic, TMDB integration)
├─────────────────┤
│   Data Layer    │  SQLAlchemy models (movie.py)
├─────────────────┤
│   Cache Layer   │  Redis (CacheService)
├─────────────────┤
│   External APIs │  TMDB API (tmdbsimple)
└─────────────────┘
```

- **Models**: 12+ interconnected models for movies/TV ecosystem
- **Service Layer**: MovieService handles TMDB sync, recommendations, and business logic
- **API Endpoints**: 30+ REST endpoints plus WebSocket for watch parties
- **WebSocket**: Real-time watch party synchronization

### Authentication Requirements

Most endpoints require Firebase authentication. Use the `Authorization: Bearer <firebase_token>` header. Some endpoints support optional auth for enhanced features.

Multi-profile support uses the `X-Profile-Id` header to specify the active profile.

### Multi-Profile Support Explanation

Users can create multiple profiles (like Netflix), each with separate:
- Watchlist
- Viewing history
- Preferences (maturity rating, autoplay settings)

Profiles support kids mode with content filtering based on maturity ratings (G/PG/PG13/R/NC17).

## Setup & Configuration

### How to Obtain TMDB API Key

1. Visit [TMDB Website](https://www.themoviedb.org/)
2. Create a free account
3. Go to Settings > API
4. Request an API Key (v3 auth)
5. Copy the API Key (v3 auth) - this is your `TMDB_API_KEY`

### Environment Variable Setup

Add to your `.env` file:

```bash
# TMDB Movie Integration
TMDB_API_KEY=your_tmdb_api_key_here
TMDB_CACHE_TTL=3600
MOVIE_CACHE_TTL=7200

# Video Streaming Configuration
STREAMING_CDN_URL=https://cdn.yourdomain.com
STREAMING_QUALITIES=360p,480p,720p,1080p,4K

# Watch Party Configuration
MAX_WATCH_PARTY_PARTICIPANTS=10
WATCH_PARTY_TIMEOUT_MINUTES=120

# Viewing Progress Configuration
CONTINUE_WATCHING_THRESHOLD_PERCENT=5
COMPLETED_THRESHOLD_PERCENT=90
```

### Streaming CDN Configuration

Configure your CDN base URL for video streaming. The system supports multiple quality levels (360p to 4K). Video URLs follow the pattern: `{STREAMING_CDN_URL}/movies/{movie_id}/{quality}.mp4`

### Watch Party Settings

- `MAX_WATCH_PARTY_PARTICIPANTS`: Maximum users per party (default: 10)
- `WATCH_PARTY_TIMEOUT_MINUTES`: Inactivity timeout before ending party (default: 120)

## API Endpoints Reference

### Search & Discovery

#### Advanced Search
- **Method**: GET
- **Path**: `/api/movies/search`
- **Parameters**: 
  - `query` (string, required): Search term
  - `content_type` (string, optional): movie/tv/person (default: all)
  - `genre_ids` (string, optional): Comma-separated genre IDs
  - `year` (int, optional): Release year
  - `min_rating` (float, optional): Minimum rating (0-10)
  - `max_rating` (float, optional): Maximum rating (0-10)
  - `language` (string, optional): Language code (en, es, etc.)
  - `page` (int, optional): Page number (default: 1)
  - `limit` (int, optional): Results per page (default: 20)
- **Response**: `SearchResponse` with results array and pagination
- **Auth Required**: No (optional for personalized results)
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/movies/search?query=action&content_type=movie&genre_ids=28&limit=10"
  ```

#### Personalized Recommendations
- **Method**: GET
- **Path**: `/api/movies/recommendations`
- **Parameters**: `limit` (int, optional, default: 20), `profile_id` (int, required in header)
- **Response**: `RecommendationsResponse`
- **Auth Required**: Yes
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/movies/recommendations?limit=10" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -H "X-Profile-Id: 1"
  ```

#### Similar Movies
- **Method**: GET
- **Path**: `/api/movies/recommendations/movie/{movie_id}`
- **Parameters**: `limit` (int, optional, default: 20)
- **Response**: `RecommendationsResponse`

#### Trending Movies
- **Method**: GET
- **Path**: `/api/movies/trending/movies`
- **Parameters**: `time_window` (string, optional): day/week (default: week), `limit` (int, optional, default: 20)
- **Response**: List of `MovieResponse`

#### Popular Movies
- **Method**: GET
- **Path**: `/api/movies/popular/movies`
- **Parameters**: `limit` (int, optional, default: 20)
- **Response**: List of `MovieResponse`

#### Top Rated Movies
- **Method**: GET
- **Path**: `/api/movies/top-rated/movies`
- **Parameters**: `limit` (int, optional, default: 20)
- **Response**: List of `MovieResponse`

#### Upcoming Movies
- **Method**: GET
- **Path**: `/api/movies/upcoming`
- **Parameters**: `limit` (int, optional, default: 20)
- **Response**: List of `MovieResponse`

#### Now Playing Movies
- **Method**: GET
- **Path**: `/api/movies/now-playing`
- **Parameters**: `limit` (int, optional, default: 20)
- **Response**: List of `MovieResponse`

#### Movies by Genre
- **Method**: GET
- **Path**: `/api/movies/genres/{genre_id}/movies`
- **Parameters**: `limit` (int, optional, default: 20)
- **Response**: List of `MovieResponse`

#### Get Genres
- **Method**: GET
- **Path**: `/api/movies/genres`
- **Response**: List of `GenreResponse`

### Movies

#### Movie Details
- **Method**: GET
- **Path**: `/api/movies/movies/{movie_id}`
- **Parameters**: `include_cast` (bool, optional), `include_crew` (bool, optional), `include_reviews` (bool, optional)
- **Response**: `MovieDetail`
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/movies/movies/550?include_cast=true"
  ```

#### Movie Cast
- **Method**: GET
- **Path**: `/api/movies/movies/{movie_id}/cast`
- **Parameters**: `limit` (int, optional, default: 20)
- **Response**: List of `CastMember`

#### Movie Crew
- **Method**: GET
- **Path**: `/api/movies/movies/{movie_id}/crew`
- **Parameters**: `department` (string, optional), `limit` (int, optional, default: 20)
- **Response**: List of `CrewMember`

#### Movie Trailers
- **Method**: GET
- **Path**: `/api/movies/movies/{movie_id}/trailers`
- **Response**: List of `TrailerResponse`

#### Movie Reviews
- **Method**: GET
- **Path**: `/api/movies/movies/{movie_id}/reviews`
- **Parameters**: `limit` (int, optional, default: 20), `offset` (int, optional, default: 0)
- **Response**: List of `ReviewResponse`

#### Movie Similar
- **Method**: GET
- **Path**: `/api/movies/movies/{movie_id}/similar`
- **Parameters**: `limit` (int, optional, default: 20)
- **Response**: List of `MovieResponse`

#### Movie Qualities
- **Method**: GET
- **Path**: `/api/movies/movies/{movie_id}/qualities`
- **Response**: List of `VideoQualityResponse`

#### Sync Movie from TMDB
- **Method**: POST
- **Path**: `/api/movies/movies/{movie_id}/sync`
- **Auth Required**: Admin only
- **Response**: `MovieDetail`

### TV Shows

#### TV Show Details
- **Method**: GET
- **Path**: `/api/movies/tv/{tv_show_id}`
- **Parameters**: `include_cast` (bool, optional), `include_crew` (bool, optional), `include_seasons` (bool, optional)
- **Response**: `TVShowDetail`

#### Season Details
- **Method**: GET
- **Path**: `/api/movies/tv/{tv_show_id}/season/{season_number}`
- **Parameters**: `include_episodes` (bool, optional)
- **Response**: `SeasonDetail`

#### Episode Details
- **Method**: GET
- **Path**: `/api/movies/tv/{tv_show_id}/season/{season_number}/episode/{episode_number}`
- **Response**: `EpisodeResponse`

#### TV Show Cast/Crew/Reviews/Similar
- Similar to movie endpoints: `/api/movies/tv/{tv_show_id}/cast`, `/crew`, `/reviews`, `/similar`

#### Sync TV Show from TMDB
- **Method**: POST
- **Path**: `/api/movies/tv/{tv_show_id}/sync`
- **Auth Required**: Admin only

### People

#### Person Details
- **Method**: GET
- **Path**: `/api/movies/people/{person_id}`
- **Parameters**: `include_credits` (bool, optional)
- **Response**: `PersonDetail`

#### Person Movie Credits
- **Method**: GET
- **Path**: `/api/movies/people/{person_id}/movie-credits`
- **Response**: Dict with cast and crew lists

#### Person TV Credits
- **Method**: GET
- **Path**: `/api/movies/people/{person_id}/tv-credits`
- **Response**: Dict with cast and crew lists

### Watchlist

#### Get Watchlist
- **Method**: GET
- **Path**: `/api/movies/watchlist`
- **Parameters**: `content_type` (string, optional): movie/tv, `limit`, `offset`, `profile_id` (header)
- **Response**: `WatchlistResponse`
- **Auth Required**: Yes

#### Add to Watchlist
- **Method**: POST
- **Path**: `/api/movies/watchlist`
- **Body**: `WatchlistAdd`
- **Auth Required**: Yes

#### Update Watchlist Item
- **Method**: PUT
- **Path**: `/api/movies/watchlist/{watchlist_id}`
- **Body**: `WatchlistUpdate`
- **Auth Required**: Yes

#### Remove from Watchlist
- **Method**: DELETE
- **Path**: `/api/movies/watchlist/{watchlist_id}`
- **Auth Required**: Yes

#### Check in Watchlist
- **Method**: GET
- **Path**: `/api/movies/watchlist/contains`
- **Parameters**: `item_ids` (string), `content_type` (string), `profile_id` (header)
- **Response**: Dict mapping item_id to boolean

### Viewing History

#### Get Viewing History
- **Method**: GET
- **Path**: `/api/movies/history`
- **Parameters**: `content_type` (optional), `limit`, `offset`, `profile_id` (header)
- **Response**: List of `ViewingHistoryResponse`

#### Record Viewing
- **Method**: POST
- **Path**: `/api/movies/history`
- **Body**: `ViewingProgressUpdate`
- **Auth Required**: Yes

#### Update Progress
- **Method**: PUT
- **Path**: `/api/movies/history/{history_id}/progress`
- **Body**: `ViewingProgressUpdate`

#### Get Recently Watched
- **Method**: GET
- **Path**: `/api/movies/history/recent`
- **Parameters**: `limit`, `profile_id` (header)

#### Get Watch Stats
- **Method**: GET
- **Path**: `/api/movies/history/stats`
- **Parameters**: `time_range` (string), `profile_id` (header)
- **Response**: `WatchStatsResponse`

#### Get Continue Watching
- **Method**: GET
- **Path**: `/api/movies/continue-watching`
- **Parameters**: `limit`, `profile_id` (header)
- **Response**: `ContinueWatchingResponse`

#### Mark as Completed
- **Method**: POST
- **Path**: `/api/movies/history/{history_id}/complete`

### Reviews & Ratings

#### Get Movie Reviews
- **Method**: GET
- **Path**: `/api/movies/reviews/movie/{movie_id}`
- **Parameters**: `limit`, `offset`

#### Add Review
- **Method**: POST
- **Path**: `/api/movies/reviews`
- **Body**: `ReviewCreate`
- **Auth Required**: Yes

#### Update Review
- **Method**: PUT
- **Path**: `/api/movies/reviews/{review_id}`
- **Body**: `ReviewUpdate`

#### Delete Review
- **Method**: DELETE
- **Path**: `/api/movies/reviews/{review_id}`

#### Mark Review Helpful
- **Method**: POST
- **Path**: `/api/movies/reviews/{review_id}/helpful`

### Profile Management

#### Get User Profiles
- **Method**: GET
- **Path**: `/api/movies/profiles`
- **Auth Required**: Yes
- **Response**: List of `ProfileResponse`

#### Create Profile
- **Method**: POST
- **Path**: `/api/movies/profiles`
- **Body**: `ProfileCreate`

#### Get Profile
- **Method**: GET
- **Path**: `/api/movies/profiles/{profile_id}`

#### Update Profile
- **Method**: PUT
- **Path**: `/api/movies/profiles/{profile_id}`
- **Body**: `ProfileUpdate`

#### Delete Profile
- **Method**: DELETE
- **Path**: `/api/movies/profiles/{profile_id}`

#### Switch Profile
- **Method**: POST
- **Path**: `/api/movies/profiles/{profile_id}/switch`

### Watch Party

#### Create Watch Party
- **Method**: POST
- **Path**: `/api/movies/watch-party`
- **Body**: `WatchPartyCreate`
- **Auth Required**: Yes
- **Response**: `WatchPartyResponse`

#### Join Watch Party
- **Method**: POST
- **Path**: `/api/movies/watch-party/join`
- **Body**: `WatchPartyJoin`

#### Get Watch Party
- **Method**: GET
- **Path**: `/api/movies/watch-party/{party_code}`

#### Update Position
- **Method**: PUT
- **Path**: `/api/movies/watch-party/{party_id}/position`
- **Body**: `WatchPartyUpdate`

#### Update Status
- **Method**: PUT
- **Path**: `/api/movies/watch-party/{party_id}/status`
- **Body**: `WatchPartyUpdate`

#### Leave Watch Party
- **Method**: POST
- **Path**: `/api/movies/watch-party/{party_id}/leave`

#### End Watch Party
- **Method**: DELETE
- **Path**: `/api/movies/watch-party/{party_id}`

#### Get Active Watch Parties
- **Method**: GET
- **Path**: `/api/movies/watch-party/active`
- **Auth Required**: Yes

#### Get Participants
- **Method**: GET
- **Path**: `/api/movies/watch-party/{party_id}/participants`

### Video Quality

#### Get Qualities for Movie
- **Method**: GET
- **Path**: `/api/movies/qualities/movie/{movie_id}`

#### Get Optimal Quality
- **Method**: GET
- **Path**: `/api/movies/qualities/optimal`
- **Parameters**: `bandwidth_kbps` (int), `movie_id` or `episode_id`

#### Add Video Quality
- **Method**: POST
- **Path**: `/api/movies/qualities`
- **Body**: `VideoQualityCreate`
- **Auth Required**: Admin only

#### Delete Video Quality
- **Method**: DELETE
- **Path**: `/api/movies/qualities/{quality_id}`

## Data Models

### Entity Relationship Diagram (Text-based)

```
User --1:N--> UserProfile
User --1:N--> Review

UserProfile --1:N--> Watchlist
UserProfile --1:N--> ViewingHistory
UserProfile --1:N--> WatchParty (host)
UserProfile --N:M--> WatchParty (participants)

MovieDetail --1:N--> MovieCast
MovieDetail --1:N--> MovieCrew
MovieDetail --1:N--> Review
MovieDetail --1:N--> Watchlist
MovieDetail --1:N--> ViewingHistory
MovieDetail --1:N--> VideoQuality

TVShow --1:N--> Season
TVShow --1:N--> TVShowCast
TVShow --1:N--> TVShowCrew
TVShow --1:N--> Review
TVShow --1:N--> Watchlist
TVShow --1:N--> ViewingHistory

Season --1:N--> Episode

Episode --1:N--> ViewingHistory
Episode --1:N--> VideoQuality

Person --N:M--> MovieDetail (via MovieCast/MovieCrew)
Person --N:M--> TVShow (via TVShowCast/TVShowCrew)

WatchParty --1:N--> WatchPartyParticipant
WatchParty --N:1--> MovieDetail or Episode
```

### Model Descriptions

- **MovieDetail**: Comprehensive movie information from TMDB
- **TVShow**: TV series with seasons and episodes
- **Season**: TV show seasons with episode counts
- **Episode**: Individual TV episodes
- **Person**: Actors, directors, crew members
- **MovieCast/MovieCrew**: Association tables for movie credits
- **TVShowCast/TVShowCrew**: Association tables for TV credits
- **Review**: User reviews and ratings
- **Watchlist**: User's saved movies/TV shows per profile
- **ViewingHistory**: Playback progress and history per profile
- **UserProfile**: User profiles for multi-profile support
- **WatchParty**: Real-time viewing sessions
- **WatchPartyParticipant**: Users in watch parties
- **VideoQuality**: Streaming quality options and URLs

## Multi-Profile Support

### How Profiles Work

Each user can create multiple profiles, similar to Netflix. Profiles isolate:
- Watchlist items
- Viewing history and progress
- Maturity rating preferences
- Autoplay settings

### Creating and Managing Profiles

Use `/api/movies/profiles` endpoints to create, update, and delete profiles. Each profile has:
- Unique name per user
- Avatar URL
- Kids mode flag
- Maturity rating (G/PG/PG13/R/NC17)
- Language preference
- Autoplay settings

### Profile-Specific Data

All watchlist, history, and watch party data is tied to profiles. Specify the active profile via `X-Profile-Id` header.

### Kids Profiles and Maturity Ratings

Kids profiles filter content based on maturity ratings. The system checks ratings against profile settings before returning results.

## Continue Watching Feature

### How Viewing Progress is Tracked

Progress is recorded via `/api/movies/history` endpoints. Each viewing session tracks:
- Current position (seconds)
- Total duration
- Completion status
- Device type and quality

### Resume Points and Completion Thresholds

- **Continue Watching Threshold**: Minimum watch percentage to appear in continue watching (default: 5%)
- **Completed Threshold**: Minimum watch percentage to mark as completed (default: 90%)

### API Endpoints for Continue Watching

Use `GET /api/movies/continue-watching` to fetch incomplete items ordered by last watched time.

## Watch Party Feature

### How Watch Party Works

Watch parties enable synchronized viewing across multiple users. The host controls playback, and changes are broadcast via WebSocket.

### Creating and Joining Parties

1. Host creates party with `POST /api/movies/watch-party`
2. Receives unique 6-character party code
3. Participants join with `POST /api/movies/watch-party/join`

### WebSocket Protocol for Real-Time Sync

Connect to `ws://localhost:8000/api/movies/ws/watch-party/{party_code}?token={firebase_token}&profile_id={id}`

#### Message Types

- `{"type": "join", "profile_id": int}` - User joins
- `{"type": "leave"}` - User leaves
- `{"type": "play", "position": int}` - Host starts playback
- `{"type": "pause", "position": int}` - Host pauses
- `{"type": "seek", "position": int}` - Host seeks
- `{"type": "sync_request"}` - Request current state
- `{"type": "chat", "message": str}` - Send chat message

#### Event Handling

Server broadcasts events to all participants. Clients should update their player state accordingly.

#### Example Client Implementation

```javascript
class WatchPartyClient {
    constructor(partyCode, token, profileId) {
        this.ws = new WebSocket(`ws://localhost:8000/api/movies/ws/watch-party/${partyCode}?token=${token}&profile_id=${profileId}`);
        this.ws.onmessage = this.handleMessage.bind(this);
    }
    
    handleMessage(event) {
        const data = JSON.parse(event.data);
        switch(data.type) {
            case 'play':
                player.play();
                player.currentTime = data.position;
                break;
            case 'pause':
                player.pause();
                player.currentTime = data.position;
                break;
            case 'seek':
                player.currentTime = data.position;
                break;
        }
    }
    
    sendMessage(type, data = {}) {
        this.ws.send(JSON.stringify({type, ...data}));
    }
}
```

## Video Streaming & Quality

### Quality Settings (360p to 4K)

Supported qualities: 360p, 480p, 720p, 1080p, 4K. Each has different bitrate and file size.

### Adaptive Quality Selection Based on Bandwidth

Use `GET /api/movies/qualities/optimal?bandwidth_kbps=5000&movie_id=550` to get the best quality for user's connection.

### CDN Integration

Video URLs are served from configured CDN. Format: `{cdn_url}/movies/{movie_id}/{quality}.mp4`

### Video URL Structure

- Movies: `/movies/{movie_id}/{quality}.mp4`
- Episodes: `/tv/{tv_show_id}/season/{season_number}/episode/{episode_number}/{quality}.mp4`

## Recommendations System

### Personalized Recommendations Algorithm

Combines collaborative filtering (based on similar users' preferences) with content-based filtering (genre, actors, directors).

### TMDB-Based Recommendations

Uses TMDB's recommendation API for similar movies/TV shows.

### Trending and Popular Content

Fetches trending/popular content from TMDB, cached for performance.

### Genre-Based Discovery

Browse movies/TV by genre using `/api/movies/genres/{id}/movies`.

## Reviews & Ratings

### Adding and Managing Reviews

Users can review movies or TV shows with ratings (1-10) and text. Reviews can be marked as containing spoilers.

### Rating System (1-10)

Ratings are averaged to show overall scores. Users can update their own reviews.

### Spoiler Warnings

Reviews with `is_spoiler: true` are hidden by default, with a "Show Spoiler" toggle.

### Helpful Votes

Users can mark reviews as helpful, incrementing the `helpful_count`.

## Integration Examples

### Python Client

```python
import requests

class MovieAPIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def search_movies(self, query, limit=20):
        response = requests.get(
            f'{self.base_url}/api/movies/search',
            params={'query': query, 'content_type': 'movie', 'limit': limit},
            headers=self.headers
        )
        return response.json()
    
    def add_to_watchlist(self, profile_id, movie_id, priority=3):
        data = {'movie_id': movie_id, 'priority': priority}
        response = requests.post(
            f'{self.base_url}/api/movies/watchlist',
            json=data,
            headers={**self.headers, 'X-Profile-Id': str(profile_id)}
        )
        return response.json()
```

### JavaScript/TypeScript Client

```typescript
class MovieAPI {
    constructor(private baseURL: string, private token: string) {}
    
    async getRecommendations(profileId: number, limit = 20) {
        const response = await fetch(
            `${this.baseURL}/api/movies/recommendations?limit=${limit}`,
            {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'X-Profile-Id': profileId.toString()
                }
            }
        );
        return response.json();
    }
    
    async createWatchParty(profileId: number, movieId: number) {
        const response = await fetch(
            `${this.baseURL}/api/movies/watch-party`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'X-Profile-Id': profileId.toString(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({movie_id: movieId, max_participants: 5, is_public: false})
            }
        );
        return response.json();
    }
}
```

### Flutter/Dart Client

```dart
class MovieService {
    final String baseUrl;
    final String token;
    
    Future<List<dynamic>> getContinueWatching(int profileId, {int limit = 10}) async {
        final response = await http.get(
            Uri.parse('$baseUrl/api/movies/continue-watching?limit=$limit'),
            headers: {
                'Authorization': 'Bearer $token',
                'X-Profile-Id': profileId.toString()
            }
        );
        return json.decode(response.body)['items'];
    }
    
    Future<void> recordViewing(int profileId, int movieId, int progressSeconds, int durationSeconds) async {
        await http.post(
            Uri.parse('$baseUrl/api/movies/history'),
            headers: {
                'Authorization': 'Bearer $token',
                'X-Profile-Id': profileId.toString(),
                'Content-Type': 'application/json'
            },
            body: json.encode({
                'movie_id': movieId,
                'progress_seconds': progressSeconds,
                'duration_seconds': durationSeconds,
                'completed': false,
                'device_type': 'mobile',
                'quality_setting': '720p'
            })
        );
    }
}
```

### WebSocket Client Example for Watch Party

```javascript
// Using WebSocket API
const ws = new WebSocket(`ws://localhost:8000/api/movies/ws/watch-party/${partyCode}?token=${token}&profile_id=${profileId}`);

ws.onopen = () => {
    console.log('Connected to watch party');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Handle sync events
    if (data.type === 'play') {
        videoPlayer.play();
        videoPlayer.currentTime = data.position;
    }
};

ws.onclose = () => {
    console.log('Disconnected from watch party');
};

// Send chat message
ws.send(JSON.stringify({
    type: 'chat',
    message: 'Great movie!'
}));
```

## Caching Strategy

### What Data is Cached

- TMDB API responses (movies, TV shows, people)
- Search results
- Recommendations
- Popular/trending lists

### Cache Invalidation Rules

- TMDB data: Expires after `TMDB_CACHE_TTL` (default: 1 hour)
- User-specific data: Invalidated on changes (add to watchlist, record viewing)
- Search results: Cached per query hash

### Performance Considerations

Redis caching reduces TMDB API calls. Cache keys include user/profile IDs for personalization.

## Rate Limiting

### TMDB API Rate Limits

TMDB allows 40 requests per 10 seconds. The service implements backoff and caching to stay within limits.

### Backend Rate Limiting Strategy

- 100 requests per minute per user for search/recommendations
- 10 requests per minute for TMDB sync operations

### Best Practices for Clients

- Cache results client-side
- Use pagination to limit requests
- Implement exponential backoff on 429 errors

## Error Handling

### Common Error Codes and Their Meanings

- `400`: Bad Request - Invalid parameters
- `401`: Unauthorized - Missing/invalid token
- `403`: Forbidden - Profile access denied
- `404`: Not Found - Movie/TV show doesn't exist
- `429`: Too Many Requests - Rate limited
- `500`: Internal Server Error - TMDB API unavailable

### How to Handle API Unavailability

Fallback to cached data or mock responses. Check `settings.has_tmdb` for TMDB status.

### Fallback Strategies

- Serve cached data with warning
- Use database-only mode for basic features
- Graceful degradation for recommendations

## Migration Guide

### How to Migrate from the Old Movie Model

The old `Movie` model in `enhanced_post.py` is deprecated. New features use models in `movie.py`.

### Database Migration Steps

1. Run `alembic upgrade head` to create new tables
2. Optionally migrate existing data using a script
3. Update code to use new models/endpoints

### Data Migration Script Considerations

```python
# Example migration script
from app.models.enhanced_post import Movie as OldMovie
from app.models.movie import MovieDetail

def migrate_movies(db: Session):
    old_movies = db.query(OldMovie).all()
    for old in old_movies:
        new_movie = MovieDetail(
            tmdb_id=old.tmdb_id,
            title=old.title,
            # ... map other fields
        )
        db.add(new_movie)
        old.migrated_to_movie_id = new_movie.id
    db.commit()
```

## Testing

### How to Test with Mock Data

Use `/api/movies` (fallback) when TMDB is not configured. It serves mock data from posts.

### How to Test with TMDB API

Set `TMDB_API_KEY` and test sync endpoints. Use real TMDB IDs for testing.

### Example Test Cases

- Search for "The Matrix" and verify results
- Add movie to watchlist and check retrieval
- Create watch party and join with WebSocket

### Watch Party Testing

Use multiple browser tabs or WebSocket clients to test synchronization.

## Troubleshooting

### Common Issues and Solutions

- **TMDB API errors**: Check API key and network connectivity
- **WebSocket disconnections**: Verify token validity and party code
- **Profile access denied**: Ensure correct `X-Profile-Id` header

### Debug Logging

Enable debug logs to see TMDB requests and WebSocket events.

### FAQ

**Q: How do I enable 4K streaming?**
A: Add "4K" to `STREAMING_QUALITIES` and ensure CDN supports it.

**Q: Can I have unlimited profiles?**
A: Currently limited to reasonable numbers; contact admin for increases.

**Q: What happens if TMDB is down?**
A: System falls back to cached data or mock mode.