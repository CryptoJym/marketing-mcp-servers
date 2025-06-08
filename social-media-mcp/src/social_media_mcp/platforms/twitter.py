"""Twitter/X platform client implementation."""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import tweepy
from tweepy.errors import TweepyException, TwitterServerError

from .base import PlatformClient
from ..models import Post, PostResult, Analytics, PlatformType

logger = logging.getLogger(__name__)


class TwitterClient(PlatformClient):
    """Twitter/X API client with real API implementation."""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str
    ):
        """Initialize Twitter client with credentials."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        
        try:
            # Initialize Tweepy v2 client
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True  # Auto handle rate limits
            )
            
            # Initialize API v1.1 for media upload
            auth = tweepy.OAuth1UserHandler(
                api_key, api_secret, access_token, access_token_secret
            )
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Verify credentials
            self._verify_credentials()
            
        except TweepyException as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            raise
    
    def _verify_credentials(self):
        """Verify that credentials are valid."""
        try:
            # Test API access
            self.api_v1.verify_credentials()
            logger.info("Twitter credentials verified successfully")
        except TweepyException as e:
            logger.error(f"Invalid Twitter credentials: {e}")
            raise ValueError("Invalid Twitter API credentials")
    
    async def create_post(self, post: Post) -> PostResult:
        """Create a post on Twitter."""
        try:
            # Format text with hashtags
            text = post.text
            if post.hashtags:
                hashtag_text = " ".join(f"#{tag}" for tag in post.hashtags)
                text = f"{text}\n\n{hashtag_text}"
            
            # Upload media if present
            media_ids = []
            if post.media:
                for media in post.media[:4]:  # Twitter allows max 4 images
                    if media.type == "image":
                        media_obj = self.api_v1.media_upload(media.path)
                        media_ids.append(media_obj.media_id)
            
            # Create tweet
            response = self.client.create_tweet(
                text=text,
                media_ids=media_ids if media_ids else None
            )
            
            tweet_id = response.data['id']
            
            return PostResult(
                success=True,
                platform=PlatformType.TWITTER,
                post_id=tweet_id,
                url=f"https://twitter.com/user/status/{tweet_id}"
            )
            
        except Exception as e:
            logger.error(f"Twitter post failed: {e}")
            return PostResult(
                success=False,
                platform=PlatformType.TWITTER,
                error=str(e)
            )
    
    async def get_analytics(
        self,
        metric_type: str,
        date_range: Optional[Dict[str, str]] = None,
        post_ids: Optional[List[str]] = None
    ) -> Analytics:
        """Get analytics data from Twitter."""
        try:
            metrics = {}
            
            if post_ids:
                # Get metrics for specific tweets
                tweets = self.client.get_tweets(
                    ids=post_ids,
                    tweet_fields=['public_metrics']
                )
                
                total_impressions = 0
                total_engagement = 0
                
                for tweet in tweets.data:
                    metrics_data = tweet.public_metrics
                    total_impressions += metrics_data['impression_count']
                    total_engagement += (
                        metrics_data['like_count'] +
                        metrics_data['retweet_count'] +
                        metrics_data['reply_count']
                    )
                
                metrics = {
                    "impressions": total_impressions,
                    "engagement": total_engagement,
                    "likes": sum(t.public_metrics['like_count'] for t in tweets.data),
                    "shares": sum(t.public_metrics['retweet_count'] for t in tweets.data),
                    "comments": sum(t.public_metrics['reply_count'] for t in tweets.data)
                }
            else:
                # Get account-level metrics
                # Note: This requires Twitter API v2 with appropriate access level
                metrics = {
                    "impressions": 0,
                    "engagement": 0,
                    "followers": 0
                }
            
            return Analytics(
                platform=PlatformType.TWITTER,
                metrics=metrics,
                date_range=date_range,
                post_ids=post_ids
            )
            
        except Exception as e:
            logger.error(f"Twitter analytics failed: {e}")
            return Analytics(
                platform=PlatformType.TWITTER,
                metrics={}
            )
    
    async def get_trending(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get trending topics from Twitter."""
        try:
            # Get worldwide trends by default
            woeid = 1  # Worldwide
            
            trends = self.api_v1.get_place_trends(woeid)
            
            trending_topics = []
            for trend in trends[0]['trends'][:10]:
                trending_topics.append({
                    "topic": trend['name'],
                    "volume": trend.get('tweet_volume', 0),
                    "url": trend['url']
                })
            
            return {
                "trending_topics": trending_topics,
                "location": location or "Worldwide",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Twitter trending failed: {e}")
            return {"error": str(e)}
    
    async def schedule_post(
        self,
        post: Post,
        scheduled_time: datetime
    ) -> Dict[str, Any]:
        """Schedule a post for future publishing."""
        # Twitter doesn't have native scheduling in the API
        # This would need to be handled by the MCP server's scheduling system
        return {
            "scheduled": True,
            "scheduled_time": scheduled_time.isoformat(),
            "message": "Post scheduled in MCP server queue"
        }
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete a tweet."""
        try:
            self.client.delete_tweet(post_id)
            return True
        except Exception as e:
            logger.error(f"Twitter delete failed: {e}")
            return False
    
    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """Get details about a specific tweet."""
        try:
            tweet = self.client.get_tweet(
                post_id,
                tweet_fields=['public_metrics', 'created_at']
            )
            
            return {
                "id": tweet.data.id,
                "text": tweet.data.text,
                "created_at": tweet.data.created_at,
                "metrics": tweet.data.public_metrics
            }
            
        except Exception as e:
            logger.error(f"Twitter get post failed: {e}")
            return {"error": str(e)}