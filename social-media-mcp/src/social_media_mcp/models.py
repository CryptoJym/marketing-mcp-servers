"""Data models for social media MCP server."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class PlatformType(str, Enum):
    """Supported social media platforms."""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"


class MediaType(str, Enum):
    """Types of media content."""
    IMAGE = "image"
    VIDEO = "video"
    GIF = "gif"
    CAROUSEL = "carousel"


class MetricType(str, Enum):
    """Types of analytics metrics."""
    IMPRESSIONS = "impressions"
    ENGAGEMENT = "engagement"
    REACH = "reach"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    SHARES = "shares"
    LIKES = "likes"
    COMMENTS = "comments"


class MediaAsset(BaseModel):
    """Represents a media asset for social posts."""
    type: MediaType
    path: str
    alt_text: Optional[str] = ""
    thumbnail_path: Optional[str] = None
    duration_seconds: Optional[int] = None  # For videos
    dimensions: Optional[Dict[str, int]] = None  # {"width": 1920, "height": 1080}


class Post(BaseModel):
    """Represents a social media post."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    media: List[MediaAsset] = []
    hashtags: List[str] = []
    mentions: List[str] = []
    platforms: List[PlatformType] = []
    scheduled_time: Optional[datetime] = None
    location: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}


class PostResult(BaseModel):
    """Result of posting to a platform."""
    success: bool
    platform: PlatformType
    post_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Analytics(BaseModel):
    """Analytics data for posts or accounts."""
    platform: PlatformType
    metrics: Dict[MetricType, int]
    date_range: Optional[Dict[str, datetime]] = None
    post_ids: Optional[List[str]] = None
    demographic_data: Optional[Dict[str, Any]] = None
    top_content: Optional[List[Dict[str, Any]]] = None


class ScheduledPost(BaseModel):
    """Represents a scheduled post."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post: Post
    platform: PlatformType
    scheduled_time: datetime
    status: str = "pending"  # pending, posted, failed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class TrendingTopic(BaseModel):
    """Represents a trending topic or hashtag."""
    topic: str
    hashtag: Optional[str] = None
    volume: Optional[int] = None
    sentiment: Optional[float] = None  # -1 to 1
    platform: PlatformType
    location: Optional[str] = None
    category: Optional[str] = None


class ContentCalendarEntry(BaseModel):
    """Entry in the content calendar."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    posts: List[ScheduledPost] = []
    campaign_id: Optional[str] = None
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Campaign(BaseModel):
    """Marketing campaign containing multiple posts."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    platforms: List[PlatformType]
    goals: Dict[str, Any] = {}
    budget: Optional[float] = None
    posts: List[Post] = []
    analytics: Optional[Analytics] = None


class PlatformConfig(BaseModel):
    """Configuration for a social media platform."""
    platform: PlatformType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    page_id: Optional[str] = None
    business_account_id: Optional[str] = None
    webhook_url: Optional[str] = None


class OptimizationSettings(BaseModel):
    """Settings for content optimization."""
    auto_hashtags: bool = True
    max_hashtags: int = 10
    optimize_timing: bool = True
    optimize_media: bool = True
    target_engagement_rate: float = 0.05
    preferred_posting_times: List[Dict[str, Any]] = []
    content_variations: bool = False


class MediaOptimizationResult(BaseModel):
    """Result of media optimization."""
    original_path: str
    optimized_path: str
    platform: PlatformType
    original_size_bytes: int
    optimized_size_bytes: int
    compression_ratio: float
    format_changes: Dict[str, str] = {}
    dimensions: Dict[str, int] = {}


class HashtagRecommendation(BaseModel):
    """Hashtag recommendation with metadata."""
    hashtag: str
    relevance_score: float
    estimated_reach: Optional[int] = None
    competition_level: Optional[str] = None  # low, medium, high
    trending: bool = False
    category: Optional[str] = None