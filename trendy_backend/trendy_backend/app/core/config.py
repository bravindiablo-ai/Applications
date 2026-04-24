from functools import lru_cache
from typing import List, Optional
import os
import json
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings for the TRENDY backend.
    Required fields (must be configured):
    - DATABASE_URL: Database connection string
    - REDIS_URL: Redis connection string
    - FIREBASE_PROJECT_ID: Firebase project identifier
    - FIREBASE_API_KEY: Firebase API key
    - FIREBASE_CREDENTIALS_JSON: Firebase credentials JSON string
    - JWT_SECRET_KEY: Secret key for JWT token signing
    - SECRET_KEY: General secret key for encryption
    Optional fields (services will use fallbacks if not configured):
    - openai_api_key: For AI-powered moderation (falls back to rule-based)
    - apisports_key: For real football data (falls back to mock data)
    - spotify_client_id/spotify_client_secret: For Spotify integration (falls back to mock data)
    - tmdb_api_key: For TMDB movie data (falls back to database posts)
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    # Environment
    ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    # Database
    DATABASE_URL: str = Field(default="postgresql+psycopg2://postgres:postgres@localhost:5432/trendydb")
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    # JWT Authentication
    # IMPORTANT: Change this in production to a secure, randomly generated key
    JWT_SECRET_KEY: str = Field(default="your-super-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30)
    # Firebase
    # Raw JSON value for Firebase credentials (Render compatibility)
    FIREBASE_CREDENTIALS_JSON: str = Field(default="", env="FIREBASE_CREDENTIALS_JSON")
    FIREBASE_PROJECT_ID: str = Field(default="", env="FIREBASE_PROJECT_ID")
    FIREBASE_API_KEY: str = Field(default="", env="FIREBASE_API_KEY")
    firebase_credentials_path: Optional[str] = Field(default="firebase_credentials.json", env="FIREBASE_CREDENTIALS_PATH", description="Path to Firebase credentials file (used if FIREBASE_CREDENTIALS_JSON env var not set)")    # Security
    ENCRYPTION_KEY: str = Field(default="dGVzdC1lbmNyeXB0aW9uLWtleS1mb3ItZmVybmV0LWF1dGg=", env="ENCRYPTION_KEY")
    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:3000", "https://trendy.app"], env="CORS_ORIGINS")
    # SSL/HTTPS
    ssl_keyfile: Optional[str] = Field(default=None, env="SSL_KEYFILE")
    ssl_certfile: Optional[str] = Field(default=None, env="SSL_CERTFILE")
    # OpenAI for AI moderation
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    # API Keys
    apisports_key: str = Field(default="your_apisports_key_here", env="APISPORTS_KEY")
    spotify_client_id: str = Field(default="your_spotify_client_id_here", env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: str = Field(default="your_spotify_client_secret_here", env="SPOTIFY_CLIENT_SECRET")
    spotify_redirect_uri: str = Field(default="http://127.0.0.1:8000/api/music/callback", env="SPOTIFY_REDIRECT_URI")
    spotify_scopes: str = Field(default="user-library-read,user-library-modify,playlist-read-private,playlist-modify-public,playlist-modify-private,user-read-recently-played,user-top-read,user-follow-read,user-follow-modify", env="SPOTIFY_SCOPES")
    apple_music_team_id: str = Field(default="", env="APPLE_MUSIC_TEAM_ID")
    apple_music_key_id: str = Field(default="", env="APPLE_MUSIC_KEY_ID")
    apple_music_private_key_path: str = Field(default="", env="APPLE_MUSIC_PRIVATE_KEY_PATH")
    music_cache_ttl: int = Field(default=3600, env="MUSIC_CACHE_TTL")
    lyrics_api_key: Optional[str] = Field(default=None, env="LYRICS_API_KEY")
    tmdb_api_key: str = Field(default="your_tmdb_api_key_here", env="TMDB_API_KEY")
    tmdb_cache_ttl: int = Field(default=3600, env="TMDB_CACHE_TTL")
    movie_cache_ttl: int = Field(default=7200, env="MOVIE_CACHE_TTL")
    streaming_cdn_url: str = Field(default="https://cdn.yourdomain.com", env="STREAMING_CDN_URL")
    streaming_qualities: List[str] = Field(default=["360p", "480p", "720p", "1080p", "4K"], env="STREAMING_QUALITIES")
    max_watch_party_participants: int = Field(default=10, env="MAX_WATCH_PARTY_PARTICIPANTS")
    watch_party_timeout_minutes: int = Field(default=120, env="WATCH_PARTY_TIMEOUT_MINUTES")
    continue_watching_threshold_percent: int = Field(default=5, env="CONTINUE_WATCHING_THRESHOLD_PERCENT")
    completed_threshold_percent: int = Field(default=90, env="COMPLETED_THRESHOLD_PERCENT")
    # Social OAuth
    google_client_id: str = Field(default="your_google_client_id", env="GOOGLE_CLIENT_ID")
    facebook_client_id: str = Field(default="your_facebook_client_id", env="FACEBOOK_CLIENT_ID")
    facebook_client_secret: str = Field(default="your_facebook_client_secret", env="FACEBOOK_CLIENT_SECRET")
    # Payment Providers
    stripe_secret_key: str = Field(default="", env="STRIPE_SECRET_KEY", description="Stripe secret key (test: sk_test_... or prod: sk_live_...)")
    stripe_publishable_key: str = Field(default="", env="STRIPE_PUBLISHABLE_KEY")
    stripe_webhook_secret: str = Field(default="", env="STRIPE_WEBHOOK_SECRET")
    google_play_service_acc_json_path: str = Field(default="google-play-service-account.json", env="GOOGLE_PLAY_SERVICE_ACC_JSON_PATH")
    apple_api_key_id: str = Field(default="your_apple_api_key_id_here", env="APPLE_API_KEY_ID")
    apple_issuer_id: str = Field(default="your_apple_issuer_id_here", env="APPLE_ISSUER_ID")
    apple_private_key_path: str = Field(default="apple-private-key.p8", env="APPLE_PRIVATE_KEY_PATH")
    # AdMob
    admob_app_id: str = Field(default="", env="ADMOB_APP_ID")
    admob_banner_unit: str = Field(default="", env="ADMOB_BANNER_UNIT")
    admob_native_unit: str = Field(default="", env="ADMOB_NATIVE_UNIT")
    admob_rewarded_unit: str = Field(default="", env="ADMOB_REWARDED_UNIT")
    admob_banner_id: str = Field(default="/6300978111", env="ADMOB_BANNER_ID")
    admob_interstitial_id: str = Field(default="/1033173712", env="ADMOB_INTERSTITIAL_ID")
    admob_rewarded_id: str = Field(default="/5224354917", env="ADMOB_REWARDED_ID")
    # Agora Configuration
    agora_app_id: str = Field(default="", env="AGORA_APP_ID")
    agora_app_certificate: str = Field(default="", env="AGORA_APP_CERTIFICATE")
    agora_rest_host: str = Field(default="", env="AGORA_REST_HOST")
    agora_ws_host: str = Field(default="", env="AGORA_WS_HOST")
    # Storage
    cloud_storage_bucket: str = Field(default="your-cloud-storage-bucket", env="CLOUD_STORAGE_BUCKET")
    cdn_url: str = Field(default="https://cdn.yourdomain.com", env="CDN_URL")
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    otel_exporter_otlp_endpoint: Optional[str] = Field(default=None, env="OTEL_EXPORTER_OTLP_ENDPOINT")
    # Security
    secret_key: str = Field(default="your-super-secret-key-change-this-in-production", env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    # Cache
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

settings = get_settings()
