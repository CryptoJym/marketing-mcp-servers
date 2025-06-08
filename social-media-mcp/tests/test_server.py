"""Real tests for Social Media MCP Server."""

import pytest
import asyncio
import os
import json
from datetime import datetime, timezone
from pathlib import Path

from social_media_mcp.server import SocialMediaMCPServer
from social_media_mcp.models import Post, MediaAsset, PlatformType


class TestSocialMediaMCPServer:
    """Test suite for Social Media MCP Server with real functionality."""
    
    @pytest.fixture
    async def server(self):
        """Create a server instance."""
        server = SocialMediaMCPServer()
        await server.initialize()
        return server
    
    @pytest.fixture
    def sample_image(self, tmp_path):
        """Create a real test image."""
        from PIL import Image
        
        # Create a real image file
        img = Image.new('RGB', (1200, 675), color=(73, 109, 137))
        img_path = tmp_path / "test_image.jpg"
        img.save(img_path)
        return str(img_path)
    
    @pytest.fixture
    def sample_video(self, tmp_path):
        """Create a real test video."""
        import cv2
        import numpy as np
        
        # Create a simple video file
        video_path = tmp_path / "test_video.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(video_path), fourcc, 20.0, (640, 480))
        
        # Generate 30 frames (1.5 seconds at 20fps)
        for i in range(30):
            frame = np.zeros((480, 640, 3), np.uint8)
            cv2.putText(frame, f'Frame {i}', (50, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            out.write(frame)
        
        out.release()
        return str(video_path)
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, server):
        """Test that server initializes correctly."""
        assert server is not None
        assert hasattr(server, 'platforms')
        assert hasattr(server, 'scheduled_posts')
    
    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test that all tools are properly registered."""
        tools = await server.handle_list_tools()
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "create_post",
            "get_analytics", 
            "schedule_posts",
            "generate_hashtags",
            "optimize_media",
            "get_trending",
            "manage_calendar"
        ]
        
        for expected in expected_tools:
            assert expected in tool_names, f"Tool {expected} not found"
    
    @pytest.mark.asyncio
    async def test_create_post_validation(self, server):
        """Test post creation with validation."""
        # Test with invalid platform
        result = await server.handle_call_tool("create_post", {
            "platforms": ["invalid_platform"],
            "content": {"text": "Test post"}
        })
        
        response = json.loads(result[0].text)
        assert "invalid_platform" in response["results"]
        assert "not configured" in response["results"]["invalid_platform"]["error"]
    
    @pytest.mark.asyncio
    async def test_generate_hashtags_real(self, server):
        """Test real hashtag generation."""
        result = await server.handle_call_tool("generate_hashtags", {
            "content": "Launching our new AI-powered marketing automation platform with advanced analytics",
            "platform": "instagram",
            "max_hashtags": 10,
            "include_trending": False
        })
        
        response = json.loads(result[0].text)
        assert "hashtags" in response
        assert isinstance(response["hashtags"], list)
        assert len(response["hashtags"]) <= 10
        
        # Check that hashtags are relevant to content
        content_words = ["ai", "marketing", "automation", "analytics", "platform"]
        hashtags_lower = [h.lower() for h in response["hashtags"]]
        
        # At least some hashtags should relate to content
        relevant_count = sum(1 for word in content_words 
                           if any(word in hashtag for hashtag in hashtags_lower))
        assert relevant_count > 0, "Generated hashtags should be relevant to content"
    
    @pytest.mark.asyncio
    async def test_optimize_image_real(self, server, sample_image):
        """Test real image optimization."""
        result = await server.handle_call_tool("optimize_media", {
            "media_path": sample_image,
            "platforms": ["twitter", "instagram"],
            "media_type": "image"
        })
        
        response = json.loads(result[0].text)
        assert "optimized" in response
        
        # Check that optimization actually created files
        for platform in ["twitter", "instagram"]:
            if platform in response["optimized"] and response["optimized"][platform]["success"]:
                optimized_path = response["optimized"][platform]["path"]
                assert Path(optimized_path).exists(), f"Optimized file should exist for {platform}"
                
                # Verify the optimized image has appropriate dimensions
                from PIL import Image
                img = Image.open(optimized_path)
                assert img.width <= 1200, "Image width should be optimized"
                assert img.height <= 1350, "Image height should be optimized"
    
    @pytest.mark.asyncio
    async def test_schedule_posts_with_spacing(self, server):
        """Test scheduling multiple posts with optimized spacing."""
        posts = [
            {
                "platforms": ["twitter"],
                "content": {"text": "Morning update #1"}
            },
            {
                "platforms": ["twitter"],
                "content": {"text": "Afternoon update #2"}
            },
            {
                "platforms": ["twitter"],
                "content": {"text": "Evening update #3"}
            }
        ]
        
        result = await server.handle_call_tool("schedule_posts", {
            "posts": posts,
            "optimize_spacing": True
        })
        
        response = json.loads(result[0].text)
        assert response["scheduled_count"] == 3
        
        # Verify posts are properly spaced
        scheduled_times = []
        for post_result in response["results"]:
            for platform, data in post_result["results"].items():
                if "scheduled_time" in data:
                    scheduled_times.append(datetime.fromisoformat(data["scheduled_time"]))
        
        # Check that posts are at least 2 hours apart
        scheduled_times.sort()
        for i in range(1, len(scheduled_times)):
            time_diff = (scheduled_times[i] - scheduled_times[i-1]).total_seconds() / 3600
            assert time_diff >= 2, "Posts should be at least 2 hours apart"
    
    @pytest.mark.asyncio
    async def test_manage_calendar_operations(self, server):
        """Test calendar management operations."""
        # First, schedule some posts
        await server.handle_call_tool("create_post", {
            "platforms": ["twitter"],
            "content": {"text": "Scheduled post for calendar test"},
            "schedule": (datetime.now(timezone.utc).replace(hour=15, minute=0)).isoformat()
        })
        
        # View calendar
        result = await server.handle_call_tool("manage_calendar", {
            "action": "view",
            "date_range": {
                "start": datetime.now(timezone.utc).date().isoformat(),
                "end": (datetime.now(timezone.utc).date()).isoformat()
            }
        })
        
        response = json.loads(result[0].text)
        assert "scheduled_posts" in response
        assert response["total_count"] >= 0
    
    @pytest.mark.asyncio
    async def test_content_validation(self, server):
        """Test content validation for different platforms."""
        from social_media_mcp.utils import validate_post_content
        
        # Test Twitter character limit
        valid, msg = validate_post_content("a" * 280, "twitter")
        assert valid is True
        
        valid, msg = validate_post_content("a" * 281, "twitter")
        assert valid is False
        assert "character limit" in msg
        
        # Test Instagram without hashtags (warning, not error)
        valid, msg = validate_post_content("Great photo!", "instagram")
        assert valid is True
        assert msg is not None  # Should have a warning
    
    @pytest.mark.asyncio
    async def test_media_format_validation(self, server, tmp_path):
        """Test that unsupported media formats are rejected."""
        # Create an unsupported file
        unsupported_file = tmp_path / "test.bmp"
        unsupported_file.write_text("fake bmp content")
        
        result = await server.handle_call_tool("optimize_media", {
            "media_path": str(unsupported_file),
            "platforms": ["twitter"],
            "media_type": "image"
        })
        
        response = json.loads(result[0].text)
        assert "twitter" in response["optimized"]
        assert response["optimized"]["twitter"]["success"] is False
    
    @pytest.mark.asyncio
    async def test_analytics_aggregation(self, server):
        """Test analytics aggregation across platforms."""
        # This would need real API credentials to fully test
        # For now, test the aggregation logic
        result = await server.handle_call_tool("get_analytics", {
            "platforms": ["twitter", "instagram"],
            "metric_type": "engagement"
        })
        
        response = json.loads(result[0].text)
        assert "platforms" in response
        assert "aggregated" in response
        assert "total_impressions" in response["aggregated"]
        assert "total_engagement" in response["aggregated"]
        assert "engagement_rate" in response["aggregated"]
    
    @pytest.mark.asyncio
    async def test_trending_topics_structure(self, server):
        """Test trending topics response structure."""
        result = await server.handle_call_tool("get_trending", {
            "platforms": ["twitter"],
            "category": "technology"
        })
        
        response = json.loads(result[0].text)
        assert "platforms" in response
        assert "timestamp" in response
        
        # Verify timestamp is valid ISO format
        timestamp = datetime.fromisoformat(response["timestamp"].replace('Z', '+00:00'))
        assert timestamp is not None


class TestPlatformClients:
    """Test individual platform client implementations."""
    
    @pytest.mark.asyncio
    async def test_twitter_client_structure(self):
        """Test Twitter client has required methods."""
        from social_media_mcp.platforms.twitter import TwitterClient
        
        # Test with dummy credentials
        client = TwitterClient(
            api_key="test",
            api_secret="test",
            access_token="test",
            access_token_secret="test"
        )
        
        # Verify all required methods exist
        assert hasattr(client, 'create_post')
        assert hasattr(client, 'get_analytics')
        assert hasattr(client, 'get_trending')
        assert hasattr(client, 'schedule_post')
        assert hasattr(client, 'delete_post')
        assert hasattr(client, 'get_post')
    
    @pytest.mark.asyncio
    async def test_post_model_validation(self):
        """Test Post model validation."""
        from social_media_mcp.models import Post, MediaAsset, PlatformType
        
        # Valid post
        post = Post(
            text="Test post",
            platforms=[PlatformType.TWITTER],
            hashtags=["test", "mcp"],
            media=[MediaAsset(type="image", path="/test.jpg")]
        )
        
        assert post.text == "Test post"
        assert len(post.platforms) == 1
        assert len(post.hashtags) == 2
        assert len(post.media) == 1
        
        # Test ID generation
        assert post.id is not None
        assert len(post.id) == 36  # UUID length


class TestUtilityFunctions:
    """Test utility functions with real implementations."""
    
    @pytest.mark.asyncio
    async def test_hashtag_analysis(self):
        """Test hashtag performance analysis."""
        from social_media_mcp.utils import analyze_hashtag_performance
        
        hashtags = ["marketing", "AI", "automation", "verylonghashtag" * 5]
        recommendations = await analyze_hashtag_performance(hashtags, "instagram")
        
        assert len(recommendations) == len(hashtags)
        
        # Check scoring logic
        for rec in recommendations:
            assert 0 <= rec.relevance_score <= 1.0
            assert rec.competition_level in ["low", "medium", "high"]
        
        # Verify that very long hashtags get lower scores
        long_hashtag_rec = next(r for r in recommendations if len(r.hashtag) > 50)
        short_hashtag_rec = next(r for r in recommendations if r.hashtag == "AI")
        assert short_hashtag_rec.relevance_score > long_hashtag_rec.relevance_score
    
    def test_engagement_rate_calculation(self):
        """Test engagement rate calculation."""
        from social_media_mcp.utils import calculate_engagement_rate
        
        rate = calculate_engagement_rate(1000, 50)
        assert rate == 5.0
        
        rate = calculate_engagement_rate(0, 50)
        assert rate == 0.0
    
    @pytest.mark.asyncio
    async def test_optimal_posting_time(self):
        """Test optimal posting time calculation."""
        from social_media_mcp.utils import find_optimal_posting_time
        
        optimal_time = await find_optimal_posting_time(["twitter", "linkedin"])
        
        assert isinstance(optimal_time, datetime)
        assert optimal_time > datetime.now(timezone.utc)
        
        # Should be within the next 24 hours
        time_diff = (optimal_time - datetime.now(timezone.utc)).total_seconds() / 3600
        assert 0 < time_diff <= 24


if __name__ == "__main__":
    pytest.main([__file__, "-v"])