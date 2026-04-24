"""
AI-powered content moderation service using OpenAI's moderation API.
Works with or without OpenAI API key - uses rule-based fallback when OpenAI is not configured.
"""
import logging
import openai
import re
from enum import Enum
from typing import Dict, List, Optional, Tuple
from app.core.config import get_settings
from app.models.content import ContentType
from app.database import SessionLocal
from app.models.moderation import ContentFlag
from datetime import datetime

logger = logging.getLogger(__name__)

class ModerationType(str, Enum):
    """Types of content that can be moderated."""
    NUDITY = "nudity"
    VIOLENCE = "violence"
    HATE = "hate"
    SELF_HARM = "self-harm"
    SEXUAL = "sexual"
    HARASSMENT = "harassment"
    SPAM = "spam"

class ModerationService:
    """
    Service for AI-powered content moderation.
    
    This service uses OpenAI's moderation API when available, but falls back to rule-based
    moderation if the OpenAI API key is not configured. The fallback provides conservative
    moderation scores for content safety.
    """

    # Keyword lists for rule-based moderation
    PROFANITY_WORDS = [
        "fuck", "shit", "damn", "bitch", "asshole", "bastard", "cunt", "dick", "pussy",
        "nigger", "faggot", "chink", "spic", "kike", "wetback", "coon", "porch monkey",
        "sand n*****", "towelhead", "beaner", "gook", "slant-eye", "jap", "kraut"
    ]
    
    POSITIVE_WORDS = ["good", "great", "awesome", "excellent", "amazing", "love", "happy", "joy", "wonderful", "fantastic"]
    NEGATIVE_WORDS = ["bad", "terrible", "awful", "hate", "angry", "sad", "horrible", "disgusting", "stupid", "idiot"]

    def __init__(self):
        """Initialize the moderation service."""
        self.settings = get_settings()
        self.use_openai = bool(self.settings.openai_api_key and self.settings.openai_api_key.strip())
        if self.use_openai:
            openai.api_key = self.settings.openai_api_key
        else:
            logger.warning("OpenAI API key not configured. Using rule-based moderation fallback.")
        
        self.auto_ban_thresholds = {
            ModerationType.NUDITY: 0.9,
            ModerationType.VIOLENCE: 0.9,
            ModerationType.HATE: 0.8,
            ModerationType.SELF_HARM: 0.9,
            ModerationType.SEXUAL: 0.9,
            ModerationType.HARASSMENT: 0.8,
            ModerationType.SPAM: 0.95,
        }

    @classmethod
    def create_with_fallback(cls) -> 'ModerationService':
        """Create a ModerationService instance and log OpenAI availability."""
        instance = cls()
        if instance.use_openai:
            logger.info("OpenAI moderation enabled.")
        else:
            logger.info("OpenAI moderation disabled. Using rule-based fallback.")
        return instance

    async def moderate_content(
        self, 
        content: str, 
        content_type: ContentType
    ) -> Tuple[bool, Dict[ModerationType, float]]:
        """
        Moderate content using OpenAI's moderation API or rule-based fallback.
        Returns (is_allowed, category_scores).
        """
        if self.use_openai:
            try:
                response = await openai.Moderation.create(input=content)
                results = response["results"][0]

                # Map OpenAI categories to our ModerationType
                scores = {
                    ModerationType.NUDITY: results["categories"].get("sexual", 0),
                    ModerationType.VIOLENCE: results["categories"].get("violence", 0),
                    ModerationType.HATE: results["categories"].get("hate", 0),
                    ModerationType.SELF_HARM: results["categories"].get("self-harm", 0),
                    ModerationType.SEXUAL: results["categories"].get("sexual", 0),
                    ModerationType.HARASSMENT: results["categories"].get("harassment", 0),
                    ModerationType.SPAM: 0.0  # OpenAI doesn't detect spam directly
                }

                # Check if any threshold is exceeded
                for category, score in scores.items():
                    if score >= self.auto_ban_thresholds[category]:
                        return False, scores

                return True, scores
            except Exception as e:
                logger.error(f"OpenAI moderation API call failed: {str(e)}")
                # Fall back to rule-based if API fails
                return await self._moderate_content_fallback(content)
        else:
            return await self._moderate_content_fallback(content)

    async def _moderate_content_fallback(self, content: str) -> Tuple[bool, Dict[ModerationType, float]]:
        """Rule-based content moderation fallback."""
        logger.warning("Using rule-based moderation fallback.")
        
        scores = {
            ModerationType.NUDITY: 0.0,
            ModerationType.VIOLENCE: 0.0,
            ModerationType.HATE: 0.0,
            ModerationType.SELF_HARM: 0.0,
            ModerationType.SEXUAL: 0.0,
            ModerationType.HARASSMENT: 0.0,
            ModerationType.SPAM: 0.0,
        }
        
        content_lower = content.lower()
        
        # Check for profanity/slurs (hate)
        for word in self.PROFANITY_WORDS:
            if word in content_lower:
                scores[ModerationType.HATE] = 0.3
                scores[ModerationType.HARASSMENT] = 0.3
                break
        
        # Check for spam patterns
        if re.search(r'[A-Z]{5,}', content):  # Excessive caps
            scores[ModerationType.SPAM] = 0.3
        if re.search(r'(.)\1{4,}', content):  # Repeated characters
            scores[ModerationType.SPAM] = 0.3
        if re.search(r'https?://', content):  # URLs
            scores[ModerationType.SPAM] = 0.3
        
        # Check for harassment patterns
        if any(word in content_lower for word in ["threat", "kill", "harm", "attack", "fuck you", "die"]):
            scores[ModerationType.HARASSMENT] = 0.3
            scores[ModerationType.VIOLENCE] = 0.3
        
        # Check if any threshold is exceeded
        is_allowed = True
        for category, score in scores.items():
            if score >= self.auto_ban_thresholds[category]:
                is_allowed = False
        
        return is_allowed, scores

    async def analyze_sentiment(self, text: str) -> float:
        """
        Analyze text sentiment using OpenAI or rule-based fallback.
        Returns score from -1 (very negative) to 1 (very positive).
        """
        if self.use_openai:
            try:
                response = await openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"Analyze the sentiment of this text and respond with a score from -1 to 1:\n{text}",
                    max_tokens=1,
                    temperature=0
                )
                sentiment = float(response.choices[0].text.strip())
                return max(-1, min(1, sentiment))  # Clamp between -1 and 1
            except Exception as e:
                logger.error(f"OpenAI sentiment analysis API call failed: {str(e)}")
                return self._analyze_sentiment_fallback(text)
        else:
            return self._analyze_sentiment_fallback(text)

    def _analyze_sentiment_fallback(self, text: str) -> float:
        """Rule-based sentiment analysis fallback."""
        text_lower = text.lower()
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / total_words
        return max(-1, min(1, sentiment))  # Clamp between -1 and 1

    def should_auto_ban(self, scores: Dict[ModerationType, float]) -> bool:
        """Check if content scores warrant an automatic ban."""
        for category, score in scores.items():
            if score >= self.auto_ban_thresholds[category]:
                return True
        return False

    async def flag_for_review(
        self,
        content_id: str,
        content_type: ContentType,
        scores: Dict[ModerationType, float],
        reviewer_id: Optional[str] = None
    ):
        """Flag content for manual review and store in database."""
        try:
            with SessionLocal() as db:
                # Check if content is already flagged
                existing_flag = db.query(ContentFlag).filter_by(
                    content_id=content_id,
                    content_type=content_type.value,
                    status="pending"
                ).first()
                
                if existing_flag:
                    # Update existing flag with new scores
                    existing_flag.moderation_scores = scores
                    existing_flag.updated_at = datetime.utcnow()
                else:
                    # Create new flag
                    flag = ContentFlag(
                        content_id=content_id,
                        content_type=content_type.value,
                        moderation_scores=scores,
                        flagged_by="system",
                        reviewer_id=reviewer_id,
                        status="pending",
                        priority=self._calculate_priority(scores),
                        created_at=datetime.utcnow()
                    )
                    db.add(flag)
                
                db.commit()
                logger.info(f"Content {content_id} flagged for review with scores: {scores}")
                
                # TODO: Send notification to moderators (implement in Phase 3)
                # await self._notify_moderators(content_id, scores)
                
        except Exception as e:
            logger.error(f"Failed to flag content for review: {str(e)}")
            # Don't raise exception to avoid breaking content creation flow

    def _calculate_priority(self, scores: Dict[ModerationType, float]) -> str:
        """Calculate priority level based on moderation scores."""
        max_score = max(scores.values()) if scores else 0.0
        if max_score >= 0.8:
            return "high"
        elif max_score >= 0.5:
            return "medium"
        else:
            return "low"