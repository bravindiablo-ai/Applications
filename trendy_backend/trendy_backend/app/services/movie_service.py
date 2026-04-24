"""
Movie Service for TRENDY App
Provides comprehensive movie functionality with TMDB integration
"""

import hashlib
import json
import logging
import random
import string
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union

import tmdbsimple as tmdb
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_, or_, text

from app.core.config import get_settings
from app.services.cache_service import CacheService
from app.services.personalization_service import PersonalizationService
from app.models.movie import (
    MovieDetail, TVShow, Season, Episode, Person, MovieCast, MovieCrew,
    TVShowCast, TVShowCrew, Review, Watchlist, ViewingHistory, UserProfile,
    WatchParty, WatchPartyParticipant, VideoQuality
)

logger = logging.getLogger(__name__)

class MovieService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        tmdb.API_KEY = self.settings.tmdb_api_key
        self.cache_service = CacheService()
        self.personalization_service = PersonalizationService(db)
        self.tmdb_api_key = self.settings.tmdb_api_key if self.settings.has_tmdb else "YOUR_TMDB_API_KEY"

    # TMDB Integration Methods

    def _get_tmdb_client(self):
        tmdb.API_KEY = self.settings.tmdb_api_key
        return tmdb

    def _cache_tmdb_data(self, key: str, data: dict, ttl: int):
        """Cache TMDB API responses using Redis"""
        try:
            import redis
            r = redis.Redis.from_url(self.settings.redis_url)
            r.setex(f"tmdb:{key}", ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Error caching TMDB data: {str(e)}")

    def _get_cached_tmdb_data(self, key: str) -> Optional[dict]:
        """Retrieve cached TMDB data"""
        try:
            import redis
            r = redis.Redis.from_url(self.settings.redis_url)
            data = r.get(f"tmdb:{key}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting cached TMDB data: {str(e)}")
            return None

    def sync_movie_from_tmdb(self, tmdb_id: int) -> MovieDetail:
        """Fetch movie from TMDB API and sync to database (with cast, crew, genres)"""
        try:
            tmdb_client = self._get_tmdb_client()
            movie = tmdb_client.Movies(tmdb_id)
            movie_data = movie.info()

            # Check if movie exists
            existing_movie = self.db.query(MovieDetail).filter(MovieDetail.tmdb_id == tmdb_id).first()
            if existing_movie:
                return existing_movie

            # Create movie
            movie_detail = MovieDetail(
                tmdb_id=tmdb_id,
                imdb_id=movie_data.get('imdb_id'),
                title=movie_data['title'],
                original_title=movie_data.get('original_title'),
                overview=movie_data.get('overview'),
                tagline=movie_data.get('tagline'),
                release_date=movie_data.get('release_date'),
                runtime_minutes=movie_data.get('runtime'),
                budget=movie_data.get('budget'),
                revenue=movie_data.get('revenue'),
                status=movie_data.get('status'),
                original_language=movie_data.get('original_language'),
                spoken_languages=json.dumps(movie_data.get('spoken_languages', [])),
                poster_path=movie_data.get('poster_path'),
                backdrop_path=movie_data.get('backdrop_path'),
                trailer_url=None,  # Will be set from videos
                homepage=movie_data.get('homepage'),
                popularity_score=movie_data.get('popularity', 0),
                vote_average=movie_data.get('vote_average', 0),
                vote_count=movie_data.get('vote_count', 0),
                adult=movie_data.get('adult', False),
                genres=json.dumps(movie_data.get('genres', [])),
                production_companies=json.dumps(movie_data.get('production_companies', [])),
                production_countries=json.dumps(movie_data.get('production_countries', [])),
                is_trending=False
            )

            self.db.add(movie_detail)
            self.db.flush()  # Get ID

            # Sync cast and crew
            credits_data = movie.credits()
            self._sync_movie_cast(movie_detail.id, credits_data.get('cast', []))
            self._sync_movie_crew(movie_detail.id, credits_data.get('crew', []))

            # Sync trailer
            videos_data = movie.videos()
            trailer = next((v for v in videos_data.get('results', []) if v['type'] == 'Trailer' and v['site'] == 'YouTube'), None)
            if trailer:
                movie_detail.trailer_url = f"https://www.youtube.com/watch?v={trailer['key']}"

            self.db.commit()
            self.db.refresh(movie_detail)

            # Cache
            self._cache_tmdb_data(f"movie:{tmdb_id}", movie_data, self.settings.tmdb_cache_ttl)

            return movie_detail
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error syncing movie {tmdb_id}: {str(e)}")
            raise

    def sync_tv_show_from_tmdb(self, tmdb_id: int) -> TVShow:
        """Fetch TV show from TMDB API and sync to database (with seasons, episodes, cast, crew)"""
        try:
            tmdb_client = self._get_tmdb_client()
            tv = tmdb_client.TV(tmdb_id)
            tv_data = tv.info()

            existing_tv = self.db.query(TVShow).filter(TVShow.tmdb_id == tmdb_id).first()
            if existing_tv:
                return existing_tv

            tv_show = TVShow(
                tmdb_id=tmdb_id,
                name=tv_data['name'],
                original_name=tv_data.get('original_name'),
                overview=tv_data.get('overview'),
                first_air_date=tv_data.get('first_air_date'),
                last_air_date=tv_data.get('last_air_date'),
                status=tv_data.get('status'),
                type=tv_data.get('type'),
                number_of_seasons=tv_data.get('number_of_seasons', 0),
                number_of_episodes=tv_data.get('number_of_episodes', 0),
                episode_run_time=json.dumps(tv_data.get('episode_run_time', [])),
                poster_path=tv_data.get('poster_path'),
                backdrop_path=tv_data.get('backdrop_path'),
                homepage=tv_data.get('homepage'),
                popularity_score=tv_data.get('popularity', 0),
                vote_average=tv_data.get('vote_average', 0),
                vote_count=tv_data.get('vote_count', 0),
                adult=tv_data.get('adult', False),
                genres=json.dumps(tv_data.get('genres', [])),
                networks=json.dumps(tv_data.get('networks', [])),
                production_companies=json.dumps(tv_data.get('production_companies', [])),
                created_by=json.dumps(tv_data.get('created_by', [])),
                in_production=tv_data.get('in_production', False),
                languages=json.dumps(tv_data.get('languages', [])),
                origin_country=json.dumps(tv_data.get('origin_country', []))
            )

            self.db.add(tv_show)
            self.db.flush()

            # Sync seasons
            for season_data in tv_data.get('seasons', []):
                season = Season(
                    tv_show_id=tv_show.id,
                    tmdb_id=season_data['id'],
                    season_number=season_data['season_number'],
                    name=season_data['name'],
                    overview=season_data.get('overview'),
                    air_date=season_data.get('air_date'),
                    episode_count=season_data.get('episode_count', 0),
                    poster_path=season_data.get('poster_path')
                )
                self.db.add(season)

            # Sync cast and crew
            credits_data = tv.credits()
            self._sync_tv_show_cast(tv_show.id, credits_data.get('cast', []))
            self._sync_tv_show_crew(tv_show.id, credits_data.get('crew', []))

            self.db.commit()
            self.db.refresh(tv_show)

            self._cache_tmdb_data(f"tv:{tmdb_id}", tv_data, self.settings.tmdb_cache_ttl)

            return tv_show
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error syncing TV show {tmdb_id}: {str(e)}")
            raise

    def sync_person_from_tmdb(self, tmdb_id: int) -> Person:
        """Fetch person (actor/director) from TMDB API and sync to database"""
        try:
            tmdb_client = self._get_tmdb_client()
            person_api = tmdb_client.People(tmdb_id)
            person_data = person_api.info()

            existing_person = self.db.query(Person).filter(Person.tmdb_id == tmdb_id).first()
            if existing_person:
                return existing_person

            person = Person(
                tmdb_id=tmdb_id,
                name=person_data['name'],
                biography=person_data.get('biography'),
                birthday=person_data.get('birthday'),
                deathday=person_data.get('deathday'),
                place_of_birth=person_data.get('place_of_birth'),
                profile_path=person_data.get('profile_path'),
                known_for_department=person_data.get('known_for_department'),
                popularity_score=person_data.get('popularity', 0),
                adult=person_data.get('adult', False),
                imdb_id=person_data.get('imdb_id'),
                homepage=person_data.get('homepage')
            )

            self.db.add(person)
            self.db.commit()
            self.db.refresh(person)

            self._cache_tmdb_data(f"person:{tmdb_id}", person_data, self.settings.tmdb_cache_ttl)

            return person
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error syncing person {tmdb_id}: {str(e)}")
            raise

    def sync_season_episodes(self, tv_show_id: int, season_number: int):
        """Fetch and sync all episodes for a season"""
        try:
            tv_show = self.db.query(TVShow).filter(TVShow.id == tv_show_id).first()
            if not tv_show:
                raise ValueError("TV show not found")

            season = self.db.query(Season).filter(Season.tv_show_id == tv_show_id, Season.season_number == season_number).first()
            if not season:
                raise ValueError("Season not found")

            tmdb_client = self._get_tmdb_client()
            tv = tmdb_client.TV(tv_show.tmdb_id)
            season_data = tv.season(season_number)

            for episode_data in season_data.get('episodes', []):
                episode = Episode(
                    season_id=season.id,
                    tmdb_id=episode_data['id'],
                    episode_number=episode_data['episode_number'],
                    name=episode_data['name'],
                    overview=episode_data.get('overview'),
                    air_date=episode_data.get('air_date'),
                    runtime_minutes=episode_data.get('runtime'),
                    still_path=episode_data.get('still_path'),
                    vote_average=episode_data.get('vote_average', 0),
                    vote_count=episode_data.get('vote_count', 0),
                    production_code=episode_data.get('production_code')
                )
                self.db.add(episode)

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error syncing season episodes: {str(e)}")
            raise

    def update_movie_metadata(self, movie_id: int):
        """Refresh movie data from TMDB"""
        movie = self.db.query(MovieDetail).filter(MovieDetail.id == movie_id).first()
        if movie:
            self.sync_movie_from_tmdb(movie.tmdb_id)

    def update_tv_show_metadata(self, tv_show_id: int):
        """Refresh TV show data from TMDB"""
        tv_show = self.db.query(TVShow).filter(TVShow.id == tv_show_id).first()
        if tv_show:
            self.sync_tv_show_from_tmdb(tv_show.tmdb_id)

    # Search Methods

    def search_movies(self, query: str, year: Optional[int], page: int) -> dict:
        """Search movies via TMDB with caching"""
        try:
            query_hash = hashlib.md5(f"{query}:{year}:{page}".encode()).hexdigest()
            cache_key = f"search:movies:{query_hash}"
            cached = self._get_cached_tmdb_data(cache_key)
            if cached:
                return cached

            tmdb_client = self._get_tmdb_client()
            search = tmdb_client.Search()
            results = search.movie(query=query, year=year, page=page)

            self._cache_tmdb_data(cache_key, results, self.settings.tmdb_cache_ttl)
            return results
        except Exception as e:
            logger.error(f"Error searching movies: {str(e)}")
            return {}

    def search_tv_shows(self, query: str, first_air_date_year: Optional[int], page: int) -> dict:
        """Search TV shows"""
        try:
            query_hash = hashlib.md5(f"{query}:{first_air_date_year}:{page}".encode()).hexdigest()
            cache_key = f"search:tv:{query_hash}"
            cached = self._get_cached_tmdb_data(cache_key)
            if cached:
                return cached

            tmdb_client = self._get_tmdb_client()
            search = tmdb_client.Search()
            results = search.tv(query=query, first_air_date_year=first_air_date_year, page=page)

            self._cache_tmdb_data(cache_key, results, self.settings.tmdb_cache_ttl)
            return results
        except Exception as e:
            logger.error(f"Error searching TV shows: {str(e)}")
            return {}

    def search_people(self, query: str, page: int) -> dict:
        """Search actors/directors"""
        try:
            query_hash = hashlib.md5(f"{query}:{page}".encode()).hexdigest()
            cache_key = f"search:people:{query_hash}"
            cached = self._get_cached_tmdb_data(cache_key)
            if cached:
                return cached

            tmdb_client = self._get_tmdb_client()
            search = tmdb_client.Search()
            results = search.person(query=query, page=page)

            self._cache_tmdb_data(cache_key, results, self.settings.tmdb_cache_ttl)
            return results
        except Exception as e:
            logger.error(f"Error searching people: {str(e)}")
            return {}

    def advanced_search(self, query: str, filters: dict) -> dict:
        """Unified search with filters (genre, year, rating, language)"""
        try:
            # Simplified implementation
            results = {'movies': [], 'tv_shows': [], 'people': []}
            if filters.get('content_type', 'all') in ['all', 'movie']:
                results['movies'] = self.search_movies(query, filters.get('year'), filters.get('page', 1))['results']
            if filters.get('content_type', 'all') in ['all', 'tv']:
                results['tv_shows'] = self.search_tv_shows(query, filters.get('year'), filters.get('page', 1))['results']
            if filters.get('content_type', 'all') in ['all', 'person']:
                results['people'] = self.search_people(query, filters.get('page', 1))['results']
            return results
        except Exception as e:
            logger.error(f"Error in advanced search: {str(e)}")
            return {}

    # Recommendation Methods

    def get_personalized_recommendations(self, user_profile_id: int, limit: int) -> List[Union[MovieDetail, TVShow]]:
        """Use viewing history and PersonalizationService for recommendations"""
        try:
            cache_key = f"recommendations:{user_profile_id}"
            cached = self._get_cached_tmdb_data(cache_key)
            if cached:
                return cached

            # Get viewing history
            history = self.db.query(ViewingHistory).filter(ViewingHistory.user_profile_id == user_profile_id).all()
            movie_ids = [h.movie_id for h in history if h.movie_id]
            tv_ids = [h.tv_show_id for h in history if h.tv_show_id]

            recommendations = []
            if movie_ids:
                # Get similar movies
                for movie_id in movie_ids[:5]:  # Limit to recent
                    similar = self.get_movie_recommendations(movie_id, limit // 2)
                    recommendations.extend(similar)
            if tv_ids:
                for tv_id in tv_ids[:5]:
                    similar = self.get_tv_show_recommendations(tv_id, limit // 2)
                    recommendations.extend(similar)

            # Deduplicate and limit
            seen_ids = set()
            unique_recs = []
            for rec in recommendations:
                rec_id = rec.id
                if rec_id not in seen_ids:
                    unique_recs.append(rec)
                    seen_ids.add(rec_id)
                    if len(unique_recs) >= limit:
                        break

            self._cache_tmdb_data(cache_key, unique_recs, self.settings.movie_cache_ttl)
            return unique_recs
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {str(e)}")
            return []

    def get_movie_recommendations(self, movie_id: int, limit: int) -> List[MovieDetail]:
        """Similar movies from TMDB"""
        try:
            movie = self.db.query(MovieDetail).filter(MovieDetail.id == movie_id).first()
            if not movie:
                return []

            tmdb_client = self._get_tmdb_client()
            tmdb_movie = tmdb_client.Movies(movie.tmdb_id)
            recs = tmdb_movie.recommendations(page=1)

            recommendations = []
            for rec in recs['results'][:limit]:
                try:
                    rec_movie = self.sync_movie_from_tmdb(rec['id'])
                    recommendations.append(rec_movie)
                except:
                    pass

            return recommendations
        except Exception as e:
            logger.error(f"Error getting movie recommendations: {str(e)}")
            return []

    def get_tv_show_recommendations(self, tv_show_id: int, limit: int) -> List[TVShow]:
        """Similar TV shows"""
        try:
            tv_show = self.db.query(TVShow).filter(TVShow.id == tv_show_id).first()
            if not tv_show:
                return []

            tmdb_client = self._get_tmdb_client()
            tv = tmdb_client.TV(tv_show.tmdb_id)
            recs = tv.recommendations(page=1)

            recommendations = []
            for rec in recs['results'][:limit]:
                try:
                    rec_tv = self.sync_tv_show_from_tmdb(rec['id'])
                    recommendations.append(rec_tv)
                except:
                    pass

            return recommendations
        except Exception as e:
            logger.error(f"Error getting TV show recommendations: {str(e)}")
            return []

    def get_trending_movies(self, time_window: str, limit: int) -> List[MovieDetail]:
        """Trending movies (day/week) from TMDB"""
        try:
            cache_key = f"trending:movies:{time_window}"
            cached = self._get_cached_tmdb_data(cache_key)
            if cached:
                return cached

            tmdb_client = self._get_tmdb_client()
            trending = tmdb_client.Trending()
            results = trending.movie(time_window=time_window)

            movies = []
            for result in results['results'][:limit]:
                try:
                    movie = self.sync_movie_from_tmdb(result['id'])
                    movies.append(movie)
                except:
                    pass

            self._cache_tmdb_data(cache_key, movies, self.settings.tmdb_cache_ttl)
            return movies
        except Exception as e:
            logger.error(f"Error getting trending movies: {str(e)}")
            return []

    def get_trending_tv_shows(self, time_window: str, limit: int) -> List[TVShow]:
        """Trending TV shows"""
        try:
            cache_key = f"trending:tv:{time_window}"
            cached = self._get_cached_tmdb_data(cache_key)
            if cached:
                return cached

            tmdb_client = self._get_tmdb_client()
            trending = tmdb_client.Trending()
            results = trending.tv(time_window=time_window)

            tv_shows = []
            for result in results['results'][:limit]:
                try:
                    tv = self.sync_tv_show_from_tmdb(result['id'])
                    tv_shows.append(tv)
                except:
                    pass

            self._cache_tmdb_data(cache_key, tv_shows, self.settings.tmdb_cache_ttl)
            return tv_shows
        except Exception as e:
            logger.error(f"Error getting trending TV shows: {str(e)}")
            return []

    def get_popular_movies(self, limit: int) -> List[MovieDetail]:
        """Popular movies from TMDB"""
        try:
            tmdb_client = self._get_tmdb_client()
            movies = tmdb_client.Movies()
            results = movies.popular(page=1)

            popular = []
            for result in results['results'][:limit]:
                try:
                    movie = self.sync_movie_from_tmdb(result['id'])
                    popular.append(movie)
                except:
                    pass

            return popular
        except Exception as e:
            logger.error(f"Error getting popular movies: {str(e)}")
            return []

    def get_top_rated_movies(self, limit: int) -> List[MovieDetail]:
        """Top rated movies"""
        try:
            tmdb_client = self._get_tmdb_client()
            movies = tmdb_client.Movies()
            results = movies.top_rated(page=1)

            top_rated = []
            for result in results['results'][:limit]:
                try:
                    movie = self.sync_movie_from_tmdb(result['id'])
                    top_rated.append(movie)
                except:
                    pass

            return top_rated
        except Exception as e:
            logger.error(f"Error getting top rated movies: {str(e)}")
            return []

    def get_upcoming_movies(self, limit: int) -> List[MovieDetail]:
        """Upcoming releases"""
        try:
            tmdb_client = self._get_tmdb_client()
            movies = tmdb_client.Movies()
            results = movies.upcoming(page=1)

            upcoming = []
            for result in results['results'][:limit]:
                try:
                    movie = self.sync_movie_from_tmdb(result['id'])
                    upcoming.append(movie)
                except:
                    pass

            return upcoming
        except Exception as e:
            logger.error(f"Error getting upcoming movies: {str(e)}")
            return []

    def get_now_playing_movies(self, limit: int) -> List[MovieDetail]:
        """Now playing in theaters"""
        try:
            tmdb_client = self._get_tmdb_client()
            movies = tmdb_client.Movies()
            results = movies.now_playing(page=1)

            now_playing = []
            for result in results['results'][:limit]:
                try:
                    movie = self.sync_movie_from_tmdb(result['id'])
                    now_playing.append(movie)
                except:
                    pass

            return now_playing
        except Exception as e:
            logger.error(f"Error getting now playing movies: {str(e)}")
            return []

    def get_movies_by_genre(self, genre_id: int, limit: int) -> List[MovieDetail]:
        """Movies filtered by genre"""
        try:
            tmdb_client = self._get_tmdb_client()
            discover = tmdb_client.Discover()
            results = discover.movie(with_genres=str(genre_id), page=1)

            movies = []
            for result in results['results'][:limit]:
                try:
                    movie = self.sync_movie_from_tmdb(result['id'])
                    movies.append(movie)
                except:
                    pass

            return movies
        except Exception as e:
            logger.error(f"Error getting movies by genre: {str(e)}")
            return []

    # Watchlist Management Methods

    def add_to_watchlist(self, user_profile_id: int, movie_id: Optional[int], tv_show_id: Optional[int], priority: int, notes: str) -> Watchlist:
        """Add to watchlist"""
        try:
            watchlist_item = Watchlist(
                user_profile_id=user_profile_id,
                movie_id=movie_id,
                tv_show_id=tv_show_id,
                priority=priority,
                notes=notes,
                added_at=datetime.utcnow()
            )
            self.db.add(watchlist_item)
            self.db.commit()
            self.db.refresh(watchlist_item)
            return watchlist_item
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding to watchlist: {str(e)}")
            raise

    def remove_from_watchlist(self, user_profile_id: int, watchlist_id: int) -> bool:
        """Remove from watchlist"""
        try:
            deleted = self.db.query(Watchlist).filter(
                Watchlist.id == watchlist_id,
                Watchlist.user_profile_id == user_profile_id
            ).delete()
            self.db.commit()
            return deleted > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing from watchlist: {str(e)}")
            return False

    def get_user_watchlist(self, user_profile_id: int, content_type: Optional[str], limit: int, offset: int) -> List[Watchlist]:
        """Get watchlist with optional filter (movie/tv)"""
        try:
            query = self.db.query(Watchlist).filter(Watchlist.user_profile_id == user_profile_id)
            if content_type == 'movie':
                query = query.filter(Watchlist.movie_id.isnot(None))
            elif content_type == 'tv':
                query = query.filter(Watchlist.tv_show_id.isnot(None))
            return query.order_by(Watchlist.added_at.desc()).offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting user watchlist: {str(e)}")
            return []

    def update_watchlist_priority(self, watchlist_id: int, priority: int) -> Watchlist:
        """Update watchlist priority"""
        try:
            watchlist_item = self.db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
            if not watchlist_item:
                raise ValueError("Watchlist item not found")
            watchlist_item.priority = priority
            self.db.commit()
            self.db.refresh(watchlist_item)
            return watchlist_item
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating watchlist priority: {str(e)}")
            raise

    def is_in_watchlist(self, user_profile_id: int, movie_id: Optional[int], tv_show_id: Optional[int]) -> bool:
        """Check if in watchlist"""
        try:
            query = self.db.query(Watchlist).filter(Watchlist.user_profile_id == user_profile_id)
            if movie_id:
                query = query.filter(Watchlist.movie_id == movie_id)
            if tv_show_id:
                query = query.filter(Watchlist.tv_show_id == tv_show_id)
            return query.first() is not None
        except Exception as e:
            logger.error(f"Error checking watchlist: {str(e)}")
            return False

    # Viewing History Methods

    def record_viewing(self, user_profile_id: int, movie_id: Optional[int], tv_show_id: Optional[int], episode_id: Optional[int], progress_seconds: int, duration_seconds: int, completed: bool, device_type: str, quality_setting: str) -> ViewingHistory:
        """Record viewing"""
        try:
            viewing = ViewingHistory(
                user_profile_id=user_profile_id,
                movie_id=movie_id,
                tv_show_id=tv_show_id,
                episode_id=episode_id,
                watched_at=datetime.utcnow(),
                progress_seconds=progress_seconds,
                duration_seconds=duration_seconds,
                completed=completed,
                device_type=device_type,
                quality_setting=quality_setting,
                watch_count=1
            )
            self.db.add(viewing)
            self.db.commit()
            self.db.refresh(viewing)
            return viewing
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recording viewing: {str(e)}")
            raise

    def update_viewing_progress(self, history_id: int, progress_seconds: int, completed: bool) -> ViewingHistory:
        """Update viewing progress"""
        try:
            viewing = self.db.query(ViewingHistory).filter(ViewingHistory.id == history_id).first()
            if not viewing:
                raise ValueError("Viewing history not found")
            viewing.progress_seconds = progress_seconds
            viewing.completed = completed
            viewing.last_position_seconds = progress_seconds
            self.db.commit()
            self.db.refresh(viewing)
            return viewing
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating viewing progress: {str(e)}")
            raise

    def get_continue_watching(self, user_profile_id: int, limit: int) -> List[ViewingHistory]:
        """Get incomplete items ordered by watched_at desc"""
        try:
            return self.db.query(ViewingHistory).filter(
                ViewingHistory.user_profile_id == user_profile_id,
                ViewingHistory.completed == False
            ).order_by(ViewingHistory.watched_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting continue watching: {str(e)}")
            return []

    def get_viewing_history(self, user_profile_id: int, content_type: Optional[str], limit: int, offset: int) -> List[ViewingHistory]:
        """Get viewing history"""
        try:
            query = self.db.query(ViewingHistory).filter(ViewingHistory.user_profile_id == user_profile_id)
            if content_type == 'movie':
                query = query.filter(ViewingHistory.movie_id.isnot(None))
            elif content_type == 'tv':
                query = query.filter(ViewingHistory.episode_id.isnot(None))
            return query.order_by(ViewingHistory.watched_at.desc()).offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting viewing history: {str(e)}")
            return []

    def get_recently_watched(self, user_profile_id: int, limit: int) -> List[ViewingHistory]:
        """Recently watched"""
        try:
            return self.db.query(ViewingHistory).filter(
                ViewingHistory.user_profile_id == user_profile_id
            ).order_by(ViewingHistory.watched_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting recently watched: {str(e)}")
            return []

    def mark_as_completed(self, user_profile_id: int, movie_id: Optional[int], episode_id: Optional[int]) -> ViewingHistory:
        """Mark as completed"""
        try:
            query = self.db.query(ViewingHistory).filter(ViewingHistory.user_profile_id == user_profile_id)
            if movie_id:
                query = query.filter(ViewingHistory.movie_id == movie_id)
            if episode_id:
                query = query.filter(ViewingHistory.episode_id == episode_id)
            viewing = query.order_by(ViewingHistory.watched_at.desc()).first()
            if viewing:
                viewing.completed = True
                self.db.commit()
                self.db.refresh(viewing)
            return viewing
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking as completed: {str(e)}")
            raise

    def get_watch_stats(self, user_profile_id: int, time_range: str) -> dict:
        """Statistics (total watch time, favorite genres, top actors)"""
        try:
            # Simplified
            history = self.db.query(ViewingHistory).filter(ViewingHistory.user_profile_id == user_profile_id).all()
            total_time = sum(h.progress_seconds for h in history)
            return {
                'total_watch_time_hours': total_time / 3600,
                'total_movies_watched': len(set(h.movie_id for h in history if h.movie_id)),
                'total_episodes_watched': len(set(h.episode_id for h in history if h.episode_id)),
                'favorite_genres': [],  # Placeholder
                'top_actors': []  # Placeholder
            }
        except Exception as e:
            logger.error(f"Error getting watch stats: {str(e)}")
            return {}

    # Review & Rating Methods

    def add_review(self, user_id: int, movie_id: Optional[int], tv_show_id: Optional[int], rating: float, review_text: str, is_spoiler: bool) -> Review:
        """Add review"""
        try:
            review = Review(
                user_id=user_id,
                movie_id=movie_id,
                tv_show_id=tv_show_id,
                rating=rating,
                review_text=review_text,
                is_spoiler=is_spoiler,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(review)
            self.db.commit()
            self.db.refresh(review)
            return review
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding review: {str(e)}")
            raise

    def update_review(self, review_id: int, user_id: int, rating: float, review_text: str, is_spoiler: bool) -> Review:
        """Update review"""
        try:
            review = self.db.query(Review).filter(Review.id == review_id, Review.user_id == user_id).first()
            if not review:
                raise ValueError("Review not found")
            review.rating = rating
            review.review_text = review_text
            review.is_spoiler = is_spoiler
            review.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(review)
            return review
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating review: {str(e)}")
            raise

    def delete_review(self, review_id: int, user_id: int) -> bool:
        """Delete review"""
        try:
            deleted = self.db.query(Review).filter(Review.id == review_id, Review.user_id == user_id).delete()
            self.db.commit()
            return deleted > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting review: {str(e)}")
            return False

    def get_movie_reviews(self, movie_id: int, limit: int, offset: int) -> List[Review]:
        """Get movie reviews"""
        try:
            return self.db.query(Review).filter(Review.movie_id == movie_id).order_by(Review.created_at.desc()).offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting movie reviews: {str(e)}")
            return []

    def get_tv_show_reviews(self, tv_show_id: int, limit: int, offset: int) -> List[Review]:
        """Get TV show reviews"""
        try:
            return self.db.query(Review).filter(Review.tv_show_id == tv_show_id).order_by(Review.created_at.desc()).offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting TV show reviews: {str(e)}")
            return []

    def get_user_reviews(self, user_id: int, limit: int) -> List[Review]:
        """Get user's reviews"""
        try:
            return self.db.query(Review).filter(Review.user_id == user_id).order_by(Review.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting user reviews: {str(e)}")
            return []

    def mark_review_helpful(self, review_id: int) -> Review:
        """Increment helpful_count"""
        try:
            review = self.db.query(Review).filter(Review.id == review_id).first()
            if review:
                review.helpful_count += 1
                self.db.commit()
                self.db.refresh(review)
            return review
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking review helpful: {str(e)}")
            raise

    def get_average_rating(self, movie_id: Optional[int], tv_show_id: Optional[int]) -> float:
        """Get average rating"""
        try:
            query = self.db.query(func.avg(Review.rating))
            if movie_id:
                query = query.filter(Review.movie_id == movie_id)
            if tv_show_id:
                query = query.filter(Review.tv_show_id == tv_show_id)
            avg = query.scalar()
            return avg or 0.0
        except Exception as e:
            logger.error(f"Error getting average rating: {str(e)}")
            return 0.0

    # Profile Management Methods

    def create_profile(self, user_id: int, profile_name: str, avatar_url: str, is_kids_profile: bool, maturity_rating: str) -> UserProfile:
        """Create profile"""
        try:
            profile = UserProfile(
                user_id=user_id,
                profile_name=profile_name,
                avatar_url=avatar_url,
                is_kids_profile=is_kids_profile,
                maturity_rating=maturity_rating,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating profile: {str(e)}")
            raise

    def update_profile(self, profile_id: int, user_id: int, updates: dict) -> UserProfile:
        """Update profile"""
        try:
            profile = self.db.query(UserProfile).filter(UserProfile.id == profile_id, UserProfile.user_id == user_id).first()
            if not profile:
                raise ValueError("Profile not found")
            for key, value in updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating profile: {str(e)}")
            raise

    def delete_profile(self, profile_id: int, user_id: int) -> bool:
        """Delete profile"""
        try:
            deleted = self.db.query(UserProfile).filter(UserProfile.id == profile_id, UserProfile.user_id == user_id).delete()
            self.db.commit()
            return deleted > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting profile: {str(e)}")
            return False

    def get_user_profiles(self, user_id: int) -> List[UserProfile]:
        """Get user's profiles"""
        try:
            return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).all()
        except Exception as e:
            logger.error(f"Error getting user profiles: {str(e)}")
            return []

    def get_profile_by_id(self, profile_id: int, user_id: int) -> UserProfile:
        """Get profile by ID"""
        try:
            return self.db.query(UserProfile).filter(UserProfile.id == profile_id, UserProfile.user_id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting profile by ID: {str(e)}")
            return None

    def switch_profile(self, user_id: int, profile_id: int) -> UserProfile:
        """Switch to profile"""
        try:
            profile = self.get_profile_by_id(profile_id, user_id)
            if not profile:
                raise ValueError("Profile not found")
            return profile
        except Exception as e:
            logger.error(f"Error switching profile: {str(e)}")
            raise

    # Watch Party Methods

    def create_watch_party(self, host_profile_id: int, movie_id: Optional[int], tv_show_id: Optional[int], episode_id: Optional[int], max_participants: int, is_public: bool) -> WatchParty:
        """Create watch party"""
        try:
            party_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            watch_party = WatchParty(
                host_profile_id=host_profile_id,
                movie_id=movie_id,
                tv_show_id=tv_show_id,
                episode_id=episode_id,
                party_code=party_code,
                status='waiting',
                max_participants=max_participants,
                is_public=is_public,
                started_at=datetime.utcnow()
            )
            self.db.add(watch_party)
            self.db.commit()
            self.db.refresh(watch_party)
            return watch_party
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating watch party: {str(e)}")
            raise

    def join_watch_party(self, party_code: str, user_profile_id: int) -> WatchPartyParticipant:
        """Join watch party"""
        try:
            watch_party = self.db.query(WatchParty).filter(WatchParty.party_code == party_code).first()
            if not watch_party:
                raise ValueError("Watch party not found")
            participant = WatchPartyParticipant(
                watch_party_id=watch_party.id,
                user_profile_id=user_profile_id,
                joined_at=datetime.utcnow(),
                is_active=True
            )
            self.db.add(participant)
            self.db.commit()
            self.db.refresh(participant)
            return participant
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error joining watch party: {str(e)}")
            raise

    def leave_watch_party(self, party_id: int, user_profile_id: int) -> bool:
        """Leave watch party"""
        try:
            participant = self.db.query(WatchPartyParticipant).filter(
                WatchPartyParticipant.watch_party_id == party_id,
                WatchPartyParticipant.user_profile_id == user_profile_id
            ).first()
            if participant:
                participant.left_at = datetime.utcnow()
                participant.is_active = False
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error leaving watch party: {str(e)}")
            return False

    def update_watch_party_position(self, party_id: int, position_seconds: int, status: str) -> WatchParty:
        """Update playback position and status"""
        try:
            watch_party = self.db.query(WatchParty).filter(WatchParty.id == party_id).first()
            if not watch_party:
                raise ValueError("Watch party not found")
            watch_party.current_position_seconds = position_seconds
            watch_party.status = status
            self.db.commit()
            self.db.refresh(watch_party)
            return watch_party
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating watch party position: {str(e)}")
            raise

    def get_watch_party(self, party_code: str) -> WatchParty:
        """Get watch party"""
        try:
            return self.db.query(WatchParty).filter(WatchParty.party_code == party_code).first()
        except Exception as e:
            logger.error(f"Error getting watch party: {str(e)}")
            return None

    def get_watch_party_participants(self, party_id: int) -> List[WatchPartyParticipant]:
        """Get participants"""
        try:
            return self.db.query(WatchPartyParticipant).filter(WatchPartyParticipant.watch_party_id == party_id).all()
        except Exception as e:
            logger.error(f"Error getting watch party participants: {str(e)}")
            return []

    def end_watch_party(self, party_id: int, host_profile_id: int) -> bool:
        """End watch party"""
        try:
            watch_party = self.db.query(WatchParty).filter(
                WatchParty.id == party_id,
                WatchParty.host_profile_id == host_profile_id
            ).first()
            if watch_party:
                watch_party.status = 'ended'
                watch_party.ended_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error ending watch party: {str(e)}")
            return False

    def get_active_watch_parties(self, user_profile_id: int) -> List[WatchParty]:
        """Get user's active watch parties"""
        try:
            return self.db.query(WatchParty).join(WatchPartyParticipant).filter(
                WatchPartyParticipant.user_profile_id == user_profile_id,
                WatchPartyParticipant.is_active == True,
                WatchParty.status.in_(['waiting', 'playing', 'paused'])
            ).all()
        except Exception as e:
            logger.error(f"Error getting active watch parties: {str(e)}")
            return []

    def broadcast_watch_party_event(self, party_id: int, event_type: str, data: dict):
        """Send WebSocket event to all participants"""
        # Placeholder for WebSocket integration
        pass

    # Detail Methods

    def get_movie_details(self, movie_id: int, include_cast: bool, include_crew: bool, include_reviews: bool) -> dict:
        """Return movie with related data"""
        try:
            movie = self.db.query(MovieDetail).filter(MovieDetail.id == movie_id).first()
            if not movie:
                return {}
            details = {'movie': movie}
            if include_cast:
                details['cast'] = self.get_movie_cast(movie_id, 10)
            if include_crew:
                details['crew'] = self.get_movie_crew(movie_id, None)
            if include_reviews:
                details['reviews'] = self.get_movie_reviews(movie_id, 10, 0)
            return details
        except Exception as e:
            logger.error(f"Error getting movie details: {str(e)}")
            return {}

    def get_tv_show_details(self, tv_show_id: int, include_cast: bool, include_crew: bool, include_seasons: bool) -> dict:
        """Return TV show with related data"""
        try:
            tv_show = self.db.query(TVShow).filter(TVShow.id == tv_show_id).first()
            if not tv_show:
                return {}
            details = {'tv_show': tv_show}
            if include_cast:
                details['cast'] = self.get_tv_show_cast(tv_show_id, 10)
            if include_crew:
                details['crew'] = self.get_tv_show_crew(tv_show_id, None)
            if include_seasons:
                details['seasons'] = self.db.query(Season).filter(Season.tv_show_id == tv_show_id).all()
            return details
        except Exception as e:
            logger.error(f"Error getting TV show details: {str(e)}")
            return {}

    def get_season_details(self, season_id: int, include_episodes: bool) -> dict:
        """Return season with episodes"""
        try:
            season = self.db.query(Season).filter(Season.id == season_id).first()
            if not season:
                return {}
            details = {'season': season}
            if include_episodes:
                details['episodes'] = self.db.query(Episode).filter(Episode.season_id == season_id).all()
            return details
        except Exception as e:
            logger.error(f"Error getting season details: {str(e)}")
            return {}

    def get_episode_details(self, episode_id: int) -> Episode:
        """Return episode"""
        try:
            return self.db.query(Episode).filter(Episode.id == episode_id).first()
        except Exception as e:
            logger.error(f"Error getting episode details: {str(e)}")
            return None

    def get_person_details(self, person_id: int, include_credits: bool) -> dict:
        """Return person with movie/TV credits"""
        try:
            person = self.db.query(Person).filter(Person.id == person_id).first()
            if not person:
                return {}
            details = {'person': person}
            if include_credits:
                details['movie_credits'] = []  # Placeholder
                details['tv_credits'] = []  # Placeholder
            return details
        except Exception as e:
            logger.error(f"Error getting person details: {str(e)}")
            return {}

    def get_movie_cast(self, movie_id: int, limit: int) -> List[dict]:
        """Cast with character names"""
        try:
            cast = self.db.query(MovieCast).join(Person).filter(MovieCast.movie_id == movie_id).limit(limit).all()
            return [{'person': c.person, 'character_name': c.character_name, 'order': c.order} for c in cast]
        except Exception as e:
            logger.error(f"Error getting movie cast: {str(e)}")
            return []

    def get_movie_crew(self, movie_id: int, department: Optional[str]) -> List[dict]:
        """Crew filtered by department"""
        try:
            query = self.db.query(MovieCrew).join(Person).filter(MovieCrew.movie_id == movie_id)
            if department:
                query = query.filter(MovieCrew.department == department)
            crew = query.all()
            return [{'person': c.person, 'job': c.job, 'department': c.department} for c in crew]
        except Exception as e:
            logger.error(f"Error getting movie crew: {str(e)}")
            return []

    def get_movie_trailers(self, movie_id: int) -> List[dict]:
        """Fetch trailers from TMDB"""
        try:
            movie = self.db.query(MovieDetail).filter(MovieDetail.id == movie_id).first()
            if not movie:
                return []
            tmdb_client = self._get_tmdb_client()
            tmdb_movie = tmdb_client.Movies(movie.tmdb_id)
            videos = tmdb_movie.videos()
            trailers = [v for v in videos.get('results', []) if v['type'] == 'Trailer']
            return trailers
        except Exception as e:
            logger.error(f"Error getting movie trailers: {str(e)}")
            return []

    # Video Quality Methods

    def add_video_quality(self, movie_id: Optional[int], episode_id: Optional[int], quality_label: str, video_url: str, file_size_mb: float, bitrate_kbps: int, codec: str) -> VideoQuality:
        """Add video quality"""
        try:
            quality = VideoQuality(
                movie_id=movie_id,
                episode_id=episode_id,
                quality_label=quality_label,
                video_url=video_url,
                file_size_mb=file_size_mb,
                bitrate_kbps=bitrate_kbps,
                codec=codec,
                created_at=datetime.utcnow()
            )
            self.db.add(quality)
            self.db.commit()
            self.db.refresh(quality)
            return quality
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding video quality: {str(e)}")
            raise

    def get_available_qualities(self, movie_id: Optional[int], episode_id: Optional[int]) -> List[VideoQuality]:
        """Get available qualities"""
        try:
            query = self.db.query(VideoQuality)
            if movie_id:
                query = query.filter(VideoQuality.movie_id == movie_id)
            if episode_id:
                query = query.filter(VideoQuality.episode_id == episode_id)
            return query.all()
        except Exception as e:
            logger.error(f"Error getting available qualities: {str(e)}")
            return []

    def get_optimal_quality(self, user_bandwidth_kbps: int, movie_id: Optional[int], episode_id: Optional[int]) -> VideoQuality:
        """Select best quality based on bandwidth"""
        try:
            qualities = self.get_available_qualities(movie_id, episode_id)
            if not qualities:
                return None
            # Simple selection
            suitable = [q for q in qualities if q.bitrate_kbps <= user_bandwidth_kbps]
            return max(suitable, key=lambda q: q.bitrate_kbps) if suitable else qualities[0]
        except Exception as e:
            logger.error(f"Error getting optimal quality: {str(e)}")
            return None

    def delete_video_quality(self, quality_id: int) -> bool:
        """Delete video quality"""
        try:
            deleted = self.db.query(VideoQuality).filter(VideoQuality.id == quality_id).delete()
            self.db.commit()
            return deleted > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting video quality: {str(e)}")
            return False

    # Category & Genre Methods

    def get_genres(self) -> List[dict]:
        """Get all movie/TV genres from TMDB"""
        try:
            tmdb_client = self._get_tmdb_client()
            genres = tmdb_client.Genres()
            movie_genres = genres.movie_list()['genres']
            tv_genres = genres.tv_list()['genres']
            return movie_genres + tv_genres
        except Exception as e:
            logger.error(f"Error getting genres: {str(e)}")
            return []

    def get_movies_by_category(self, category: str, limit: int) -> List[MovieDetail]:
        """Categories: trending, popular, top_rated, upcoming, now_playing"""
        try:
            if category == 'trending':
                return self.get_trending_movies('week', limit)
            elif category == 'popular':
                return self.get_popular_movies(limit)
            elif category == 'top_rated':
                return self.get_top_rated_movies(limit)
            elif category == 'upcoming':
                return self.get_upcoming_movies(limit)
            elif category == 'now_playing':
                return self.get_now_playing_movies(limit)
            return []
        except Exception as e:
            logger.error(f"Error getting movies by category: {str(e)}")
            return []

    def get_tv_shows_by_category(self, category: str, limit: int) -> List[TVShow]:
        """Categories: trending, popular, top_rated, on_the_air, airing_today"""
        try:
            if category == 'trending':
                return self.get_trending_tv_shows('week', limit)
            # Add other categories similarly
            return []
        except Exception as e:
            logger.error(f"Error getting TV shows by category: {str(e)}")
            return []

    # Helper Methods

    def _sync_movie_cast(self, movie_id: int, cast_data: list):
        """Sync movie cast"""
        for cast in cast_data[:20]:  # Limit
            person = self.sync_person_from_tmdb(cast['id'])
            movie_cast = MovieCast(
                movie_id=movie_id,
                person_id=person.id,
                character_name=cast.get('character', ''),
                order=cast.get('order', 0),
                credit_id=cast.get('credit_id', '')
            )
            self.db.add(movie_cast)

    def _sync_movie_crew(self, movie_id: int, crew_data: list):
        """Sync movie crew"""
        for crew in crew_data[:20]:  # Limit
            person = self.sync_person_from_tmdb(crew['id'])
            movie_crew = MovieCrew(
                movie_id=movie_id,
                person_id=person.id,
                job=crew.get('job', ''),
                department=crew.get('department', ''),
                credit_id=crew.get('credit_id', '')
            )
            self.db.add(movie_crew)

    def _sync_tv_show_cast(self, tv_show_id: int, cast_data: list):
        """Sync TV show cast"""
        for cast in cast_data[:20]:
            person = self.sync_person_from_tmdb(cast['id'])
            tv_cast = TVShowCast(
                tv_show_id=tv_show_id,
                person_id=person.id,
                character_name=cast.get('character', ''),
                order=cast.get('order', 0),
                credit_id=cast.get('credit_id', '')
            )
            self.db.add(tv_cast)

    def _sync_tv_show_crew(self, tv_show_id: int, crew_data: list):
        """Sync TV show crew"""
        for crew in crew_data[:20]:
            person = self.sync_person_from_tmdb(crew['id'])
            tv_crew = TVShowCrew(
                tv_show_id=tv_show_id,
                person_id=person.id,
                job=crew.get('job', ''),
                department=crew.get('department', ''),
                credit_id=crew.get('credit_id', '')
            )
            self.db.add(tv_crew)

    def get_tv_show_cast(self, tv_show_id: int, limit: int) -> List[dict]:
        """TV show cast"""
        try:
            cast = self.db.query(TVShowCast).join(Person).filter(TVShowCast.tv_show_id == tv_show_id).limit(limit).all()
            return [{'person': c.person, 'character_name': c.character_name, 'order': c.order} for c in cast]
        except Exception as e:
            logger.error(f"Error getting TV show cast: {str(e)}")
            return []

    def get_tv_show_crew(self, tv_show_id: int, department: Optional[str]) -> List[dict]:
        """TV show crew"""
        try:
            query = self.db.query(TVShowCrew).join(Person).filter(TVShowCrew.tv_show_id == tv_show_id)
            if department:
                query = query.filter(TVShowCrew.department == department)
            crew = query.all()
            return [{'person': c.person, 'job': c.job, 'department': c.department} for c in crew]
        except Exception as e:
            logger.error(f"Error getting TV show crew: {str(e)}")
            return []
