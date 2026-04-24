from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class PostBase(BaseModel):
    content: Optional[str] = None
    media_urls: List[str] = Field(default_factory=list)
    media_type: str = Field(default="image")
    location: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    content: Optional[str] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None

class PostResponse(PostBase):
    id: int
    user_id: int
    likes_count: int
    comments_count: int
    shares_count: int
    views_count: int
    is_published: bool
    is_flagged: bool
    moderation_status: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class PostList(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    per_page: int

class PostDetail(PostResponse):
    user: Dict[str, Any]
    is_liked: bool
    is_bookmarked: bool

# Alias PostOut to PostResponse for compatibility
PostOut = PostResponse
