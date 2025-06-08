#!/usr/bin/env python3
"""
Example usage of the Social Media MCP Server.

This example demonstrates real-world usage patterns for the server.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Example 1: Basic posting to multiple platforms
async def example_basic_post(mcp_client):
    """Create a simple post across multiple platforms."""
    result = await mcp_client.call_tool("social-media", "create_post", {
        "platforms": ["twitter", "linkedin"],
        "content": {
            "text": "Excited to announce our new product launch! 🚀 Join us as we revolutionize marketing automation.",
            "hashtags": ["ProductLaunch", "MarketingAutomation", "Innovation"]
        }
    })
    
    print("Post created:", json.dumps(result, indent=2))


# Example 2: Post with media
async def example_media_post(mcp_client):
    """Create a post with optimized media."""
    # First, optimize the media
    optimization_result = await mcp_client.call_tool("social-media", "optimize_media", {
        "media_path": "/path/to/product-screenshot.png",
        "platforms": ["twitter", "instagram", "linkedin"],
        "media_type": "image"
    })
    
    # Then create the post with optimized media
    result = await mcp_client.call_tool("social-media", "create_post", {
        "platforms": ["twitter", "instagram", "linkedin"],
        "content": {
            "text": "Check out our new dashboard! Clean, intuitive, and powerful. What do you think?",
            "media": [{
                "type": "image",
                "path": optimization_result["optimized"]["twitter"]["path"],
                "alt_text": "New dashboard screenshot showing analytics"
            }]
        },
        "optimize_timing": True
    })
    
    print("Media post created:", json.dumps(result, indent=2))


# Example 3: Content calendar scheduling
async def example_content_calendar(mcp_client):
    """Schedule a week's worth of content."""
    posts = [
        {
            "platforms": ["twitter", "linkedin"],
            "content": {
                "text": "Monday Motivation: Your marketing doesn't have to be complicated. Start with understanding your audience. 💡",
                "hashtags": ["MondayMotivation", "MarketingTips"]
            },
            "schedule": (datetime.now() + timedelta(days=0, hours=9)).isoformat()
        },
        {
            "platforms": ["instagram", "facebook"],
            "content": {
                "text": "Behind the scenes: Our team hard at work creating amazing features for you! 👨‍💻👩‍💻",
                "media": [{
                    "type": "image",
                    "path": "/path/to/team-photo.jpg"
                }],
                "hashtags": ["TeamWork", "BehindTheScenes", "StartupLife"]
            },
            "schedule": (datetime.now() + timedelta(days=1, hours=14)).isoformat()
        },
        {
            "platforms": ["twitter"],
            "content": {
                "text": "New blog post: '5 Ways AI is Transforming Marketing in 2024' Read more: [link]",
                "hashtags": ["AIMarketing", "MarketingTrends"]
            },
            "schedule": (datetime.now() + timedelta(days=2, hours=10)).isoformat()
        },
        {
            "platforms": ["linkedin"],
            "content": {
                "text": "Thought leadership: The future of marketing is not about more tools, but smarter integration. Here's what we're seeing in the industry...",
                "hashtags": ["ThoughtLeadership", "MarketingStrategy", "Innovation"]
            },
            "schedule": (datetime.now() + timedelta(days=3, hours=8)).isoformat()
        },
        {
            "platforms": ["instagram", "facebook"],
            "content": {
                "text": "Customer success story! 🎉 See how @customer increased their engagement by 300% using our platform.",
                "media": [{
                    "type": "image",
                    "path": "/path/to/success-infographic.png"
                }]
            },
            "schedule": (datetime.now() + timedelta(days=4, hours=16)).isoformat()
        }
    ]
    
    result = await mcp_client.call_tool("social-media", "schedule_posts", {
        "posts": posts,
        "optimize_spacing": True
    })
    
    print(f"Scheduled {result['scheduled_count']} posts for the week")


# Example 4: Analytics and performance tracking
async def example_analytics(mcp_client):
    """Get analytics across all platforms."""
    # Get last week's performance
    result = await mcp_client.call_tool("social-media", "get_analytics", {
        "platforms": ["twitter", "linkedin", "instagram", "facebook"],
        "metric_type": "engagement",
        "date_range": {
            "start": (datetime.now() - timedelta(days=7)).date().isoformat(),
            "end": datetime.now().date().isoformat()
        }
    })
    
    print("Weekly Analytics Report:")
    print("-" * 50)
    
    for platform, data in result["platforms"].items():
        if "error" not in data:
            print(f"\n{platform.upper()}:")
            print(f"  Impressions: {data.get('impressions', 0):,}")
            print(f"  Engagement: {data.get('engagement', 0):,}")
            print(f"  Clicks: {data.get('clicks', 0):,}")
            print(f"  Engagement Rate: {data.get('engagement_rate', 0):.2f}%")
    
    print(f"\nTotal Engagement Rate: {result['aggregated']['engagement_rate']:.2f}%")


# Example 5: Trending topics and hashtag research
async def example_trending_research(mcp_client):
    """Research trending topics and generate relevant hashtags."""
    # Get trending topics
    trending = await mcp_client.call_tool("social-media", "get_trending", {
        "platforms": ["twitter", "linkedin"],
        "category": "technology",
        "location": "United States"
    })
    
    print("Trending Topics in Technology:")
    for platform, data in trending["platforms"].items():
        if "trending_topics" in data:
            print(f"\n{platform}:")
            for topic in data["trending_topics"][:5]:
                print(f"  - {topic['topic']} (volume: {topic.get('volume', 'N/A')})")
    
    # Generate hashtags based on content
    content = "Launching our AI-powered marketing automation platform that helps businesses scale their social media presence efficiently."
    
    hashtags = await mcp_client.call_tool("social-media", "generate_hashtags", {
        "content": content,
        "platform": "instagram",
        "max_hashtags": 15,
        "include_trending": True
    })
    
    print(f"\nGenerated {hashtags['count']} hashtags for Instagram:")
    print(", ".join(f"#{tag}" for tag in hashtags["hashtags"]))


# Example 6: A/B testing with different content variations
async def example_ab_testing(mcp_client):
    """Test different content variations."""
    variations = [
        {
            "platforms": ["twitter"],
            "content": {
                "text": "🚀 New Feature Alert: AI-powered content suggestions are here! Try it now →",
                "hashtags": ["NewFeature", "AI"]
            }
        },
        {
            "platforms": ["twitter"],
            "content": {
                "text": "Make your content work smarter, not harder. Our new AI suggestions feature is live! 🤖",
                "hashtags": ["ProductUpdate", "Marketing"]
            }
        }
    ]
    
    # Post variations at different times
    for i, variation in enumerate(variations):
        variation["schedule"] = (datetime.now() + timedelta(hours=i*4)).isoformat()
    
    result = await mcp_client.call_tool("social-media", "schedule_posts", {
        "posts": variations,
        "optimize_spacing": False  # We want specific timing for A/B test
    })
    
    print("A/B test variations scheduled")
    
    # Later, compare analytics for both posts
    # ... analytics comparison code ...


# Example 7: Crisis management - quick multi-platform update
async def example_crisis_communication(mcp_client):
    """Handle urgent communications across all platforms."""
    urgent_message = {
        "platforms": ["twitter", "linkedin", "facebook", "instagram"],
        "content": {
            "text": """Important Update: We're currently experiencing technical difficulties with our service. 
            
Our team is working hard to resolve this issue. We expect full service to be restored within 2 hours.
            
We apologize for any inconvenience. Updates will be posted every 30 minutes.
            
Thank you for your patience. 💙""",
            "hashtags": ["ServiceUpdate"]
        }
    }
    
    # Post immediately
    result = await mcp_client.call_tool("social-media", "create_post", urgent_message)
    
    print("Crisis communication posted to all platforms")
    
    # Schedule follow-up updates
    updates = []
    for i in range(1, 5):  # 4 updates, 30 minutes apart
        updates.append({
            "platforms": ["twitter", "facebook"],  # Most real-time platforms
            "content": {
                "text": f"Service Update {i}/4: Progress is being made. Current status: [status details]. ETA: {2-i*0.5} hours",
            },
            "schedule": (datetime.now() + timedelta(minutes=30*i)).isoformat()
        })
    
    await mcp_client.call_tool("social-media", "schedule_posts", {
        "posts": updates,
        "optimize_spacing": False
    })


# Example 8: Content performance optimization
async def example_performance_optimization(mcp_client):
    """Analyze and optimize content based on performance."""
    # Get best performing content
    analytics = await mcp_client.call_tool("social-media", "get_analytics", {
        "platforms": ["twitter", "linkedin", "instagram"],
        "metric_type": "engagement",
        "date_range": {
            "start": (datetime.now() - timedelta(days=30)).date().isoformat(),
            "end": datetime.now().date().isoformat()
        }
    })
    
    # View current calendar
    calendar = await mcp_client.call_tool("social-media", "manage_calendar", {
        "action": "view",
        "date_range": {
            "start": datetime.now().date().isoformat(),
            "end": (datetime.now() + timedelta(days=7)).date().isoformat()
        }
    })
    
    print(f"Upcoming posts: {calendar['total_count']}")
    
    # Analyze patterns and adjust strategy
    # ... analysis code ...


if __name__ == "__main__":
    # Example of how to run these examples
    # In a real implementation, you would use your MCP client
    
    print("Social Media MCP Server Usage Examples")
    print("=" * 50)
    print("\nThese examples demonstrate:")
    print("1. Basic multi-platform posting")
    print("2. Media optimization and posting")
    print("3. Content calendar scheduling")
    print("4. Analytics and performance tracking")
    print("5. Trending topic research")
    print("6. A/B testing strategies")
    print("7. Crisis communication")
    print("8. Performance optimization")
    print("\nTo run these examples, integrate with your MCP client.")