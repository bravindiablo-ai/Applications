   cp .env.example .env
   ```

2. **Configure required services**:
   - Set up PostgreSQL database and update `DATABASE_URL`
   - Set up Redis and update `REDIS_URL`
   - Download Firebase Admin SDK JSON (see [FIREBASE_SETUP.md](FIREBASE_SETUP.md))
   - Generate secure JWT secret key

3. **Optional: Add external API keys** for enhanced features:
   - OpenAI API key for AI moderation
   - Spotify credentials for music integration
   - TMDB API key for movie data
   - APISports key for football data

4. **Run the backend**:
   ```bash
   python run_backend.py
   ```

## Required Configuration

### Database
PostgreSQL is required for production use. Use the following connection string format:
```
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/database_name
```

**Local setup**:
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
createdb trendydb

# Create user (optional)
createuser trendy_user
psql -c "ALTER USER trendy_user PASSWORD 'secure_password';"
```

### Redis
Redis is used for caching and session management.
```
REDIS_URL=redis://localhost:6379
```

**Local setup**:
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
redis-server
```

### Firebase
Firebase provides authentication and storage services.

- **Project ID**: `trendy-83364`
- **API Key**: `AIzaSyBb-0MsyxpID3b8WRAyiDwDlgY19TUETEg`
- **Admin SDK JSON**: Download from Firebase Console (see [FIREBASE_SETUP.md](FIREBASE_SETUP.md))

### JWT Secret
Generate a secure secret key for JWT token signing:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Update `JWT_SECRET_KEY` in your `.env` file with the generated value.

## Core Services (Already Configured)

These services are pre-configured with test keys and ready for development:

### Agora
Real-time video/audio communication.
- App ID: `74a08e353a5f4b018526abfc2f8c851b`
- Certificate: `4d1855e4e6fb4104824a61e2f6fedf94`
- Status: Ready for development and testing

### AdMob
Mobile advertising integration.
- App ID: `ca-app-pub-9682167183617452~8170337933`
- Banner Unit: `ca-app-pub-9682167183617452/4151201875`
- Native Unit: `ca-app-pub-9682167183617452/9760990890`
- Rewarded Unit: `ca-app-pub-9682167183617452/7791063981`
- Status: Test keys configured

### Stripe
Payment processing.
- Publishable Key: `pk_test_51SLPOQCBkbX78IwPCeAbkfPB4d1GW4BPfP5XMuMCw1OpmADhKQen81BrOPFlCigqO8DbOSrn5sK73QJctXdeTuIu00AyIHt1N1`
- Secret Key: `sk_test_51SLPOQCBkbX78IwP...` (truncated for security)
- Status: Test keys configured, replace with production keys for deployment

## Optional External APIs

These services enhance TRENDY with real data but are not required - the application includes fallback implementations.

### OpenAI (AI Moderation)
**Purpose**: Advanced content moderation and sentiment analysis using GPT models.

**Fallback**: Rule-based moderation using keyword detection and pattern matching.

**Setup**:
1. Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to `.env`: `OPENAI_API_KEY=your_key_here`

**Cost**: Pay-per-use based on token consumption.

### Spotify (Music Integration)
**Purpose**: Real music catalog integration with Spotify's database.

**Fallback**: Mock music data (already implemented in `app/api/music.py`).

**Setup**:
1. Visit [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Get Client ID and Client Secret
4. Add to `.env`:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   ```

**Status**: Currently not used, mock data sufficient.

### TMDB (Movie Database)
**Purpose**: Real movie information, ratings, and metadata from The Movie Database.

**Fallback**: Database posts (already implemented in `app/api/movies.py`).

**Setup**:
1. Visit [https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
2. Create a new API key
3. Add to `.env`: `TMDB_API_KEY=your_key_here`

**Status**: Currently not used, database posts sufficient.

### APISports (Football Data)
**Purpose**: Real-time football match data, scores, and statistics.

**Fallback**: Mock match data (already implemented in `app/api/football.py`).

**Setup**:
1. Visit [https://www.api-football.com](https://www.api-football.com)
2. Sign up for an API key
3. Add to `.env`: `APISPORTS_KEY=your_key_here`

**Status**: Currently not used, mock data sufficient.

## Environment-Specific Configuration

### Development
- Use localhost URLs for database and Redis
- Use test API keys
- Enable debug logging (`DEBUG=true`)
- Use `.env` file in project root

### Staging
- Use staging server URLs
- Use test API keys
- Moderate logging
- Create `.env.staging` file

### Production
- Use production URLs and live API keys
- Disable debug logging (`DEBUG=false`)
- Use environment variables instead of `.env` files
- Create `.env.production` file

**Creating environment-specific files**:
```bash
cp .env.example .env.staging
# Edit .env.staging with staging values

cp .env.example .env.production
# Edit .env.production with production values
```

## Security Best Practices

### Never commit sensitive files
- `.env` files contain secrets and should never be committed to version control
- Firebase Admin SDK JSON files should be added to `.gitignore`
- Use `.env.example` as a template without real values

### Use strong secrets
- Generate JWT secrets using `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Use different secrets for each environment
- Rotate secrets regularly

### API key management
- Use separate keys for development, staging, and production
- Rotate API keys if compromised
- Monitor API usage and costs
- Use read-only keys where possible

### Production deployments
- Use environment variables instead of `.env` files
- Store secrets in secure key management systems (AWS KMS, Azure Key Vault, etc.)
- Enable HTTPS and SSL/TLS
- Use firewall rules to restrict access

## Verification

### Startup logs
The backend logs configuration status on startup:
```
INFO: Starting TRENDY backend in development mode
INFO: Database: localhost:5432/trendydb
INFO: Redis: localhost:6379
INFO: Firebase Project: trendy-83364
INFO: OpenAI Moderation: Disabled (using rule-based fallback)
INFO: Spotify Integration: Disabled (using mock data)
INFO: TMDB Integration: Disabled (using database posts)
INFO: APISports Integration: Disabled (using mock data)
```

### Testing services
Test each service independently:

**Database**:
```bash
python -c "from app.core.config import get_settings; s = get_settings(); print('DB OK' if s.DATABASE_URL else 'DB FAIL')"
```

**Redis**:
```bash
python -c "import redis; r = redis.Redis.from_url('redis://localhost:6379'); r.ping(); print('Redis OK')"
```

**Firebase**:
```bash
python -c "import firebase_admin; firebase_admin.initialize_app(); print('Firebase OK')"