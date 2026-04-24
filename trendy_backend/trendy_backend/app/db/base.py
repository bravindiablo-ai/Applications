"""
Import all models here for Alembic to detect them
"""
from .base_class import Base

# Import all models
from ..models.analytics_event import AnalyticsEvent, EventAggregation, UserEventSummary
from ..models.trend import Trend, TrendingCategory
from ..models.music import Artist, Album, Track, Playlist, PlayHistory, Lyrics, ArtistFollower, UserLibrary, QueueItem
from ..models.movie import MovieDetail, TVShow, Season, Episode, Person, Review, Watchlist, ViewingHistory, UserProfile, WatchParty, VideoQuality
from ..models.moderation import Report, ModerationQueue, ContentFlag
