"""Social Media MCP Server implementation."""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from .platforms import (
    TwitterClient,
    LinkedInClient,
    InstagramClient,
    FacebookClient,
    PlatformClient
)
from .models import (
    Post,
    PostResult,
    Analytics,
    ScheduledPost,
    MediaAsset
)
from .utils import (
    optimize_image,
    optimize_video,
    generate_hashtags,
    find_optimal_posting_time
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaMCPServer:
    """MCP Server for social media management."""
    
    def __init__(self):
        self.server = Server("social-media-mcp")
        self.platforms: Dict[str, PlatformClient] = {}
        self.scheduled_posts: List[ScheduledPost] = []
        
        # Register handlers
        self.server.list_tools()(self.handle_list_tools)
        self.server.call_tool()(self.handle_call_tool)
        
    async def initialize(self):
        """Initialize platform clients with API credentials."""
        # Twitter/X
        if all(os.getenv(key) for key in ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET"]):
            self.platforms["twitter"] = TwitterClient(
                api_key=os.getenv("TWITTER_API_KEY"),
                api_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_secret=os.getenv("TWITTER_ACCESS_SECRET")
            )
            logger.info("Twitter client initialized")
            
        # LinkedIn
        if os.getenv("LINKEDIN_ACCESS_TOKEN"):
            self.platforms["linkedin"] = LinkedInClient(
                access_token=os.getenv("LINKEDIN_ACCESS_TOKEN")
            )
            logger.info("LinkedIn client initialized")
            
        # Instagram
        if os.getenv("INSTAGRAM_ACCESS_TOKEN"):
            self.platforms["instagram"] = InstagramClient(
                access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN"),
                business_account_id=os.getenv("INSTAGRAM_BUSINESS_ID")
            )
            logger.info("Instagram client initialized")
            
        # Facebook
        if os.getenv("FACEBOOK_ACCESS_TOKEN"):
            self.platforms["facebook"] = FacebookClient(
                access_token=os.getenv("FACEBOOK_ACCESS_TOKEN"),
                page_id=os.getenv("FACEBOOK_PAGE_ID")
            )
            logger.info("Facebook client initialized")
            
    async def handle_list_tools(self) -> List[types.Tool]:
        """List available social media tools."""
        return [
            types.Tool(
                name="create_post",
                description="Create and publish a post to one or more social media platforms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "platforms": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["twitter", "linkedin", "instagram", "facebook"]},
                            "description": "List of platforms to post to"
                        },
                        "content": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Post text content"},
                                "media": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string", "enum": ["image", "video"]},
                                            "path": {"type": "string"},
                                            "alt_text": {"type": "string"}
                                        }
                                    }
                                },
                                "hashtags": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["text"]
                        },
                        "schedule": {
                            "type": "string",
                            "format": "date-time",
                            "description": "ISO 8601 datetime to schedule the post"
                        },
                        "optimize_timing": {
                            "type": "boolean",
                            "description": "Whether to automatically optimize posting time"
                        }
                    },
                    "required": ["platforms", "content"]
                }
            ),
            types.Tool(
                name="get_analytics",
                description="Get analytics for posts and accounts",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "platforms": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["twitter", "linkedin", "instagram", "facebook"]}
                        },
                        "metric_type": {
                            "type": "string",
                            "enum": ["engagement", "reach", "impressions", "clicks", "conversions"],
                            "description": "Type of metrics to retrieve"
                        },
                        "date_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string", "format": "date"},
                                "end": {"type": "string", "format": "date"}
                            }
                        },
                        "post_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific post IDs to get analytics for"
                        }
                    },
                    "required": ["platforms"]
                }
            ),
            types.Tool(
                name="schedule_posts",
                description="Schedule multiple posts across platforms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "posts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "platforms": {"type": "array", "items": {"type": "string"}},
                                    "content": {"type": "object"},
                                    "schedule": {"type": "string", "format": "date-time"}
                                }
                            }
                        },
                        "optimize_spacing": {
                            "type": "boolean",
                            "description": "Automatically space out posts for optimal engagement"
                        }
                    },
                    "required": ["posts"]
                }
            ),
            types.Tool(
                name="generate_hashtags",
                description="Generate relevant hashtags based on content and trends",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Post content to generate hashtags for"},
                        "platform": {"type": "string", "enum": ["twitter", "linkedin", "instagram", "facebook"]},
                        "max_hashtags": {"type": "integer", "minimum": 1, "maximum": 30},
                        "include_trending": {"type": "boolean", "description": "Include currently trending hashtags"}
                    },
                    "required": ["content"]
                }
            ),
            types.Tool(
                name="optimize_media",
                description="Optimize images and videos for social media platforms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "media_path": {"type": "string", "description": "Path to the media file"},
                        "platforms": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["twitter", "linkedin", "instagram", "facebook"]},
                            "description": "Target platforms for optimization"
                        },
                        "media_type": {"type": "string", "enum": ["image", "video"]}
                    },
                    "required": ["media_path", "platforms", "media_type"]
                }
            ),
            types.Tool(
                name="get_trending",
                description="Get trending topics and hashtags",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "platforms": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["twitter", "linkedin", "instagram", "facebook"]}
                        },
                        "category": {
                            "type": "string",
                            "description": "Category or industry to filter trends"
                        },
                        "location": {
                            "type": "string",
                            "description": "Geographic location for trends"
                        }
                    },
                    "required": ["platforms"]
                }
            ),
            types.Tool(
                name="manage_calendar",
                description="Manage content calendar and scheduled posts",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["view", "update", "delete", "reschedule"],
                            "description": "Action to perform on the calendar"
                        },
                        "date_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string", "format": "date"},
                                "end": {"type": "string", "format": "date"}
                            }
                        },
                        "post_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific post IDs for update/delete actions"
                        }
                    },
                    "required": ["action"]
                }
            )
        ]
        
    async def handle_call_tool(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> List[types.TextContent]:
        """Handle tool calls for social media operations."""
        try:
            if name == "create_post":
                result = await self.create_post(arguments)
            elif name == "get_analytics":
                result = await self.get_analytics(arguments)
            elif name == "schedule_posts":
                result = await self.schedule_posts(arguments)
            elif name == "generate_hashtags":
                result = await self.generate_hashtags_tool(arguments)
            elif name == "optimize_media":
                result = await self.optimize_media(arguments)
            elif name == "get_trending":
                result = await self.get_trending(arguments)
            elif name == "manage_calendar":
                result = await self.manage_calendar(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
                
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error in {name}: {str(e)}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "tool": name
                }, indent=2)
            )]
            
    async def create_post(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create and publish a post to multiple platforms."""
        platforms = args["platforms"]
        content = args["content"]
        schedule = args.get("schedule")
        optimize_timing = args.get("optimize_timing", False)
        
        # Process media if provided
        media_assets = []
        if "media" in content:
            for media in content["media"]:
                if media["type"] == "image":
                    optimized_path = await optimize_image(
                        media["path"], 
                        platforms
                    )
                    media_assets.append(MediaAsset(
                        type="image",
                        path=optimized_path,
                        alt_text=media.get("alt_text", "")
                    ))
                elif media["type"] == "video":
                    optimized_path = await optimize_video(
                        media["path"],
                        platforms
                    )
                    media_assets.append(MediaAsset(
                        type="video",
                        path=optimized_path,
                        alt_text=media.get("alt_text", "")
                    ))
                    
        # Generate hashtags if not provided
        if "hashtags" not in content or not content["hashtags"]:
            hashtags = await generate_hashtags(
                content["text"],
                platforms[0] if platforms else "twitter"
            )
            content["hashtags"] = hashtags
            
        # Optimize posting time if requested
        if optimize_timing and not schedule:
            optimal_time = await find_optimal_posting_time(platforms)
            schedule = optimal_time.isoformat()
            
        # Create post object
        post = Post(
            text=content["text"],
            media=media_assets,
            hashtags=content.get("hashtags", []),
            platforms=platforms,
            scheduled_time=datetime.fromisoformat(schedule) if schedule else None
        )
        
        # Post to each platform
        results = {}
        for platform in platforms:
            if platform in self.platforms:
                try:
                    if schedule:
                        # Schedule the post
                        scheduled = ScheduledPost(
                            post=post,
                            platform=platform,
                            scheduled_time=datetime.fromisoformat(schedule)
                        )
                        self.scheduled_posts.append(scheduled)
                        results[platform] = {
                            "success": True,
                            "scheduled": True,
                            "scheduled_time": schedule
                        }
                    else:
                        # Post immediately
                        result = await self.platforms[platform].create_post(post)
                        results[platform] = result.dict()
                except Exception as e:
                    results[platform] = {
                        "success": False,
                        "error": str(e)
                    }
            else:
                results[platform] = {
                    "success": False,
                    "error": f"Platform {platform} not configured"
                }
                
        return {
            "results": results,
            "content": {
                "text": post.text,
                "hashtags": post.hashtags,
                "media_count": len(post.media)
            }
        }
        
    async def get_analytics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get analytics data from platforms."""
        platforms = args["platforms"]
        metric_type = args.get("metric_type", "engagement")
        date_range = args.get("date_range")
        post_ids = args.get("post_ids")
        
        analytics_data = {}
        for platform in platforms:
            if platform in self.platforms:
                try:
                    analytics = await self.platforms[platform].get_analytics(
                        metric_type=metric_type,
                        date_range=date_range,
                        post_ids=post_ids
                    )
                    analytics_data[platform] = analytics.dict()
                except Exception as e:
                    analytics_data[platform] = {
                        "error": str(e)
                    }
            else:
                analytics_data[platform] = {
                    "error": f"Platform {platform} not configured"
                }
                
        # Calculate aggregated metrics
        total_impressions = sum(
            data.get("impressions", 0) 
            for data in analytics_data.values() 
            if isinstance(data, dict) and "impressions" in data
        )
        total_engagement = sum(
            data.get("engagement", 0)
            for data in analytics_data.values()
            if isinstance(data, dict) and "engagement" in data
        )
        
        return {
            "platforms": analytics_data,
            "aggregated": {
                "total_impressions": total_impressions,
                "total_engagement": total_engagement,
                "engagement_rate": total_engagement / total_impressions if total_impressions > 0 else 0
            }
        }
        
    async def schedule_posts(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule multiple posts across platforms."""
        posts = args["posts"]
        optimize_spacing = args.get("optimize_spacing", False)
        
        scheduled_results = []
        
        if optimize_spacing and len(posts) > 1:
            # Space posts throughout the day for optimal engagement
            # This is a simplified implementation
            base_time = datetime.now(timezone.utc)
            spacing_hours = 4  # Space posts 4 hours apart
            
            for i, post_data in enumerate(posts):
                post_data["schedule"] = (
                    base_time + timedelta(hours=i * spacing_hours)
                ).isoformat()
                
        for post_data in posts:
            result = await self.create_post(post_data)
            scheduled_results.append(result)
            
        return {
            "scheduled_count": len(scheduled_results),
            "results": scheduled_results
        }
        
    async def generate_hashtags_tool(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hashtags for content."""
        content = args["content"]
        platform = args.get("platform", "twitter")
        max_hashtags = args.get("max_hashtags", 10)
        include_trending = args.get("include_trending", True)
        
        hashtags = await generate_hashtags(
            content,
            platform,
            max_count=max_hashtags,
            include_trending=include_trending
        )
        
        return {
            "hashtags": hashtags,
            "count": len(hashtags),
            "platform": platform
        }
        
    async def optimize_media(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize media files for social platforms."""
        media_path = args["media_path"]
        platforms = args["platforms"]
        media_type = args["media_type"]
        
        optimized_paths = {}
        
        for platform in platforms:
            try:
                if media_type == "image":
                    optimized_path = await optimize_image(media_path, [platform])
                else:
                    optimized_path = await optimize_video(media_path, [platform])
                    
                optimized_paths[platform] = {
                    "path": optimized_path,
                    "success": True
                }
            except Exception as e:
                optimized_paths[platform] = {
                    "success": False,
                    "error": str(e)
                }
                
        return {
            "original_path": media_path,
            "optimized": optimized_paths
        }
        
    async def get_trending(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get trending topics and hashtags."""
        platforms = args["platforms"]
        category = args.get("category")
        location = args.get("location")
        
        trending_data = {}
        
        for platform in platforms:
            if platform in self.platforms:
                try:
                    trends = await self.platforms[platform].get_trending(
                        category=category,
                        location=location
                    )
                    trending_data[platform] = trends
                except Exception as e:
                    trending_data[platform] = {
                        "error": str(e)
                    }
            else:
                trending_data[platform] = {
                    "error": f"Platform {platform} not configured"
                }
                
        return {
            "platforms": trending_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    async def manage_calendar(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage content calendar."""
        action = args["action"]
        date_range = args.get("date_range")
        post_ids = args.get("post_ids", [])
        
        if action == "view":
            # Filter scheduled posts by date range
            filtered_posts = self.scheduled_posts
            if date_range:
                start_date = datetime.fromisoformat(date_range["start"])
                end_date = datetime.fromisoformat(date_range["end"])
                filtered_posts = [
                    post for post in self.scheduled_posts
                    if start_date <= post.scheduled_time <= end_date
                ]
                
            return {
                "scheduled_posts": [
                    {
                        "id": post.id,
                        "platform": post.platform,
                        "scheduled_time": post.scheduled_time.isoformat(),
                        "content": post.post.text[:100] + "...",
                        "media_count": len(post.post.media),
                        "hashtags": post.post.hashtags
                    }
                    for post in filtered_posts
                ],
                "total_count": len(filtered_posts)
            }
            
        elif action == "delete":
            # Delete specified posts
            deleted_count = 0
            for post_id in post_ids:
                self.scheduled_posts = [
                    post for post in self.scheduled_posts
                    if post.id != post_id
                ]
                deleted_count += 1
                
            return {
                "action": "delete",
                "deleted_count": deleted_count
            }
            
        elif action == "reschedule":
            # This would need additional logic to handle rescheduling
            return {
                "action": "reschedule",
                "message": "Rescheduling functionality to be implemented"
            }
            
        return {
            "action": action,
            "status": "completed"
        }
        
    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.initialize()
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="social-media-mcp",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


async def main():
    """Main entry point."""
    server = SocialMediaMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())