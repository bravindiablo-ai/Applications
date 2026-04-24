"""
Analytics Engine for TRENDY App
Central analytics processing and real-time tracking
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
try:
    import redis
except Exception:
    # Lightweight in-memory Redis-like stub for local testing
    class _RedisStub:
        def __init__(self, *a, **k):
            self._store = {}
        def set(self, k, v):
            self._store[k] = v
        def get(self, k):
            return self._store.get(k)
        def delete(self, k):
            if k in self._store:
                del self._store[k]
        def publish(self, *a, **k):
            return 0
    class _RedisModule:
        Redis = _RedisStub

    redis = _RedisModule()
import json

from app.services.user_engagement_service import UserEngagementService
from app.services.analytics_event_service import AnalyticsEventService
from app.services.trending_service import TrendingService
from typing import Any

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Central analytics engine coordinating all analytics services"""

    def __init__(self, db: Session, redis_client: Optional[redis.Redis] = None):
        self.db = db
        self.redis = redis_client or redis.Redis(host='localhost', port=6379, db=0)

        # Initialize service components
        self.engagement_service = UserEngagementService(db)
        self.event_service = AnalyticsEventService(db)
        self.trending_service = TrendingService(db)

        # Real-time tracking
        self.realtime_buffer = {}
        self.buffer_size = 1000
        self.flush_interval = 60  # seconds

        # Thread pool for async processing
        self.executor = ThreadPoolExecutor(max_workers=4)

        logger.info("Analytics Engine initialized")

    def track_engagement(self, engagement_data: Any) -> Dict[str, Any]:
        """Track user engagement event"""
        try:
            engagement = self.engagement_service.track_engagement(engagement_data)

            # Add to real-time buffer
            self._add_to_realtime_buffer('engagement', engagement_data.dict())

            return {
                'success': True,
                'engagement_id': engagement.id,
                'tracked_at': engagement.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Error tracking engagement: {str(e)}")
            return {'success': False, 'error': str(e)}

    def track_event(self, event_data: Any) -> Dict[str, Any]:
        """Track analytics event"""
        try:
            event = self.event_service.log_event(event_data)

            # Add to real-time buffer
            self._add_to_realtime_buffer('event', event_data.dict())

            return {
                'success': True,
                'event_id': event.id,
                'logged_at': event.timestamp.isoformat()
            }

        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}")
            return {'success': False, 'error': str(e)}

    def start_user_session(self, session_data: Any) -> Dict[str, Any]:
        """Start user session tracking"""
        try:
            session = self.engagement_service.start_session(session_data)

            # Cache session in Redis for real-time access
            self._cache_session(session.session_id, session_data.dict())

            return {
                'success': True,
                'session_id': session.session_id,
                'started_at': session.start_time.isoformat()
            }

        except Exception as e:
            logger.error(f"Error starting session: {str(e)}")
            return {'success': False, 'error': str(e)}

    def end_user_session(self, session_id: str) -> Dict[str, Any]:
        """End user session and calculate metrics"""
        try:
            session = self.engagement_service.end_session(session_id)

            if session:
                # Remove from cache
                self._remove_cached_session(session_id)

                # Update user engagement metrics
                self._update_user_metrics_async(session.user_id)

                return {
                    'success': True,
                    'session_id': session.session_id,
                    'duration': session.duration,
                    'ended_at': session.end_time.isoformat()
                }
            else:
                return {'success': False, 'error': 'Session not found'}

        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_realtime_metrics(self, timeframe_minutes: int = 5) -> Any:
        """Get real-time analytics metrics"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=timeframe_minutes)

            # Get buffered data
            buffered_data = self._get_buffered_data(cutoff_time)

            # Get cached sessions
            active_sessions = self._get_active_sessions()

            # Calculate real-time metrics
            metrics = self._calculate_realtime_metrics(buffered_data, active_sessions)

            return RealtimeMetrics(
                timeframe_minutes=timeframe_minutes,
                active_users=metrics['active_users'],
                total_events=metrics['total_events'],
                engagement_rate=metrics['engagement_rate'],
                top_events=metrics['top_events'],
                peak_hour=metrics['peak_hour'],
                trending_topics=metrics['trending_topics']
            )

        except Exception as e:
            logger.error(f"Error getting realtime metrics: {str(e)}")
            raise

    def get_analytics_dashboard(self, days: int = 7) -> Any:
        """Get comprehensive analytics dashboard data"""
        try:
            # Get user engagement metrics
            user_metrics = self._get_user_engagement_summary(days)

            # Get event aggregations
            event_aggregations = self.event_service.get_event_aggregations(
                datetime.utcnow() - timedelta(days=days),
                datetime.utcnow()
            )

            # Get trending posts
            trending_posts = self.trending_service.get_trending_posts(limit=10)

            # Get popular events
            popular_events = self.event_service.get_popular_events(days=days, limit=5)

            # Calculate growth metrics
            growth_metrics = self._calculate_growth_metrics(days)

            return AnalyticsDashboard(
                period_days=days,
                total_users=user_metrics['total_users'],
                active_users=user_metrics['active_users'],
                total_sessions=user_metrics['total_sessions'],
                avg_session_duration=user_metrics['avg_session_duration'],
                total_events=sum(agg.total_events for agg in event_aggregations),
                event_aggregations=event_aggregations,
                trending_posts=trending_posts,
                popular_events=popular_events,
                growth_metrics=growth_metrics
            )

        except Exception as e:
            logger.error(f"Error getting analytics dashboard: {str(e)}")
            raise

    def process_analytics_batch(self) -> Dict[str, Any]:
        """Process batch analytics operations"""
        try:
            results = {}

            # Aggregate events
            event_aggregations = self.event_service.aggregate_events()
            results['event_aggregations'] = len(event_aggregations)

            # Update user summaries
            user_summaries = self.event_service.update_user_event_summaries()
            results['user_summaries'] = len(user_summaries)

            # Calculate trending scores
            trending_scores = self.trending_service.calculate_trending_scores()
            results['trending_scores'] = len(trending_scores)

            # Update trending algorithms
            updated_algorithms = self.trending_service.update_trending_algorithms()
            results['updated_algorithms'] = len(updated_algorithms)

            # Flush real-time buffer
            flushed_count = self._flush_realtime_buffer()
            results['flushed_events'] = flushed_count

            logger.info(f"Batch analytics processing completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Error in batch analytics processing: {str(e)}")
            raise

    def _add_to_realtime_buffer(self, event_type: str, data: Dict[str, Any]):
        """Add event to real-time buffer"""
        try:
            if event_type not in self.realtime_buffer:
                self.realtime_buffer[event_type] = []

            self.realtime_buffer[event_type].append({
                'data': data,
                'timestamp': datetime.utcnow()
            })

            # Auto-flush if buffer is full
            total_events = sum(len(events) for events in self.realtime_buffer.values())
            if total_events >= self.buffer_size:
                self._flush_realtime_buffer()

        except Exception as e:
            logger.error(f"Error adding to realtime buffer: {str(e)}")

    def _flush_realtime_buffer(self) -> int:
        """Flush real-time buffer to database"""
        try:
            total_flushed = 0

            for event_type, events in self.realtime_buffer.items():
                # Process events in batches
                batch_size = 100
                for i in range(0, len(events), batch_size):
                    batch = events[i:i + batch_size]
                    # Here you could implement batch processing logic
                    total_flushed += len(batch)

            # Clear buffer
            self.realtime_buffer.clear()

            logger.info(f"Flushed {total_flushed} events from realtime buffer")
            return total_flushed

        except Exception as e:
            logger.error(f"Error flushing realtime buffer: {str(e)}")
            return 0

    def _cache_session(self, session_id: str, session_data: Dict[str, Any]):
        """Cache session data in Redis"""
        try:
            key = f"session:{session_id}"
            self.redis.setex(key, 3600, json.dumps(session_data))  # 1 hour expiry
        except Exception as e:
            logger.error(f"Error caching session: {str(e)}")

    def _remove_cached_session(self, session_id: str):
        """Remove session from cache"""
        try:
            key = f"session:{session_id}"
            self.redis.delete(key)
        except Exception as e:
            logger.error(f"Error removing cached session: {str(e)}")

    def _get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get active sessions from cache"""
        try:
            active_sessions = []
            keys = self.redis.keys("session:*")
            for key in keys:
                session_data = self.redis.get(key)
                if session_data:
                    active_sessions.append(json.loads(session_data))
            return active_sessions
        except Exception as e:
            logger.error(f"Error getting active sessions: {str(e)}")
            return []

    def _get_buffered_data(self, cutoff_time: datetime) -> Dict[str, List]:
        """Get buffered data since cutoff time"""
        buffered_data = {}
        for event_type, events in self.realtime_buffer.items():
            recent_events = [
                event for event in events
                if event['timestamp'] >= cutoff_time
            ]
            buffered_data[event_type] = recent_events
        return buffered_data

    def _calculate_realtime_metrics(self, buffered_data: Dict, active_sessions: List) -> Dict[str, Any]:
        """Calculate real-time metrics from buffered data"""
        try:
            total_events = sum(len(events) for events in buffered_data.values())
            active_users = len(set(
                event['data'].get('user_id') for events in buffered_data.values()
                for event in events if event['data'].get('user_id')
            ))

            # Calculate engagement rate (simplified)
            engagement_rate = total_events / max(active_users, 1)

            # Find top events
            event_counts = {}
            for events in buffered_data.values():
                for event in events:
                    event_type = event['data'].get('event_type', 'unknown')
                    event_counts[event_type] = event_counts.get(event_type, 0) + 1

            top_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            # Find peak hour (simplified)
            peak_hour = datetime.utcnow().hour

            # Trending topics (placeholder)
            trending_topics = []

            return {
                'active_users': active_users,
                'total_events': total_events,
                'engagement_rate': round(engagement_rate, 2),
                'top_events': top_events,
                'peak_hour': peak_hour,
                'trending_topics': trending_topics
            }

        except Exception as e:
            logger.error(f"Error calculating realtime metrics: {str(e)}")
            return {
                'active_users': 0,
                'total_events': 0,
                'engagement_rate': 0.0,
                'top_events': [],
                'peak_hour': 0,
                'trending_topics': []
            }

    def _get_user_engagement_summary(self, days: int) -> Dict[str, Any]:
        """Get summary of user engagement metrics"""
        try:
            # Get top engaged users
            top_users = self.engagement_service.get_top_engaged_users(limit=100, days=days)

            # Calculate totals
            total_users = len(set(user['user_id'] for user in top_users))

            # Get session data (simplified aggregation)
            total_sessions = sum(user.get('engagement_count', 0) for user in top_users)
            avg_session_duration = 25.0  # placeholder

            return {
                'total_users': total_users,
                'active_users': len(top_users),
                'total_sessions': total_sessions,
                'avg_session_duration': avg_session_duration
            }

        except Exception as e:
            logger.error(f"Error getting user engagement summary: {str(e)}")
            return {
                'total_users': 0,
                'active_users': 0,
                'total_sessions': 0,
                'avg_session_duration': 0.0
            }

    def _calculate_growth_metrics(self, days: int) -> Dict[str, Any]:
        """Calculate growth metrics"""
        try:
            current_period = self._get_user_engagement_summary(days)
            previous_period = self._get_user_engagement_summary(days * 2)

            if previous_period['total_users'] > 0:
                user_growth = ((current_period['total_users'] - previous_period['total_users']) /
                             previous_period['total_users']) * 100
            else:
                user_growth = 0.0

            if previous_period['active_users'] > 0:
                engagement_growth = ((current_period['active_users'] - previous_period['active_users']) /
                                   previous_period['active_users']) * 100
            else:
                engagement_growth = 0.0

            return {
                'user_growth_percent': round(user_growth, 2),
                'engagement_growth_percent': round(engagement_growth, 2),
                'period_days': days
            }

        except Exception as e:
            logger.error(f"Error calculating growth metrics: {str(e)}")
            return {
                'user_growth_percent': 0.0,
                'engagement_growth_percent': 0.0,
                'period_days': days
            }

    def _update_user_metrics_async(self, user_id: int):
        """Update user metrics asynchronously"""
        try:
            # Submit to thread pool for async processing
            self.executor.submit(self._update_user_metrics_sync, user_id)
        except Exception as e:
            logger.error(f"Error submitting async user metrics update: {str(e)}")

    def _update_user_metrics_sync(self, user_id: int):
        """Update user metrics synchronously"""
        try:
            # Update engagement metrics
            self.engagement_service.get_user_engagement_metrics(user_id, days=30)

            # Update event summaries
            self.event_service.update_user_event_summaries()

            logger.info(f"Updated metrics for user {user_id}")

        except Exception as e:
            logger.error(f"Error updating user metrics: {str(e)}")

    async def start_realtime_processing(self):
        """Start real-time analytics processing loop"""
        try:
            while True:
                await asyncio.sleep(self.flush_interval)
                # Process buffered data
                self._flush_realtime_buffer()
                # Update trending scores periodically
                self.trending_service.calculate_trending_scores(hours=1)

        except Exception as e:
            logger.error(f"Error in realtime processing loop: {str(e)}")

    def shutdown(self):
        """Shutdown the analytics engine"""
        try:
            # Flush any remaining buffered data
            self._flush_realtime_buffer()

            # Shutdown thread pool
            self.executor.shutdown(wait=True)

            logger.info("Analytics Engine shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
