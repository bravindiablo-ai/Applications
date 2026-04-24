"""
User Engagement Service for TRENDY App
Handles tracking and managing user engagement metrics
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import logging

from app.models.user_engagement import UserEngagement, UserSession, EngagementMetrics
from app.models.user import User
from typing import Any

logger = logging.getLogger(__name__)

class UserEngagementService:
    def __init__(self, db: Session):
        self.db = db

    def track_engagement(self, engagement_data: Any) -> UserEngagement:
        """Track a user engagement event"""
        try:
            engagement = UserEngagement(
                user_id=engagement_data.user_id,
                session_id=engagement_data.session_id,
                event_type=engagement_data.event_type,
                content_type=engagement_data.content_type,
                content_id=engagement_data.content_id,
                action=engagement_data.action,
                event_metadata=engagement_data.metadata or {},
                duration=engagement_data.duration,
                device_info=engagement_data.device_info or {},
                location_info=engagement_data.location_info or {},
                referrer=engagement_data.referrer,
                user_agent=engagement_data.user_agent
            )

            self.db.add(engagement)
            self.db.commit()
            self.db.refresh(engagement)

            logger.info(f"Tracked engagement: {engagement.event_type} for user {engagement.user_id}")
            return engagement

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error tracking engagement: {str(e)}")
            raise

    def start_session(self, session_data: Any) -> UserSession:
        """Start a new user session"""
        try:
            # End any existing active sessions for this user/device
            self._end_active_sessions(session_data.user_id, session_data.device_id)

            session = UserSession(
                user_id=session_data.user_id,
                session_id=session_data.session_id,
                device_id=session_data.device_id,
                device_info=session_data.device_info or {},
                location_info=session_data.location_info or {},
                is_active=True
            )

            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)

            logger.info(f"Started session: {session.session_id} for user {session.user_id}")
            return session

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error starting session: {str(e)}")
            raise

    def end_session(self, session_id: str) -> Optional[UserSession]:
        """End a user session and calculate duration"""
        try:
            session = self.db.query(UserSession).filter(
                UserSession.session_id == session_id,
                UserSession.is_active == True
            ).first()

            if session:
                session.end_time = datetime.utcnow()
                session.duration = (session.end_time - session.start_time).total_seconds() / 60  # minutes
                session.is_active = False

                self.db.commit()
                self.db.refresh(session)

                logger.info(f"Ended session: {session.session_id}, duration: {session.duration} minutes")
                return session

            return None

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error ending session: {str(e)}")
            raise

    def update_session_metrics(self, session_id: str, page_views: int = None, events_count: int = None):
        """Update session metrics"""
        try:
            session = self.db.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()

            if session:
                if page_views is not None:
                    session.page_views = page_views
                if events_count is not None:
                    session.events_count = events_count

                self.db.commit()
                logger.info(f"Updated session metrics: {session_id}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating session metrics: {str(e)}")
            raise

    def get_user_engagement_metrics(self, user_id: int, days: int = 30) -> Any:
        """Get aggregated engagement metrics for a user"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Get engagement counts
            engagements = self.db.query(
                UserEngagement.event_type,
                func.count(UserEngagement.id).label('count')
            ).filter(
                UserEngagement.user_id == user_id,
                UserEngagement.created_at >= start_date
            ).group_by(UserEngagement.event_type).all()

            # Get session data
            sessions = self.db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.start_time >= start_date
            ).all()

            total_sessions = len(sessions)
            total_session_duration = sum(s.duration or 0 for s in sessions)
            avg_session_duration = total_session_duration / total_sessions if total_sessions > 0 else 0

            # Calculate engagement score (simplified)
            engagement_score = self._calculate_engagement_score(engagements, total_sessions, avg_session_duration)

            return MetricsResponse(
                user_id=user_id,
                total_views=sum(e.count for e in engagements if e.event_type == 'view'),
                total_likes=sum(e.count for e in engagements if e.event_type == 'like'),
                total_comments=sum(e.count for e in engagements if e.event_type == 'comment'),
                total_shares=sum(e.count for e in engagements if e.event_type == 'share'),
                total_follows=sum(e.count for e in engagements if e.event_type == 'follow'),
                total_unfollows=sum(e.count for e in engagements if e.event_type == 'unfollow'),
                avg_session_duration=avg_session_duration,
                total_sessions=total_sessions,
                engagement_score=engagement_score
            )

        except Exception as e:
            logger.error(f"Error getting user engagement metrics: {str(e)}")
            raise

    def get_top_engaged_users(self, limit: int = 10, days: int = 7) -> List[Dict[str, Any]]:
        """Get users with highest engagement scores"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Get users with most engagements
            top_users = self.db.query(
                UserEngagement.user_id,
                User.username,
                func.count(UserEngagement.id).label('engagement_count')
            ).join(User).filter(
                UserEngagement.created_at >= start_date
            ).group_by(UserEngagement.user_id, User.username
            ).order_by(desc('engagement_count')
            ).limit(limit).all()

            return [
                {
                    'user_id': u.user_id,
                    'username': u.username,
                    'engagement_count': u.engagement_count
                }
                for u in top_users
            ]

        except Exception as e:
            logger.error(f"Error getting top engaged users: {str(e)}")
            raise

    def get_engagement_trends(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily engagement trends for a user"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            trends = self.db.query(
                func.date(UserEngagement.created_at).label('date'),
                UserEngagement.event_type,
                func.count(UserEngagement.id).label('count')
            ).filter(
                UserEngagement.user_id == user_id,
                UserEngagement.created_at >= start_date
            ).group_by(
                func.date(UserEngagement.created_at),
                UserEngagement.event_type
            ).order_by('date').all()

            # Group by date
            daily_trends = {}
            for trend in trends:
                date_str = trend.date.isoformat()
                if date_str not in daily_trends:
                    daily_trends[date_str] = {'date': date_str}
                daily_trends[date_str][trend.event_type] = trend.count

            return list(daily_trends.values())

        except Exception as e:
            logger.error(f"Error getting engagement trends: {str(e)}")
            raise

    def _end_active_sessions(self, user_id: int, device_id: str):
        """End any active sessions for the user/device"""
        try:
            active_sessions = self.db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.device_id == device_id,
                UserSession.is_active == True
            ).all()

            for session in active_sessions:
                session.end_time = datetime.utcnow()
                session.duration = (session.end_time - session.start_time).total_seconds() / 60
                session.is_active = False

            if active_sessions:
                self.db.commit()

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error ending active sessions: {str(e)}")

    def _calculate_engagement_score(self, engagements: List, total_sessions: int, avg_session_duration: float) -> float:
        """Calculate a simplified engagement score"""
        # Simple scoring: views (1), likes/comments/shares (2), follows (3)
        score = 0
        for engagement in engagements:
            if engagement.event_type in ['view']:
                score += engagement.count * 1
            elif engagement.event_type in ['like', 'comment', 'share']:
                score += engagement.count * 2
            elif engagement.event_type in ['follow']:
                score += engagement.count * 3

        # Add session factors
        score += total_sessions * 5
        score += avg_session_duration * 0.1

        return round(score, 2)
