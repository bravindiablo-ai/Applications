"""
Lightweight AI Assistant endpoint (server-side orchestration).
This provides a REST endpoint that the client can call for conversational discovery.
Replace the 'generate_response' stub with your production LLM integration (OpenAI, Anthropic, local Llama, etc.)
"""
from typing import Dict
from fastapi import HTTPException
import random

class AIRecommendationsAssistant:
    def __init__(self, db=None):
        self.db = db

    def generate_recommendations(self, prompt: str, user_id: str = None, limit: int = 10) -> Dict:
        """
        Return a JSON-friendly recommendation payload.
        In production: call your recommend model / vector DB.
        """
        # lightweight placeholder: call existing HybridFeedEngine if available
        try:
            from app.services.hybrid_feed import HybridFeedEngine
            db = next(__import__('app.database', fromlist=['get_db']).get_db())
            feed_engine = HybridFeedEngine(db)
            items = feed_engine.discover_feed(user_id=user_id, limit=limit)
            return {"prompt": prompt, "items": items, "model":"placeholder"}
        except Exception:
            # fallback: mocked items
            items = [{"content_id": f"ai_demo_{i}", "score": round(random.random(),3)} for i in range(limit)]
            return {"prompt": prompt, "items": items, "model":"mock"}
