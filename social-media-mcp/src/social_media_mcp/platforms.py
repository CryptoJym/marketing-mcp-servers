"""Platform-specific client implementations."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

import tweepy
import httpx
from PIL import Image
import moviepy.editor as mp

from .models import (
    Post, PostResult, Analytics, TrendingTopic,
    PlatformType, MetricType, MediaAsset
)

logger = logging.getLogger(__name__)


class PlatformClient(ABC):
    """Abstract base class for platform clients."""
    
    @abstractmethod
    async def create_post(self, post: Post) -> PostResult:
        """Create a post on the platform."""
        pass
        
    @abstractmethod
    async def get_analytics(
        self,
        metric_type: str,
        date_range: Optional[Dict[str, datetime]] = None,
        post_ids: Optional[List[str]] = None
    ) -> Analytics:
        """Get analytics data."""
        pass
        
    @abstractmethod
    async def get_trending(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[TrendingTopic]:
        """Get trending topics."""
        pass


class TwitterClient(PlatformClient):
    """Twitter/X API client."""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_secret: str):
        # Twitter API v2
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )
        # v1.1 for media upload
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        self.api = tweepy.API(auth)
        
    async def create_post(self, post: Post) -> PostResult:
        """Create a tweet."""
        try:
            # Prepare tweet text
            text = post.text
            if post.hashtags:
                hashtag_text = " ".join(f"#{tag}" for tag in post.hashtags)
                text = f"{text} {hashtag_text}"
                
            # Handle media upload
            media_ids = []
            for media in post.media:
                if media.type == "image":
                    media_upload = self.api.media_upload(media.path)
                    media_ids.append(media_upload.media_id)
                elif media.type == "video":
                    media_upload = self.api.media_upload(
                        media.path,
                        media_category="tweet_video"
                    )
                    media_ids.append(media_upload.media_id)
                    
            # Create tweet
            if media_ids:
                response = self.client.create_tweet(
                    text=text,
                    media_ids=media_ids
                )
            else:
                response = self.client.create_tweet(text=text)
                
            tweet_id = response.data["id"]
            
            return PostResult(
                success=True,
                platform=PlatformType.TWITTER,
                post_id=tweet_id,
                url=f"https://twitter.com/user/status/{tweet_id}"
            )
            
        except Exception as e:
            logger.error(f"Twitter post failed: {str(e)}")
            return PostResult(
                success=False,
                platform=PlatformType.TWITTER,
                error=str(e)
            )
            
    async def get_analytics(
        self,
        metric_type: str,
        date_range: Optional[Dict[str, datetime]] = None,
        post_ids: Optional[List[str]] = None
    ) -> Analytics:
        """Get Twitter analytics."""
        try:
            metrics = {}
            
            if post_ids:
                # Get metrics for specific tweets
                for tweet_id in post_ids:
                    tweet = self.client.get_tweet(
                        tweet_id,
                        tweet_fields=["public_metrics"]
                    )
                    if tweet.data:
                        public_metrics = tweet.data.public_metrics
                        metrics[MetricType.IMPRESSIONS] = public_metrics.get("impression_count", 0)
                        metrics[MetricType.LIKES] = public_metrics.get("like_count", 0)
                        metrics[MetricType.SHARES] = public_metrics.get("retweet_count", 0)
                        metrics[MetricType.COMMENTS] = public_metrics.get("reply_count", 0)
            else:
                # Get account-level metrics
                # This would require Twitter Analytics API access
                metrics[MetricType.IMPRESSIONS] = 0
                metrics[MetricType.ENGAGEMENT] = 0
                
            return Analytics(
                platform=PlatformType.TWITTER,
                metrics=metrics,
                date_range=date_range,
                post_ids=post_ids
            )
            
        except Exception as e:
            logger.error(f"Twitter analytics failed: {str(e)}")
            raise
            
    async def get_trending(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[TrendingTopic]:
        """Get trending topics on Twitter."""
        try:
            # Get trending topics
            # Default to worldwide trends (WOEID 1)
            woeid = 1
            trends = self.api.get_place_trends(woeid)[0]["trends"]
            
            trending_topics = []
            for trend in trends[:20]:  # Top 20 trends
                trending_topics.append(TrendingTopic(
                    topic=trend["name"],
                    hashtag=trend["name"] if trend["name"].startswith("#") else f"#{trend['name']}",
                    volume=trend.get("tweet_volume"),
                    platform=PlatformType.TWITTER,
                    location=location
                ))
                
            return trending_topics
            
        except Exception as e:
            logger.error(f"Twitter trends failed: {str(e)}")
            return []


class LinkedInClient(PlatformClient):
    """LinkedIn API client."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
    async def create_post(self, post: Post) -> PostResult:
        """Create a LinkedIn post."""
        try:
            async with httpx.AsyncClient() as client:
                # Get user profile
                profile_response = await client.get(
                    f"{self.base_url}/me",
                    headers=self.headers
                )
                profile_data = profile_response.json()
                author = f"urn:li:person:{profile_data['id']}"
                
                # Prepare post data
                post_data = {
                    "author": author,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": post.text
                            },
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
                
                # Handle media
                if post.media:
                    # LinkedIn media upload is complex, simplified here
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                    # Would need to implement media upload flow
                    
                # Create post
                response = await client.post(
                    f"{self.base_url}/ugcPosts",
                    headers=self.headers,
                    json=post_data
                )
                
                if response.status_code == 201:
                    post_id = response.headers.get("X-LinkedIn-Id")
                    return PostResult(
                        success=True,
                        platform=PlatformType.LINKEDIN,
                        post_id=post_id,
                        url=f"https://www.linkedin.com/feed/update/{post_id}"
                    )
                else:
                    raise Exception(f"LinkedIn API error: {response.text}")
                    
        except Exception as e:
            logger.error(f"LinkedIn post failed: {str(e)}")
            return PostResult(
                success=False,
                platform=PlatformType.LINKEDIN,
                error=str(e)
            )
            
    async def get_analytics(
        self,
        metric_type: str,
        date_range: Optional[Dict[str, datetime]] = None,
        post_ids: Optional[List[str]] = None
    ) -> Analytics:
        """Get LinkedIn analytics."""
        try:
            async with httpx.AsyncClient() as client:
                # LinkedIn analytics API
                # This is a simplified implementation
                metrics = {
                    MetricType.IMPRESSIONS: 0,
                    MetricType.ENGAGEMENT: 0,
                    MetricType.CLICKS: 0
                }
                
                if post_ids:
                    for post_id in post_ids:
                        # Get post statistics
                        response = await client.get(
                            f"{self.base_url}/socialActions/{post_id}",
                            headers=self.headers
                        )
                        if response.status_code == 200:
                            data = response.json()
                            # Parse metrics from response
                            pass
                            
                return Analytics(
                    platform=PlatformType.LINKEDIN,
                    metrics=metrics,
                    date_range=date_range,
                    post_ids=post_ids
                )
                
        except Exception as e:
            logger.error(f"LinkedIn analytics failed: {str(e)}")
            raise
            
    async def get_trending(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[TrendingTopic]:
        """Get trending topics on LinkedIn."""
        # LinkedIn doesn't have a public trending API
        # Would need to implement custom trending analysis
        return []


class InstagramClient(PlatformClient):
    """Instagram Graph API client."""
    
    def __init__(self, access_token: str, business_account_id: str):
        self.access_token = access_token
        self.business_account_id = business_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
    async def create_post(self, post: Post) -> PostResult:
        """Create an Instagram post."""
        try:
            async with httpx.AsyncClient() as client:
                # Instagram requires media
                if not post.media:
                    raise ValueError("Instagram posts require at least one image or video")
                    
                media = post.media[0]  # Instagram single post
                
                # Create media container
                if media.type == "image":
                    container_params = {
                        "image_url": media.path,  # Must be publicly accessible URL
                        "caption": post.text,
                        "access_token": self.access_token
                    }
                    
                    # Add hashtags to caption
                    if post.hashtags:
                        hashtag_text = " ".join(f"#{tag}" for tag in post.hashtags)
                        container_params["caption"] = f"{post.text}\n\n{hashtag_text}"
                        
                    # Create container
                    container_response = await client.post(
                        f"{self.base_url}/{self.business_account_id}/media",
                        params=container_params
                    )
                    
                    if container_response.status_code == 200:
                        container_data = container_response.json()
                        container_id = container_data["id"]
                        
                        # Publish container
                        publish_params = {
                            "creation_id": container_id,
                            "access_token": self.access_token
                        }
                        
                        publish_response = await client.post(
                            f"{self.base_url}/{self.business_account_id}/media_publish",
                            params=publish_params
                        )
                        
                        if publish_response.status_code == 200:
                            publish_data = publish_response.json()
                            post_id = publish_data["id"]
                            
                            return PostResult(
                                success=True,
                                platform=PlatformType.INSTAGRAM,
                                post_id=post_id,
                                url=f"https://www.instagram.com/p/{post_id}"
                            )
                            
                raise Exception("Instagram post creation failed")
                
        except Exception as e:
            logger.error(f"Instagram post failed: {str(e)}")
            return PostResult(
                success=False,
                platform=PlatformType.INSTAGRAM,
                error=str(e)
            )
            
    async def get_analytics(
        self,
        metric_type: str,
        date_range: Optional[Dict[str, datetime]] = None,
        post_ids: Optional[List[str]] = None
    ) -> Analytics:
        """Get Instagram analytics."""
        try:
            async with httpx.AsyncClient() as client:
                metrics = {}
                
                if post_ids:
                    # Get insights for specific posts
                    for post_id in post_ids:
                        insights_response = await client.get(
                            f"{self.base_url}/{post_id}/insights",
                            params={
                                "metric": "impressions,reach,engagement",
                                "access_token": self.access_token
                            }
                        )
                        
                        if insights_response.status_code == 200:
                            insights_data = insights_response.json()
                            # Parse insights
                            for insight in insights_data.get("data", []):
                                if insight["name"] == "impressions":
                                    metrics[MetricType.IMPRESSIONS] = insight["values"][0]["value"]
                                elif insight["name"] == "reach":
                                    metrics[MetricType.REACH] = insight["values"][0]["value"]
                                elif insight["name"] == "engagement":
                                    metrics[MetricType.ENGAGEMENT] = insight["values"][0]["value"]
                                    
                return Analytics(
                    platform=PlatformType.INSTAGRAM,
                    metrics=metrics,
                    date_range=date_range,
                    post_ids=post_ids
                )
                
        except Exception as e:
            logger.error(f"Instagram analytics failed: {str(e)}")
            raise
            
    async def get_trending(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[TrendingTopic]:
        """Get trending topics on Instagram."""
        # Instagram doesn't provide trending hashtags via API
        # Would need to implement custom trending analysis
        return []


class FacebookClient(PlatformClient):
    """Facebook Graph API client."""
    
    def __init__(self, access_token: str, page_id: str):
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
    async def create_post(self, post: Post) -> PostResult:
        """Create a Facebook post."""
        try:
            async with httpx.AsyncClient() as client:
                # Prepare post data
                post_data = {
                    "message": post.text,
                    "access_token": self.access_token
                }
                
                # Add hashtags to message
                if post.hashtags:
                    hashtag_text = " ".join(f"#{tag}" for tag in post.hashtags)
                    post_data["message"] = f"{post.text}\n\n{hashtag_text}"
                    
                # Handle media
                endpoint = f"{self.base_url}/{self.page_id}/feed"
                if post.media:
                    media = post.media[0]
                    if media.type == "image":
                        endpoint = f"{self.base_url}/{self.page_id}/photos"
                        post_data["url"] = media.path  # Must be publicly accessible
                    elif media.type == "video":
                        endpoint = f"{self.base_url}/{self.page_id}/videos"
                        # Video upload is more complex
                        
                # Create post
                response = await client.post(endpoint, data=post_data)
                
                if response.status_code == 200:
                    response_data = response.json()
                    post_id = response_data["id"]
                    
                    return PostResult(
                        success=True,
                        platform=PlatformType.FACEBOOK,
                        post_id=post_id,
                        url=f"https://www.facebook.com/{post_id}"
                    )
                else:
                    raise Exception(f"Facebook API error: {response.text}")
                    
        except Exception as e:
            logger.error(f"Facebook post failed: {str(e)}")
            return PostResult(
                success=False,
                platform=PlatformType.FACEBOOK,
                error=str(e)
            )
            
    async def get_analytics(
        self,
        metric_type: str,
        date_range: Optional[Dict[str, datetime]] = None,
        post_ids: Optional[List[str]] = None
    ) -> Analytics:
        """Get Facebook analytics."""
        try:
            async with httpx.AsyncClient() as client:
                metrics = {}
                
                if post_ids:
                    # Get insights for specific posts
                    for post_id in post_ids:
                        insights_response = await client.get(
                            f"{self.base_url}/{post_id}/insights",
                            params={
                                "metric": "post_impressions,post_engaged_users,post_clicks",
                                "access_token": self.access_token
                            }
                        )
                        
                        if insights_response.status_code == 200:
                            insights_data = insights_response.json()
                            # Parse insights
                            for insight in insights_data.get("data", []):
                                if insight["name"] == "post_impressions":
                                    metrics[MetricType.IMPRESSIONS] = insight["values"][0]["value"]
                                elif insight["name"] == "post_engaged_users":
                                    metrics[MetricType.ENGAGEMENT] = insight["values"][0]["value"]
                                elif insight["name"] == "post_clicks":
                                    metrics[MetricType.CLICKS] = insight["values"][0]["value"]
                                    
                return Analytics(
                    platform=PlatformType.FACEBOOK,
                    metrics=metrics,
                    date_range=date_range,
                    post_ids=post_ids
                )
                
        except Exception as e:
            logger.error(f"Facebook analytics failed: {str(e)}")
            raise
            
    async def get_trending(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[TrendingTopic]:
        """Get trending topics on Facebook."""
        # Facebook doesn't provide trending topics via API anymore
        return []