from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AdConfigBase(BaseModel):
    ad_unit_id: str = Field(..., max_length=255)
    ad_type: str = Field(..., max_length=50)  # banner, interstitial, rewarded
    platform: str = Field(..., max_length=50)  # android, ios, web
    is_active: bool = True

class AdImpressionBase(BaseModel):
    ad_unit_id: str = Field(..., max_length=255)
    ad_type: str = Field(..., max_length=50)
    revenue: float = Field(default=0.0, ge=0)
    currency: str = Field(default="USD", max_length=3)
    country: Optional[str] = Field(None, max_length=2)
    device_type: Optional[str] = Field(None, max_length=50)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AdImpressionCreate(AdImpressionBase):
    user_id: Optional[int] = None

class AdImpressionResponse(AdImpressionBase):
    id: int
    user_id: Optional[int]
    created_at: datetime
    
    class Config:
        orm_mode = True
