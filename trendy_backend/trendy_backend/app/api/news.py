from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/")
async def get_news(category: str = "general") -> Dict[str, Any]:
    """Get latest news"""
    return {
        "articles": [
            {
                "id": 1,
                "title": "Breaking: Tech Industry Updates",
                "content": "Latest developments in the tech world...",
                "category": category,
                "published_at": datetime.now().isoformat()
            },
            {
                "id": 2,
                "title": "Sports: Championship Results",
                "content": "Exciting results from last night's games...",
                "category": category,
                "published_at": datetime.now().isoformat()
            }
        ],
        "total": 2
    }

@router.get("/categories")
async def get_categories() -> List[str]:
    """Get available news categories"""
    return ["general", "technology", "sports", "entertainment", "business", "health"]
