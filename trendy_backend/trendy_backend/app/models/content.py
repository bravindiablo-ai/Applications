"""
Content type enums and base models.
"""
from enum import Enum

class ContentType(str, Enum):
    """Types of content that can be moderated."""
    POST = "post"
    REEL = "reel"
    COMMENT = "comment"
    MESSAGE = "message"
    STORY = "story"
    PROFILE = "profile"