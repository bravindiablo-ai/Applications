"""
Background Analytics Aggregation Tasks for TRENDY App
Scheduled tasks for processing analytics data
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import logging
import schedule
import time
from typing import Dict, List, Any

from app.services.analytics_engine import AnalyticsEngine
from app.services.user_engagement_service import UserEngagementService
from app.services.analytics_event_service import AnalyticsEventService
from app.services.trending_service import TrendingService
from app.database import get_db

logger = logging.getLogger(__name__)

class AnalyticsAggregationTasks:
    """Background tasks for analytics aggregation"""

    def __init__(self):
        self.db = next(get_db())
        self.analytics_engine = AnalyticsEngine(self.db)
        self.engagement_service = UserEngagementService(self.db)
        self.event_service = AnalyticsEventService(self.db)
        self.trending_service = TrendingService(self.db)

        # Task tracking
        self.last_run_times = {}
        self.task_status = {}

    def schedule_daily_aggregation(self):
        """Schedule daily analytics aggregation tasks"""
        try:
            # Daily aggregations at 2 AM
            schedule.every().day.at("02:00").do(self.run_daily_aggregation)

            # Hourly trending updates
            schedule.every().hour.do(self.update_trending_scores)

            # Real-time metrics every 5 minutes
            schedule.every(5).minutes.do(self.process_realtime_metrics)

            # Weekly cleanup at Sunday 3 AM
            schedule.every().sunday.at("03:00").do(self.weekly_cleanup)

            logger.info("Analytics aggregation tasks scheduled")

        except Exception as e:
            logger.error(f"Error scheduling tasks: {str(e)}")

    def run_daily_aggregation(self) -> Dict[str, Any]:
        """Run daily analytics aggregation"""
        try:
            logger.info("Starting daily analytics aggregation")

            results = {}

            # 1. Aggregate events for yesterday
            yesterday = datetime.utcnow().date() - timedelta(days=1)
            event_aggregations = self.event_service.aggregate_events(yesterday)
            results['event_aggregations'] = len(event_aggregations)

            # 2. Update user event summaries
            user_summaries = self.event_service.update_user_event_summaries(yesterday)
            results['user_summaries'] = len(user_summaries)

            # 3. Calculate trending scores
            trending_scores = self.trending_service.calculate_trending_scores(hours=48)
            results['trending_scores'] = len(trending_scores)

            # 4. Update trending algorithms
            updated_algorithms = self.trending_service.update_trending_algorithms()
            results['updated_algorithms'] = len(updated_algorithms)

            # 5. Generate daily analytics report
            daily_report = self._generate_daily_report(yesterday)
            results['daily_report'] = daily_report

            # 6. Archive old data (older than 90 days)
            archived_count = self._archive_old_data()
            results['archived_records'] = archived_count

            self.last_run_times['daily_aggregation'] = datetime.utcnow()
            self.task_status['daily_aggregation'] = 'completed'

            logger.info(f"Daily analytics aggregation completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Error in daily aggregation: {str(e)}")
            self.task_status['daily_aggregation'] = 'failed'
            raise

    def update_trending_scores(self) -> Dict[str, Any]:
        """Update trending scores hourly"""
        try:
            logger.info("Updating trending scores")

            # Calculate trending for last 24 hours
            trending_scores = self.trending_service.calculate_trending_scores(hours=24)

            # Update algorithm performance
            self.trending_service.update_trending_algorithms()

            results = {
                'trending_posts': len(trending_scores),
                'updated_at': datetime.utcnow().isoformat()
            }

            self.last_run_times['trending_update'] = datetime.utcnow()
            self.task_status['trending_update'] = 'completed'

            logger.info(f"Trending scores updated: {results}")
            return results

        except Exception as e:
            logger.error(f"Error updating trending scores: {str(e)}")
            self.task_status['trending_update'] = 'failed'
            raise

    def process_realtime_metrics(self) -> Dict[str, Any]:
        """Process real-time metrics every 5 minutes"""
        try:
            # Get real-time metrics for last 5 minutes
            realtime_metrics = self.analytics_engine.get_realtime_metrics(timeframe_minutes=5)

            # Store in cache or database for dashboard access
            self._cache_realtime_metrics(realtime_metrics)

            results = {
                'active_users': realtime_metrics.active_users,
                'total_events': realtime_metrics.total_events,
                'engagement_rate': realtime_metrics.engagement_rate,
                'processed_at': datetime.utcnow().isoformat()
            }

            self.last_run_times['realtime_metrics'] = datetime.utcnow()
            self.task_status['realtime_metrics'] = 'completed'

            return results

        except Exception as e:
            logger.error(f"Error processing realtime metrics: {str(e)}")
            self.task_status['realtime_metrics'] = 'failed'
            raise

    def weekly_cleanup(self) -> Dict[str, Any]:
        """Weekly cleanup and maintenance tasks"""
        try:
            logger.info("Starting weekly analytics cleanup")

            results = {}

            # 1. Clean up old event aggregations (keep last 90 days)
            cleanup_date = datetime.utcnow() - timedelta(days=90)
            deleted_aggregations = self._cleanup_old_aggregations(cleanup_date)
            results['deleted_aggregations'] = deleted_aggregations

            # 2. Archive old user event summaries (keep last 180 days)
            archive_date = datetime.utcnow() - timedelta(days=180)
            archived_summaries = self._archive_old_summaries(archive_date)
            results['archived_summaries'] = archived_summaries

            # 3. Optimize trending data
            optimized_trends = self._optimize_trending_data()
            results['optimized_trends'] = optimized_trends

            # 4. Generate weekly analytics report
            weekly_report = self._generate_weekly_report()
            results['weekly_report'] = weekly_report

            # 5. Update analytics health check
            health_status = self._perform_health_check()
            results['health_check'] = health_status

            self.last_run_times['weekly_cleanup'] = datetime.utcnow()
            self.task_status['weekly_cleanup'] = 'completed'

            logger.info(f"Weekly cleanup completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Error in weekly cleanup: {str(e)}")
            self.task_status['weekly_cleanup'] = 'failed'
            raise

    def get_task_status(self) -> Dict[str, Any]:
        """Get status of all background tasks"""
        return {
            'last_run_times': self.last_run_times,
            'task_status': self.task_status,
            'next_scheduled_runs': self._get_next_scheduled_runs()
        }

    def run_manual_aggregation(self, task_type: str, date: datetime = None) -> Dict[str, Any]:
        """Run manual aggregation for specific task and date"""
        try:
            if task_type == 'daily':
                return self.run_daily_aggregation()
            elif task_type == 'trending':
                return self.update_trending_scores()
            elif task_type == 'realtime':
                return self.process_realtime_metrics()
            elif task_type == 'weekly':
                return self.weekly_cleanup()
            else:
                raise ValueError(f"Unknown task type: {task_type}")

        except Exception as e:
            logger.error(f"Error in manual aggregation: {str(e)}")
            raise

    def _generate_daily_report(self, date: datetime) -> Dict[str, Any]:
        """Generate daily analytics report"""
        try:
            # Get dashboard data for the date
            dashboard = self.analytics_engine.get_analytics_dashboard(days=1)

            report = {
                'date': date.isoformat(),
                'total_users': dashboard.total_users,
                'active_users': dashboard.active_users,
                'total_sessions': dashboard.total_sessions,
                'avg_session_duration': dashboard.avg_session_duration,
                'total_events': dashboard.total_events,
                'trending_posts_count': len(dashboard.trending_posts),
                'growth_metrics': dashboard.growth_metrics
            }

            # Store report (could be saved to database or file)
            logger.info(f"Daily report generated for {date}: {report}")
            return report

        except Exception as e:
            logger.error(f"Error generating daily report: {str(e)}")
            return {}

    def _generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly analytics report"""
        try:
            # Get dashboard data for the week
            dashboard = self.analytics_engine.get_analytics_dashboard(days=7)

            # Get trending categories
            trending_categories = self.trending_service.get_trending_categories()

            report = {
                'week_ending': datetime.utcnow().date().isoformat(),
                'total_users': dashboard.total_users,
                'active_users': dashboard.active_users,
                'total_sessions': dashboard.total_sessions,
                'avg_session_duration': dashboard.avg_session_duration,
                'total_events': dashboard.total_events,
                'trending_posts_count': len(dashboard.trending_posts),
                'trending_categories': trending_categories,
                'growth_metrics': dashboard.growth_metrics,
                'popular_events': [event.dict() for event in dashboard.popular_events]
            }

            logger.info(f"Weekly report generated: {report}")
            return report

        except Exception as e:
            logger.error(f"Error generating weekly report: {str(e)}")
            return {}

    def _archive_old_data(self) -> int:
        """Archive old analytics data"""
        try:
            # Archive events older than 90 days
            cutoff_date = datetime.utcnow() - timedelta(days=90)

            # This would typically move data to archive tables or files
            # For now, just count what would be archived
            from app.models.analytics_event import AnalyticsEvent
            old_events_count = self.db.query(func.count(AnalyticsEvent.id)).filter(
                AnalyticsEvent.timestamp < cutoff_date,
                AnalyticsEvent.processed == True
            ).scalar()

            logger.info(f"Would archive {old_events_count} old events")
            return old_events_count or 0

        except Exception as e:
            logger.error(f"Error archiving old data: {str(e)}")
            return 0

    def _cleanup_old_aggregations(self, cutoff_date: datetime) -> int:
        """Clean up old event aggregations"""
        try:
            from app.models.analytics_event import EventAggregation

            deleted_count = self.db.query(EventAggregation).filter(
                EventAggregation.date < cutoff_date.date()
            ).delete()

            self.db.commit()
            logger.info(f"Deleted {deleted_count} old event aggregations")
            return deleted_count

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cleaning up aggregations: {str(e)}")
            return 0

    def _archive_old_summaries(self, cutoff_date: datetime) -> int:
        """Archive old user event summaries"""
        try:
            from app.models.analytics_event import UserEventSummary

            # Count summaries to archive
            archive_count = self.db.query(func.count(UserEventSummary.id)).filter(
                UserEventSummary.date < cutoff_date.date()
            ).scalar()

            # In a real implementation, you might move these to archive tables
            logger.info(f"Would archive {archive_count} old user summaries")
            return archive_count or 0

        except Exception as e:
            logger.error(f"Error archiving summaries: {str(e)}")
            return 0

    def _optimize_trending_data(self) -> int:
        """Optimize trending data tables"""
        try:
            # This would run database optimization commands
            # For now, just update trend statistics
            optimized_count = self.trending_service.update_trending_algorithms()
            logger.info(f"Optimized trending data for {len(optimized_count)} algorithms")
            return len(optimized_count)

        except Exception as e:
            logger.error(f"Error optimizing trending data: {str(e)}")
            return 0

    def _perform_health_check(self) -> Dict[str, Any]:
        """Perform analytics system health check"""
        try:
            health_status = {
                'database_connection': True,
                'services_status': {},
                'data_freshness': {},
                'error_rate': 0.0,
                'checked_at': datetime.utcnow().isoformat()
            }

            # Check service availability
            try:
                self.analytics_engine.get_realtime_metrics(timeframe_minutes=1)
                health_status['services_status']['analytics_engine'] = 'healthy'
            except Exception:
                health_status['services_status']['analytics_engine'] = 'unhealthy'

            try:
                self.event_service.get_popular_events(days=1, limit=1)
                health_status['services_status']['event_service'] = 'healthy'
            except Exception:
                health_status['services_status']['event_service'] = 'unhealthy'

            try:
                self.trending_service.get_trending_posts(limit=1)
                health_status['services_status']['trending_service'] = 'healthy'
            except Exception:
                health_status['services_status']['trending_service'] = 'unhealthy'

            # Check data freshness
            try:
                recent_events = self.event_service.get_events(limit=1)
                if recent_events:
                    hours_old = (datetime.utcnow() - recent_events[0].timestamp).total_seconds() / 3600
                    health_status['data_freshness']['events'] = f"{hours_old:.1f} hours old"
                else:
                    health_status['data_freshness']['events'] = "no data"
            except Exception:
                health_status['data_freshness']['events'] = "error"

            logger.info(f"Health check completed: {health_status}")
            return health_status

        except Exception as e:
            logger.error(f"Error performing health check: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def _cache_realtime_metrics(self, metrics):
        """Cache real-time metrics for dashboard access"""
        try:
            # This would typically cache in Redis or similar
            # For now, just log the metrics
            logger.debug(f"Cached realtime metrics: {metrics.dict()}")
        except Exception as e:
            logger.error(f"Error caching realtime metrics: {str(e)}")

    def _get_next_scheduled_runs(self) -> Dict[str, str]:
        """Get next scheduled run times for tasks"""
        try:
            next_runs = {}
            for job in schedule.jobs:
                if hasattr(job, 'job_func'):
                    func_name = job.job_func.__name__ if hasattr(job.job_func, '__name__') else str(job.job_func)
                    next_runs[func_name] = job.next_run.isoformat() if job.next_run else None
            return next_runs
        except Exception as e:
            logger.error(f"Error getting next scheduled runs: {str(e)}")
            return {}

    def start_scheduler(self):
        """Start the background task scheduler"""
        try:
            logger.info("Starting analytics aggregation scheduler")

            # Schedule initial tasks
            self.schedule_daily_aggregation()

            # Run scheduler loop
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Error in scheduler: {str(e)}")
        finally:
            self.db.close()

# Global instance for easy access
analytics_tasks = AnalyticsAggregationTasks()

if __name__ == "__main__":
    # Run scheduler when script is executed directly
    analytics_tasks.start_scheduler()
