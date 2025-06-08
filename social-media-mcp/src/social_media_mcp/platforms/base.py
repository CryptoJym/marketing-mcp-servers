"""Base platform client interface."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..models import Post, PostResult, Analytics


class PlatformClient(ABC):
    """Abstract base class for social media platform clients."""
    
    @abstractmethod
    async def create_post(self, post: Post) -> PostResult:
        """Create a post on the platform."""
        pass
    
    @abstractmethod
    async def get_analytics(
        self,
        metric_type: str,
        date_range: Optional[Dict[str, str]] = None,
        post_ids: Optional[List[str]] = None
    ) -> Analytics:
        """Get analytics data from the platform."""
        pass
    
    @abstractmethod
    async def get_trending(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get trending topics and hashtags."""
        pass
    
    @abstractmethod
    async def schedule_post(
        self,
        post: Post,
        scheduled_time: datetime
    ) -> Dict[str, Any]:
        """Schedule a post for future publishing."""
        pass
    
    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """Delete a post from the platform."""
        pass
    
    @abstractmethod
    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """Get details about a specific post."""
        pass