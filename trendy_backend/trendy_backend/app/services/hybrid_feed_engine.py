"""
Hybrid feed engine that combines personalization, trending content, and rewards.
"""
from typing import List, Dict, Any
from app.services.personalization_service import PersonalizationService
from app.services.trend_service import TrendService
from app.services.rewards_service import RewardService
from app.services.analytics_event_service import AnalyticsEventService
from app.services.cache_service import CacheService
from app.services.moderation_service import ModerationService

class HybridFeedEngine:
    """Engine that combines multiple content sources into optimized feeds."""

    def __init__(self):
        """Initialize the hybrid feed engine."""
        self.personalization = PersonalizationService()
        self.trends = TrendService()
        self.rewards = RewardService()
        self.analytics = AnalyticsEventService()
        self.cache = CacheService()
        self.moderation = ModerationService()

    async def get_discover_feed(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get a discovery feed that balances trending, personalized,
        and promotional content.
        """
        # Try cache first
        cache_key = f"discover:{user_id}:{page}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Fetch content from different sources
        trending = await self.trends.get_trending_items(limit=page_size)
        personalized = await self.personalization.get_personalized_feed(
            user_id,
            page=page,
            page_size=page_size
        )
        rewarded = await self.rewards.get_promoted_content(limit=page_size//4)

        # Combine and score content
        all_content = []
        
        # Add trending content (40% weight)
        for item in trending:
            item["source"] = "trending"
            item["final_score"] = item.get("trend_score", 0) * 0.4
            all_content.append(item)

        # Add personalized content (40% weight)
        for item in personalized:
            if item["id"] not in [c["id"] for c in all_content]:
                item["source"] = "personalized"
                item["final_score"] = item.get("personalization_score", 0) * 0.4
                all_content.append(item)

        # Add rewarded content (20% weight)
        for item in rewarded:
            if item["id"] not in [c["id"] for c in all_content]:
                item["source"] = "rewarded"
                item["final_score"] = item.get("promotion_score", 0) * 0.2
                all_content.append(item)

        # Sort by final score and paginate
        all_content.sort(key=lambda x: x["final_score"], reverse=True)
        start = (page - 1) * page_size
        result = all_content[start:start + page_size]

        # Add metadata and enrich content
        enriched = await self._enrich_feed_items(result, user_id)

        # Cache the results
        await self.cache.set(cache_key, enriched, expire=300)  # 5 minutes

        return enriched

    async def get_personalized_feed(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get a purely personalized feed based on user preferences
        and behavior.
        """
        items = await self.personalization.get_personalized_feed(
            user_id,
            page=page,
            page_size=page_size
        )
        return await self._enrich_feed_items(items, user_id)

    async def get_trending_feed(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """Get a feed of trending content."""
        items = await self.trends.get_trending_items(
            offset=(page-1) * page_size,
            limit=page_size
        )
        return await self._enrich_feed_items(items, user_id)

    async def _enrich_feed_items(
        self,
        items: List[Dict[str, Any]],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Add additional metadata to feed items."""
        enriched = []
        
        for item in items:
            # Get creator info
            creator_info = await self.analytics.get_creator_stats(
                item.get("creator_id")
            )
            
            # Get engagement metrics
            engagement = await self.analytics.get_content_engagement(
                item["id"]
            )
            
            # Check user interaction
            user_interaction = await self.analytics.get_user_content_interaction(
                user_id,
                item["id"]
            )

            # Add AI-generated tags
            # TODO: Implement AI tagging

            enriched.append({
                **item,
                "creator": creator_info,
                "engagement": engagement,
                "user_interaction": user_interaction
            })

        return enriched