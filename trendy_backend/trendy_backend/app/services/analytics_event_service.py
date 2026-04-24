"""
Analytics Event Service for TRENDY App
Handles event logging, aggregation, and analytics processing
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text
import logging
import json
from app.models.analytics_event import AnalyticsEvent, EventAggregation, UserEventSummary
from typing import Any

logger = logging.getLogger(__name__)

class AnalyticsEventService:
    def __init__(self, db: Session):
        self.db = db

    def log_event(self, event_data: Any) -> AnalyticsEvent:
        """Log an analytics event"""
        try:
            event = AnalyticsEvent(
                user_id=event_data.user_id,
                session_id=event_data.session_id,
                event_type=event_data.event_type,
                event_category=event_data.event_category,
                event_action=event_data.event_action,
                event_label=event_data.event_label,
                event_value=event_data.event_value,
                page_url=event_data.page_url,
                referrer=event_data.referrer,
                user_agent=event_data.user_agent,
                device_info=event_data.device_info or {},
                location_info=event_data.location_info or {},
                custom_parameters=event_data.custom_parameters or {}
            )
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            logger.info(f"Logged event: {event.event_type} - {event.event_action}")
            return event
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging event: {str(e)}")
            raise

    def get_events(self, query: Any) -> List[AnalyticsEvent]:
        """Query analytics events with filters"""
        try:
            q = self.db.query(AnalyticsEvent)
            if query.user_id:
                q = q.filter(AnalyticsEvent.user_id == query.user_id)
            if query.event_type:
                q = q.filter(AnalyticsEvent.event_type == query.event_type)
            if query.event_category:
                q = q.filter(AnalyticsEvent.event_category == query.event_category)
            if query.session_id:
                q = q.filter(AnalyticsEvent.session_id == query.session_id)
            if query.start_date:
                q = q.filter(AnalyticsEvent.timestamp >= query.start_date)
            if query.end_date:
                q = q.filter(AnalyticsEvent.timestamp <= query.end_date)
            q = q.order_by(desc(AnalyticsEvent.timestamp))
            if query.limit:
                q = q.limit(query.limit)
            return q.all()
        except Exception as e:
            logger.error(f"Error querying events: {str(e)}")
            raise

    def aggregate_events(self, date: datetime = None, event_type: str = None) -> List[EventAggregation]:
        """Aggregate events for a specific date or all unprocessed events"""
        try:
            if date is None:
                date = datetime.utcnow().date()
            # Get events to aggregate
            query = self.db.query(AnalyticsEvent).filter(
                func.date(AnalyticsEvent.timestamp) == date,
                AnalyticsEvent.processed == False
            )
            if event_type:
                query = query.filter(AnalyticsEvent.event_type == event_type)
            events = query.all()
            if not events:
                return []
            # Group events by type and category
            aggregations = {}
            for event in events:
                key = (event.event_type, event.event_category)
                if key not in aggregations:
                    aggregations[key] = {
                        'event_type': event.event_type,
                        'event_category': event.event_category,
                        'total_events': 0,
                        'unique_users': set(),
                        'total_value': 0.0,
                        'values': []
                    }
                agg = aggregations[key]
                agg['total_events'] += 1
                if event.user_id:
                    agg['unique_users'].add(event.user_id)
                if event.event_value is not None:
                    agg['total_value'] += event.event_value
                    agg['values'].append(event.event_value)
            # Create aggregation records
            results = []
            for key, data in aggregations.items():
                values = data['values']
                avg_value = sum(values) / len(values) if values else 0.0
                aggregation = EventAggregation(
                    event_type=data['event_type'],
                    event_category=data['event_category'],
                    date=date,
                    total_events=data['total_events'],
                    unique_users=len(data['unique_users']),
                    total_value=data['total_value'],
                    avg_value=avg_value
                )
                self.db.add(aggregation)
                results.append(aggregation)
            # Mark events as processed
            for event in events:
                event.processed = True
            self.db.commit()
            logger.info(f"Aggregated {len(events)} events into {len(results)} records")
            return results
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error aggregating events: {str(e)}")
            raise

    def get_event_aggregations(self, start_date: datetime, end_date: datetime,
                              event_type: str = None) -> List[Any]:
        """Get aggregated event data for a date range"""
        try:
            query = self.db.query(EventAggregation).filter(
                EventAggregation.date >= start_date.date(),
                EventAggregation.date <= end_date.date()
            )
            if event_type:
                query = query.filter(EventAggregation.event_type == event_type)
            aggregations = query.order_by(EventAggregation.date).all()
            return [
                AggregationResponse(
                    event_type=agg.event_type,
                    event_category=agg.event_category,
                    date=agg.date,
                    total_events=agg.total_events,
                    unique_users=agg.unique_users,
                    total_value=agg.total_value,
                    avg_value=agg.avg_value
                )
                for agg in aggregations
            ]
        except Exception as e:
            logger.error(f"Error getting event aggregations: {str(e)}")
            raise

    def update_user_event_summaries(self, date: datetime = None) -> List[UserEventSummary]:
        """Update user event summaries for a specific date"""
        try:
            if date is None:
                date = datetime.utcnow().date()
            # Get all users who had events on this date
            users_with_events = self.db.query(AnalyticsEvent.user_id).filter(
                func.date(AnalyticsEvent.timestamp) == date,
                AnalyticsEvent.user_id.isnot(None)
            ).distinct().all()
            summaries = []
            for (user_id,) in users_with_events:
                summary = self._calculate_user_summary(user_id, date)
                if summary:
                    summaries.append(summary)
            logger.info(f"Updated {len(summaries)} user event summaries for {date}")
            return summaries
        except Exception as e:
            logger.error(f"Error updating user event summaries: {str(e)}")
            raise

    def get_user_event_summary(self, user_id: int, date: datetime) -> Optional[UserEventSummary]:
        """Get event summary for a specific user and date"""
        try:
            return self.db.query(UserEventSummary).filter(
                UserEventSummary.user_id == user_id,
                UserEventSummary.date == date.date()
            ).first()
        except Exception as e:
            logger.error(f"Error getting user event summary: {str(e)}")
            raise

    def get_popular_events(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular event types in the last N days"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            popular_events = self.db.query(
                AnalyticsEvent.event_type,
                AnalyticsEvent.event_category,
                func.count(AnalyticsEvent.id).label('count'),
                func.count(func.distinct(AnalyticsEvent.user_id)).label('unique_users')
            ).filter(
                AnalyticsEvent.timestamp >= start_date
            ).group_by(
                AnalyticsEvent.event_type,
                AnalyticsEvent.event_category
            ).order_by(desc('count')
            ).limit(limit).all()
            return [
                {
                    'event_type': e.event_type,
                    'event_category': e.event_category,
                    'count': e.count,
                    'unique_users': e.unique_users
                }
                for e in popular_events
            ]
        except Exception as e:
            logger.error(f"Error getting popular events: {str(e)}")
            raise

    def get_event_trends(self, event_type: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily trends for a specific event type"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            trends = self.db.query(
                func.date(AnalyticsEvent.timestamp).label('date'),
                func.count(AnalyticsEvent.id).label('count'),
                func.count(func.distinct(AnalyticsEvent.user_id)).label('unique_users'),
                func.avg(AnalyticsEvent.event_value).label('avg_value')
            ).filter(
                AnalyticsEvent.event_type == event_type,
                AnalyticsEvent.timestamp >= start_date
            ).group_by(func.date(AnalyticsEvent.timestamp)
            ).order_by('date').all()
            return [
                {
                    'date': t.date.isoformat(),
                    'count': t.count,
                    'unique_users': t.unique_users,
                    'avg_value': float(t.avg_value) if t.avg_value else 0.0
                }
                for t in trends
            ]
        except Exception as e:
            logger.error(f"Error getting event trends: {str(e)}")
            raise

    def _calculate_user_summary(self, user_id: int, date: datetime) -> Optional[UserEventSummary]:
        """Calculate event summary for a user on a specific date"""
        try:
            # Get user's events for the date
            events = self.db.query(AnalyticsEvent).filter(
                AnalyticsEvent.user_id == user_id,
                func.date(AnalyticsEvent.timestamp) == date
            ).all()
            if not events:
                return None
            # Count events by type
            event_counts = {}
            total_events = len(events)
            total_value = 0.0
            for event in events:
                event_type = event.event_type
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                if event.event_value:
                    total_value += event.event_value
            # Get session count (simplified - count unique sessions)
            session_count = len(set(e.session_id for e in events))
            # Calculate engagement score (simplified)
            engagement_score = self._calculate_engagement_score(event_counts, session_count)
            # Find most active hour
            hours = [e.timestamp.hour for e in events]
            most_active_hour = max(set(hours), key=hours.count) if hours else None
            # Find top event type
            top_event_type = max(event_counts.keys(), key=lambda k: event_counts[k]) if event_counts else None
            summary = UserEventSummary(
                user_id=user_id,
                date=date,
                total_events=total_events,
                event_types=event_counts,
                session_count=session_count,
                most_active_hour=most_active_hour,
                top_event_type=top_event_type,
                engagement_score=engagement_score
            )
            # Check if summary exists, update or create
            existing = self.db.query(UserEventSummary).filter(
                UserEventSummary.user_id == user_id,
                UserEventSummary.date == date
            ).first()
            if existing:
                # Update existing
                for key, value in summary.__dict__.items():
                    if key != 'id' and key != 'created_at':
                        setattr(existing, key, value)
                self.db.commit()
                return existing
            else:
                # Create new
                self.db.add(summary)
                self.db.commit()
                self.db.refresh(summary)
                return summary
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error calculating user summary: {str(e)}")
            return None

    def _calculate_engagement_score(self, event_counts: Dict[str, int], session_count: int) -> float:
        """Calculate engagement score based on event types and sessions"""
        score = 0
        # Weight different event types
        weights = {
            'page_view': 1,
            'button_click': 2,
            'api_call': 1,
            'content_view': 3,
            'content_like': 4,
            'content_comment': 5,
            'content_share': 6,
            'user_follow': 7,
            'user_unfollow': -2
        }
        for event_type, count in event_counts.items():
            weight = weights.get(event_type, 1)
            score += count * weight
        # Add session bonus
        score += session_count * 10
        return round(score, 2)

    # ----- Compatibility helpers used by TrendService -----
    def get_content_metrics(self, content_id: str, since: datetime) -> Dict[str, int]:
        """
        Aggregate basic engagement metrics for content since the given time.
        Maps event_label to content_id in the AnalyticsEvent model.
        Returns dict: {'views', 'likes', 'shares', 'comments'}
        """
        try:
            q = self.db.query(AnalyticsEvent).filter(
                AnalyticsEvent.event_label == content_id,
                AnalyticsEvent.timestamp >= since
            )
            views = q.filter(AnalyticsEvent.event_action == "content_view").count()
            likes = q.filter(AnalyticsEvent.event_action == "content_like").count()
            shares = q.filter(AnalyticsEvent.event_action == "content_share").count()
            comments = q.filter(AnalyticsEvent.event_action == "content_comment").count()
            return {"views": views, "likes": likes, "shares": shares, "comments": comments}
        except Exception:
            return {"views": 0, "likes": 0, "shares": 0, "comments": 0}

    def get_category_metrics(self, category: str, hours: int = 24) -> Dict[str, int]:
        """
        Summarize engagement by category.
        """
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        q = self.db.query(AnalyticsEvent).filter(
            AnalyticsEvent.event_category == category,
            AnalyticsEvent.timestamp >= since
        )
        total = q.count()
        total_items = len({a.event_label for a in q})
        return {"total_engagement": total, "total_items": total_items}

    def get_top_content_candidates(self, limit: int = 100) -> List[Dict[str, str]]:
        """
        Return candidate content with highest recent engagement.
        """
        since = datetime.now(timezone.utc) - timedelta(hours=3)
        q = self.db.query(AnalyticsEvent.event_label, AnalyticsEvent.event_category).filter(
            AnalyticsEvent.timestamp >= since
        ).distinct()
        results = [{"content_id": c[0], "category": c[1]} for c in q.limit(limit)]
        return results

    def get_random_content(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Return sample content for exploration (random selection).
        """
        # SQLite random ordering uses RANDOM()
        q = self.db.query(AnalyticsEvent.event_label, AnalyticsEvent.event_category).distinct().order_by(text('RANDOM()')).limit(limit)
        return [{"content_id": c[0], "category": c[1]} for c in q]

    def get_content_creator(self, content_id: str) -> str:
        """
        Stub: Return content creator_id (to reward viral creators).
        Replace this with real content table join later.
        """
        # Try to import Content model lazily; return None if not available
        try:
            from app.models.content import Content
        except Exception:
            return None
        try:
            content = self.db.query(Content).filter(Content.id == content_id).first()
            if content and hasattr(content, "creator_id"):
                return content.creator_id
        except Exception:
            return None
        return None
