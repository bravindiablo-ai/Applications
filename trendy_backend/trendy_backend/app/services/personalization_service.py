"""
PersonalizationService: Provides user-specific content recommendations.
Used by TrendService to blend personalized results with trending.
"""
from typing import List, Dict, Any, Union
from sqlalchemy.orm import Session
from app.models.user_preferences import UserPreference, UserHistory
from app.models.post import Post, Like
from sqlalchemy import func, desc
from collections import Counter
from datetime import datetime, timedelta

class PersonalizationService:
    def __init__(self, db: Session):
        self.db = db

    def recommend_for_user(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Hybrid recommender logic using collaborative filtering and content-based filtering.
        """
        # Get user's interaction history
        liked_posts = self.db.query(Like).filter_by(user_id=user_id).all()
        preferences = self.db.query(UserPreference).filter_by(user_id=user_id).all()
        history = self.db.query(UserHistory).filter_by(user_id=user_id, history_type="post_view").filter(UserHistory.created_at >= datetime.utcnow() - timedelta(days=30)).all()
        
        # Extract user interests
        user_hashtags = []
        for like in liked_posts:
            if like.post and like.post.hashtags:
                user_hashtags.extend(like.post.hashtags)
        # Collect categories from preferences (assuming preference_type="content_category")
        for pref in preferences:
            if pref.preference_type == "content_category":
                user_hashtags.append(pref.preference_key)
        
        hashtag_counts = Counter(user_hashtags)
        top_interests = [tag for tag, count in hashtag_counts.most_common(5)]
        
        # Find similar content
        seen_content_ids = {h.content_id for h in history if h.content_type == "post"}
        if top_interests:
            similar_posts = self.db.query(Post).filter(Post.hashtags.contains(top_interests)).filter(Post.user_id != user_id).order_by(desc(Post.likes_count)).limit(limit * 2).all()
            similar_posts = [p for p in similar_posts if str(p.id) not in seen_content_ids]
        else:
            similar_posts = []
        
        # Collaborative filtering
        if liked_posts:
            similar_users = self.db.query(Like.user_id).filter(Like.post_id.in_([p.id for p in liked_posts])).filter(Like.user_id != user_id).group_by(Like.user_id).having(func.count(Like.id) >= 3).all()
            similar_user_ids = [u[0] for u in similar_users]
            collaborative_posts = self.db.query(Post).join(Like).filter(Like.user_id.in_(similar_user_ids)).filter(Post.user_id != user_id).order_by(desc(Post.created_at)).limit(limit).all()
        else:
            collaborative_posts = []
        
        # Combine and score
        all_posts = list(set(similar_posts + collaborative_posts))
        scored_posts = []
        for post in all_posts:
            hashtag_score = len(set(post.hashtags or []) & set(top_interests)) / max(len(top_interests), 1) if top_interests else 0
            recency_score = 1 / (1 + (datetime.utcnow() - post.created_at).days)
            engagement_score = min(post.likes_count / 100, 1)
            score = 0.4 * hashtag_score + 0.3 * recency_score + 0.3 * engagement_score
            scored_posts.append((post, score))
        
        scored_posts.sort(key=lambda x: x[1], reverse=True)
        
        # Fallback for new users
        if not liked_posts and not preferences and not history:
            trending = self._get_trending_fallback(limit)
            return [{"content_id": str(p.id), "score": 0.5, "category": p.hashtags[0] if p.hashtags else "general", "post": p} for p in trending]
        
        return [{"content_id": str(post.id), "score": score, "category": post.hashtags[0] if post.hashtags else "general", "post": post} for post, score in scored_posts[:limit]]

    def _calculate_content_similarity(self, post1: Post, post2: Post) -> float:
        """Calculate Jaccard similarity of hashtags."""
        h1 = set(post1.hashtags or [])
        h2 = set(post2.hashtags or [])
        if not h1 and not h2:
            return 0.0
        return len(h1 & h2) / len(h1 | h2)

    def _get_trending_fallback(self, limit: int) -> List[Post]:
        """Return trending content for cold start."""
        return self.db.query(Post).filter(Post.created_at >= datetime.utcnow() - timedelta(days=7)).order_by(desc(Post.likes_count)).limit(limit).all()