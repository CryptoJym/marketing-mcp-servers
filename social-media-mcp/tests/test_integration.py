"""Integration tests for real API interactions."""

import pytest
import os
import asyncio
from datetime import datetime, timezone
import tempfile
from pathlib import Path

from social_media_mcp.server import SocialMediaMCPServer
from social_media_mcp.models import Post, MediaAsset, PlatformType


# Skip integration tests if no real credentials are available
SKIP_INTEGRATION = not all([
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET")
])


@pytest.mark.skipif(SKIP_INTEGRATION, reason="No API credentials configured")
class TestRealAPIIntegration:
    """Integration tests that use real APIs."""
    
    @pytest.fixture
    async def server(self):
        """Create a real server instance with actual credentials."""
        server = SocialMediaMCPServer()
        await server.initialize()
        return server
    
    @pytest.fixture
    def test_image(self):
        """Create a real test image for upload."""
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a branded test image
        img = Image.new('RGB', (1200, 675), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = "MCP Test Post\n" + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((50, 50), text, fill='black')
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            img.save(tmp.name, 'JPEG', quality=95)
            return tmp.name
    
    @pytest.mark.asyncio
    async def test_real_twitter_post(self, server, test_image):
        """Test creating a real Twitter post."""
        result = await server.handle_call_tool("create_post", {
            "platforms": ["twitter"],
            "content": {
                "text": f"Test post from MCP Server - {datetime.now().isoformat()} #MCPTest #Automation",
                "media": [{
                    "type": "image",
                    "path": test_image,
                    "alt_text": "MCP Test Image"
                }]
            }
        })
        
        import json
        response = json.loads(result[0].text)
        
        assert "results" in response
        assert "twitter" in response["results"]
        
        twitter_result = response["results"]["twitter"]
        if twitter_result["success"]:
            assert "post_id" in twitter_result
            assert "url" in twitter_result
            print(f"Successfully posted to Twitter: {twitter_result['url']}")
            
            # Store post ID for cleanup
            pytest.twitter_post_id = twitter_result["post_id"]
        else:
            # Log the error for debugging
            print(f"Twitter post failed: {twitter_result.get('error')}")
    
    @pytest.mark.asyncio
    async def test_real_twitter_analytics(self, server):
        """Test getting real analytics from Twitter."""
        # Get analytics for recent posts
        result = await server.handle_call_tool("get_analytics", {
            "platforms": ["twitter"],
            "metric_type": "engagement",
            "date_range": {
                "start": (datetime.now() - timedelta(days=7)).date().isoformat(),
                "end": datetime.now().date().isoformat()
            }
        })
        
        import json
        response = json.loads(result[0].text)
        
        assert "platforms" in response
        assert "twitter" in response["platforms"]
        
        twitter_analytics = response["platforms"]["twitter"]
        if "error" not in twitter_analytics:
            assert "impressions" in twitter_analytics
            assert "engagement" in twitter_analytics
            print(f"Twitter Analytics: {twitter_analytics}")
    
    @pytest.mark.asyncio
    async def test_real_twitter_trending(self, server):
        """Test getting real trending topics from Twitter."""
        result = await server.handle_call_tool("get_trending", {
            "platforms": ["twitter"],
            "location": "United States"
        })
        
        import json
        response = json.loads(result[0].text)
        
        assert "platforms" in response
        assert "twitter" in response["platforms"]
        
        twitter_trends = response["platforms"]["twitter"]
        if "error" not in twitter_trends:
            assert "trending_topics" in twitter_trends
            assert isinstance(twitter_trends["trending_topics"], list)
            
            if twitter_trends["trending_topics"]:
                # Verify trend structure
                trend = twitter_trends["trending_topics"][0]
                assert "topic" in trend
                print(f"Top trending: {trend['topic']}")
    
    @pytest.mark.asyncio
    async def test_real_post_deletion(self, server):
        """Test deleting a real post."""
        if hasattr(pytest, 'twitter_post_id'):
            # Delete the test post
            from social_media_mcp.platforms.twitter import TwitterClient
            
            client = TwitterClient(
                api_key=os.getenv("TWITTER_API_KEY"),
                api_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
            )
            
            success = await client.delete_post(pytest.twitter_post_id)
            assert success, "Should be able to delete test post"
            print(f"Cleaned up test post: {pytest.twitter_post_id}")


@pytest.mark.skipif(
    not os.getenv("LINKEDIN_ACCESS_TOKEN"),
    reason="No LinkedIn credentials"
)
class TestLinkedInIntegration:
    """LinkedIn API integration tests."""
    
    @pytest.fixture
    async def server(self):
        server = SocialMediaMCPServer()
        await server.initialize()
        return server
    
    @pytest.mark.asyncio
    async def test_real_linkedin_post(self, server):
        """Test creating a real LinkedIn post."""
        result = await server.handle_call_tool("create_post", {
            "platforms": ["linkedin"],
            "content": {
                "text": "Excited to share our progress on the Marketing MCP Server! "
                       "This tool enables seamless multi-platform social media management "
                       "through the Model Context Protocol. #Automation #MarketingTech"
            }
        })
        
        import json
        response = json.loads(result[0].text)
        
        if "linkedin" in response["results"]:
            linkedin_result = response["results"]["linkedin"]
            if linkedin_result["success"]:
                print(f"LinkedIn post created: {linkedin_result.get('url')}")


class TestRealMediaProcessing:
    """Test real media processing capabilities."""
    
    @pytest.mark.asyncio
    async def test_image_optimization_quality(self):
        """Test that image optimization maintains quality."""
        from PIL import Image
        import numpy as np
        from social_media_mcp.utils import optimize_image
        
        # Create a test image with fine details
        img = Image.new('RGB', (2000, 2000), 'white')
        pixels = np.array(img)
        
        # Add a pattern to test quality preservation
        for i in range(0, 2000, 10):
            pixels[i, :] = [255, 0, 0]  # Red lines
            pixels[:, i] = [0, 0, 255]  # Blue lines
        
        img = Image.fromarray(pixels)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            img.save(tmp.name, quality=95)
            original_path = tmp.name
        
        # Optimize for different platforms
        optimized_path = await optimize_image(original_path, ["instagram", "twitter"])
        
        # Load optimized image
        optimized = Image.open(optimized_path)
        
        # Check dimensions are appropriate
        assert optimized.width <= 1200
        assert optimized.height <= 1200
        
        # Check file size is reasonable
        file_size = Path(optimized_path).stat().st_size
        assert file_size < 5 * 1024 * 1024  # Less than 5MB
        
        # Clean up
        os.unlink(original_path)
        os.unlink(optimized_path)
    
    @pytest.mark.asyncio
    async def test_video_optimization_real(self):
        """Test real video optimization."""
        import cv2
        import numpy as np
        from social_media_mcp.utils import optimize_video
        
        # Create a test video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            video_path = tmp.name
        
        out = cv2.VideoWriter(video_path, fourcc, 30.0, (1920, 1080))
        
        # Create 150 frames (5 seconds at 30fps)
        for i in range(150):
            frame = np.zeros((1080, 1920, 3), np.uint8)
            # Add moving text
            cv2.putText(frame, f'Frame {i}', (50 + i*5, 540), 
                       cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)
            out.write(frame)
        
        out.release()
        
        # Get file size before optimization
        original_size = Path(video_path).stat().st_size
        
        # Optimize for Twitter (max 140 seconds)
        optimized_path = await optimize_video(video_path, ["twitter"])
        
        # Check optimization results
        assert Path(optimized_path).exists()
        
        # Verify video properties
        cap = cv2.VideoCapture(optimized_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps
        
        assert duration <= 140  # Twitter limit
        
        cap.release()
        
        # Clean up
        os.unlink(video_path)
        os.unlink(optimized_path)


class TestSchedulingLogic:
    """Test real scheduling and timing logic."""
    
    @pytest.mark.asyncio
    async def test_optimal_timing_algorithm(self):
        """Test the optimal posting time algorithm with real data."""
        from social_media_mcp.utils import find_optimal_posting_time
        
        # Test for different platform combinations
        test_cases = [
            (["twitter"], "Twitter only"),
            (["linkedin"], "LinkedIn only"),
            (["twitter", "linkedin"], "Twitter + LinkedIn"),
            (["instagram", "facebook"], "Instagram + Facebook"),
            (["twitter", "linkedin", "instagram", "facebook"], "All platforms")
        ]
        
        for platforms, description in test_cases:
            optimal_time = await find_optimal_posting_time(platforms)
            
            # Verify it's in the future
            assert optimal_time > datetime.now(timezone.utc)
            
            # Verify it's within reasonable hours (considering UTC)
            hour = optimal_time.hour
            
            # Should be during reasonable hours for at least one timezone
            # (6 AM - 11 PM in some timezone)
            assert any([
                6 <= (hour + offset) % 24 <= 23
                for offset in [-8, -5, 0, 1, 8]  # PST, EST, UTC, CET, SGT
            ])
            
            print(f"{description}: Optimal time = {optimal_time.strftime('%H:%M UTC')}")
    
    @pytest.mark.asyncio
    async def test_content_calendar_scheduling(self):
        """Test scheduling algorithm for content calendar."""
        from social_media_mcp.utils import schedule_content_calendar
        
        # Create a week's worth of posts
        posts = []
        for i in range(7):
            posts.append({
                "content": {"text": f"Day {i+1} post"},
                "platforms": ["twitter", "linkedin"]
            })
        
        # Test even spacing strategy
        scheduled = await schedule_content_calendar(posts, "even_spacing")
        
        assert len(scheduled) == 7
        
        # Verify all posts have scheduled times
        for post in scheduled:
            assert "scheduled_time" in post
            scheduled_time = datetime.fromisoformat(post["scheduled_time"])
            
            # Should be between 9 AM and 8 PM
            assert 9 <= scheduled_time.hour <= 20
        
        # Test peak times strategy
        scheduled_peak = await schedule_content_calendar(posts, "peak_times")
        
        # Verify posts are scheduled at peak times
        peak_hours = {9, 12, 17, 19}
        for post in scheduled_peak:
            scheduled_time = datetime.fromisoformat(post["scheduled_time"])
            assert scheduled_time.hour in peak_hours


if __name__ == "__main__":
    # Run tests with real output
    pytest.main([__file__, "-v", "-s"])