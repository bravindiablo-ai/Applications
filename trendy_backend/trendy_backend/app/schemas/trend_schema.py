from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TrendOut(BaseModel):
    content_id: str
    score: float
    rank: int
    category: Optional[str]
    updated_at: Optional[datetime]

class DiscoverItem(BaseModel):
    content_id: str
    score: float
    reason: str
    category: Optional[str]