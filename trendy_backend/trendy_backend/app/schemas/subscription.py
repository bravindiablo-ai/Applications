from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class SubscriptionBase(BaseModel):
    provider: str = Field(..., max_length=50)  # stripe, google_play, apple_store
    subscription_id: str = Field(..., max_length=255)
    product_id: str = Field(..., max_length=255)
    status: str = Field(..., max_length=50)  # active, cancelled, expired
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SubscriptionCreate(SubscriptionBase):
    user_id: int

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True
