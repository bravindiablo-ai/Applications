"""
Trending Service for TRENDY App
Calculates trending scores and manages trending algorithms
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text
import logging
import math

from app.models.trends import Trend
from app.models.enhanced_post import TrendingAlgorithm
from app.models.post import Post
from app.models.enhanced_post import PostAnalytics
from typing import Any

logger = logging.getLogger(__name__)

class TrendingService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_trending_scores(self, algorithm_id: int = None, hours: int = 24) -> List[Trend]:
        """Calculate trending scores for posts using specified algorithm"""
        try:
            # Get active algorithm or default
            if algorithm_id:
                algorithm = self.db.query(TrendingAlgorithm).filter(
                    TrendingAlgorithm.id == algorithm_id,
                    TrendingAlgorithm.is_active == True
                ).first()
            else:
                algorithm = self.db.query(TrendingAlgorithm).filter(
                    TrendingAlgorithm.is_active == True
                ).first()

            if not algorithm:
                logger.warning("No active trending algorithm found")
                return []

            # Get posts from the last N hours
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            posts = self.db.query(Post).filter(
                Post.created_at >= cutoff_time
            ).all()

            trends = []
            for post in posts:
                score = self._calculate_post_score(post, algorithm, hours)
                if score >= algorithm.minimum_threshold:
                    trend = Trend(
                        post_id=post.id,
                        algorithm_id=algorithm.id,
                        trending_score=score,
                        rank=0,  # Will be set after sorting
                        is_trending=True,
                        trending_factors=self._get_trending_factors(post, algorithm, hours)
                    )
                    trends.append(trend)

            # Sort by score and assign ranks
            trends.sort(key=lambda x: x.trending_score, reverse=True)
            for i, trend in enumerate(trends):
                trend.rank = i + 1

            # Save trends to database
            self._save_trends(trends)

            logger.info(f"Calculated trending scores for {len(trends)} posts")
            return trends

        except Exception as e:
            logger.error(f"Error calculating trending scores: {str(e)}")
            raise

    def get_trending_posts(self, limit: int = 20, category: str = None) -> List[Any]:
        """Get currently trending posts"""
        try:
            query = self.db.query(Trend, Post).join(Post).filter(
                Trend.is_trending == True
            ).order_by(Trend.rank)

            if category:
                query = query.filter(Post.category == category)

            results = query.limit(limit).all()

            trending_posts = []
            for trend, post in results:
                trending_posts.append(TrendingPost(
                    post_id=post.id,
                    title=post.title,
                    content=post.content[:200] + "..." if len(post.content) > 200 else post.content,
                    author_id=post.user_id,
                    trending_score=trend.trending_score,
                    rank=trend.rank,
                    trending_factors=trend.trending_factors,
                    created_at=post.created_at,
                    updated_at=post.updated_at
                ))

            return trending_posts

        except Exception as e:
            logger.error(f"Error getting trending posts: {str(e)}")
            raise

    def update_trending_algorithms(self) -> List[TrendingAlgorithm]:
        """Update trending algorithms with fresh data"""
        try:
            algorithms = self.db.query(TrendingAlgorithm).filter(
                TrendingAlgorithm.is_active == True
            ).all()

            for algorithm in algorithms:
                # Update algorithm statistics
                recent_trends = self.db.query(Trend).filter(
                    Trend.algorithm_id == algorithm.id,
                    Trend.created_at >= datetime.utcnow() - timedelta(days=1)
                ).all()

                if recent_trends:
                    avg_score = sum(t.trending_score for t in recent_trends) / len(recent_trends)
                    algorithm.average_score = avg_score
                    algorithm.last_updated = datetime.utcnow()

            self.db.commit()
            logger.info(f"Updated {len(algorithms)} trending algorithms")
            return algorithms

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating trending algorithms: {str(e)}")
            raise

    def get_trending_categories(self) -> List[Dict[str, Any]]:
        """Get trending categories and their scores"""
        try:
            # Get trending posts grouped by category
            category_trends = self.db.query(
                Post.category,
                func.count(Trend.id).label('post_count'),
                func.avg(Trend.trending_score).label('avg_score'),
                func.max(Trend.trending_score).label('max_score')
            ).join(Post).filter(
                Trend.is_trending == True
            ).group_by(Post.category
            ).order_by(desc('avg_score')).all()

            return [
                {
                    'category': ct.category,
                    'post_count': ct.post_count,
                    'avg_score': float(ct.avg_score),
                    'max_score': float(ct.max_score)
                }
                for ct in category_trends
            ]

        except Exception as e:
            logger.error(f"Error getting trending categories: {str(e)}")
            raise

    def get_trending_history(self, post_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get trending history for a specific post"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            history = self.db.query(Trend).filter(
                Trend.post_id == post_id,
                Trend.created_at >= start_date
            ).order_by(Trend.created_at).all()

            return [
                {
                    'date': t.created_at.date().isoformat(),
                    'score': t.trending_score,
                    'rank': t.rank,
                    'is_trending': t.is_trending
                }
                for t in history
            ]

        except Exception as e:
            logger.error(f"Error getting trending history: {str(e)}")
            raise

    def create_custom_algorithm(self, config: Any) -> TrendingAlgorithm:
        """Create a custom trending algorithm"""
        try:
            algorithm = TrendingAlgorithm(
                name=config.name,
                description=config.description,
                algorithm_config=config.algorithm_config,
                is_active=config.is_active,
                weight_likes=config.weight_likes,
                weight_comments=config.weight_comments,
                weight_shares=config.weight_shares,
                weight_views=config.weight_views,
                weight_recency=config.weight_recency,
                weight_engagement_rate=config.weight_engagement_rate,
                weight_velocity=config.weight_velocity,
                weight_freshness=config.weight_freshness,
                weight_virality=config.weight_virality,
                decay_factor=config.decay_factor,
                minimum_threshold=config.minimum_threshold,
                time_window_hours=config.time_window_hours
            )

            self.db.add(algorithm)
            self.db.commit()
            self.db.refresh(algorithm)

            logger.info(f"Created custom trending algorithm: {algorithm.name}")
            return algorithm

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating custom algorithm: {str(e)}")
            raise

    def _calculate_post_score(self, post: Post, algorithm: TrendingAlgorithm, hours: int) -> float:
        """Calculate trending score for a single post"""
        try:
            # Get post analytics
            analytics = self.db.query(PostAnalytics).filter(
                PostAnalytics.post_id == post.id,
                PostAnalytics.date >= datetime.utcnow() - timedelta(hours=hours)
            ).all()

            if not analytics:
                return 0.0

            # Aggregate metrics
            total_views = sum(a.views for a in analytics)
            total_likes = sum(a.likes for a in analytics)
            total_comments = sum(a.comments for a in analytics)
            total_shares = sum(a.shares for a in analytics)
            total_saves = sum(a.saves for a in analytics)
            avg_engagement_rate = sum(a.engagement_rate for a in analytics) / len(analytics) if analytics else 0

            # Calculate recency factor (newer posts get higher scores)
            hours_old = (datetime.utcnow() - post.created_at).total_seconds() / 3600
            recency_factor = max(0, 1 - (hours_old / algorithm.time_window_hours))

            # Calculate velocity (recent activity vs older activity)
            recent_analytics = [a for a in analytics if a.date >= datetime.utcnow() - timedelta(hours=hours/2)]
            older_analytics = [a for a in analytics if a.date < datetime.utcnow() - timedelta(hours=hours/2)]

            recent_activity = sum(a.likes + a.comments + a.shares for a in recent_analytics)
            older_activity = sum(a.likes + a.comments + a.shares for a in older_analytics)

            velocity_factor = 1.0
            if older_activity > 0:
                velocity_factor = recent_activity / older_activity
                velocity_factor = min(velocity_factor, 3.0)  # Cap at 3x

            # Calculate freshness (posts that are still getting engagement)
            latest_analytics = max(analytics, key=lambda x: x.date) if analytics else None
            freshness_factor = 1.0
            if latest_analytics:
                hours_since_last_activity = (datetime.utcnow() - latest_analytics.date).total_seconds() / 3600
                freshness_factor = max(0, 1 - (hours_since_last_activity / 24))  # Decay over 24 hours

            # Calculate virality (shares relative to views)
            virality_factor = 0.0
            if total_views > 0:
                virality_factor = (total_shares / total_views) * 100  # Percentage

            # Apply algorithm weights
            score = (
                algorithm.weight_likes * total_likes +
                algorithm.weight_comments * total_comments +
                algorithm.weight_shares * total_shares +
                algorithm.weight_views * total_views +
                algorithm.weight_recency * recency_factor * 100 +
                algorithm.weight_engagement_rate * avg_engagement_rate +
                algorithm.weight_velocity * velocity_factor * 50 +
                algorithm.weight_freshness * freshness_factor * 100 +
                algorithm.weight_virality * virality_factor
            )

            # Apply decay factor based on age
            age_days = (datetime.utcnow() - post.created_at).days
            decay = math.pow(algorithm.decay_factor, age_days)
            score *= decay

            return round(score, 2)

        except Exception as e:
            logger.error(f"Error calculating post score: {str(e)}")
            return 0.0

    def _get_trending_factors(self, post: Post, algorithm: TrendingAlgorithm, hours: int) -> Dict[str, Any]:
        """Get the factors that contributed to the trending score"""
        try:
            analytics = self.db.query(PostAnalytics).filter(
                PostAnalytics.post_id == post.id,
                PostAnalytics.date >= datetime.utcnow() - timedelta(hours=hours)
            ).all()

            if not analytics:
                return {}

            total_views = sum(a.views for a in analytics)
            total_likes = sum(a.likes for a in analytics)
            total_comments = sum(a.comments for a in analytics)
            total_shares = sum(a.shares for a in analytics)

            hours_old = (datetime.utcnow() - post.created_at).total_seconds() / 3600
            recency_factor = max(0, 1 - (hours_old / algorithm.time_window_hours))

            return {
                'total_views': total_views,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_shares': total_shares,
                'hours_old': round(hours_old, 1),
                'recency_factor': round(recency_factor, 3),
                'analytics_count': len(analytics)
            }

        except Exception as e:
            logger.error(f"Error getting trending factors: {str(e)}")
            return {}

    def _save_trends(self, trends: List[Trend]):
        """Save trends to database, updating existing ones"""
        try:
            for trend in trends:
                # Check if trend already exists for this post and algorithm
                existing = self.db.query(Trend).filter(
                    Trend.post_id == trend.post_id,
                    Trend.algorithm_id == trend.algorithm_id,
                    func.date(Trend.created_at) == datetime.utcnow().date()
                ).first()

                if existing:
                    # Update existing trend
                    existing.trending_score = trend.trending_score
                    existing.rank = trend.rank
                    existing.is_trending = trend.is_trending
                    existing.trending_factors = trend.trending_factors
                    existing.updated_at = datetime.utcnow()
                else:
                    # Add new trend
                    self.db.add(trend)

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving trends: {str(e)}")
            raise
