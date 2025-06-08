"""Utility functions for social media operations."""

import os
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple
import hashlib
from pathlib import Path
import logging
import aiofiles
import asyncio

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
import numpy as np
import httpx
from collections import Counter
import json

from .models import PlatformType, HashtagRecommendation

logger = logging.getLogger(__name__)


# Platform-specific media requirements
PLATFORM_MEDIA_SPECS = {
    PlatformType.TWITTER: {
        "image": {
            "max_size_mb": 5,
            "formats": ["jpg", "jpeg", "png", "gif", "webp"],
            "max_dimensions": (4096, 4096),
            "aspect_ratios": [(16, 9), (1, 1)]  # Recommended
        },
        "video": {
            "max_size_mb": 512,
            "formats": ["mp4", "mov"],
            "max_duration_seconds": 140,
            "max_dimensions": (1920, 1200),
            "min_dimensions": (32, 32)
        }
    },
    PlatformType.INSTAGRAM: {
        "image": {
            "max_size_mb": 8,
            "formats": ["jpg", "jpeg", "png"],
            "aspect_ratios": [(1, 1), (4, 5), (1.91, 1)],
            "min_dimensions": (320, 320),
            "max_dimensions": (1080, 1350)
        },
        "video": {
            "max_size_mb": 100,
            "formats": ["mp4", "mov"],
            "max_duration_seconds": 60,  # For feed posts
            "aspect_ratios": [(1, 1), (4, 5), (16, 9)]
        }
    },
    PlatformType.LINKEDIN: {
        "image": {
            "max_size_mb": 10,
            "formats": ["jpg", "jpeg", "png", "gif"],
            "min_dimensions": (552, 276),
            "max_dimensions": (4000, 4000)
        },
        "video": {
            "max_size_mb": 5000,  # 5GB
            "formats": ["mp4", "avi", "mov"],
            "max_duration_seconds": 600,  # 10 minutes
            "aspect_ratios": [(16, 9), (1, 1), (9, 16)]
        }
    },
    PlatformType.FACEBOOK: {
        "image": {
            "max_size_mb": 4,
            "formats": ["jpg", "jpeg", "png", "gif", "tiff", "bmp"],
            "min_dimensions": (200, 200),
            "recommended_dimensions": (1200, 630)
        },
        "video": {
            "max_size_mb": 4000,  # 4GB
            "formats": ["mp4", "mov"],
            "max_duration_seconds": 240,  # 4 minutes for most
            "aspect_ratios": [(16, 9), (9, 16), (1, 1)]
        }
    }
}


async def optimize_image(image_path: str, platforms: List[str]) -> str:
    """Optimize image for specified platforms."""
    try:
        img = Image.open(image_path)
        
        # Get the most restrictive requirements across platforms
        max_size_mb = min(
            PLATFORM_MEDIA_SPECS[PlatformType(p)]["image"]["max_size_mb"]
            for p in platforms
        )
        
        # Find best dimensions that work for all platforms
        target_width = 1080  # Good default for most platforms
        target_height = 1080
        
        # Resize if needed
        if img.width > target_width or img.height > target_height:
            img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
            
        # Convert to RGB if necessary (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
            
        # Save optimized image
        output_path = f"{Path(image_path).stem}_optimized.jpg"
        quality = 85
        
        # Reduce quality until file size is acceptable
        while True:
            img.save(output_path, "JPEG", quality=quality, optimize=True)
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            
            if file_size_mb <= max_size_mb or quality <= 20:
                break
                
            quality -= 5
            
        return output_path
        
    except Exception as e:
        raise Exception(f"Image optimization failed: {str(e)}")


async def optimize_video(video_path: str, platforms: List[str]) -> str:
    """Optimize video for specified platforms."""
    try:
        video = mp.VideoFileClip(video_path)
        
        # Get the most restrictive requirements
        max_duration = min(
            PLATFORM_MEDIA_SPECS[PlatformType(p)]["video"]["max_duration_seconds"]
            for p in platforms
        )
        
        # Trim video if needed
        if video.duration > max_duration:
            video = video.subclip(0, max_duration)
            
        # Resize for optimal dimensions
        target_width = 1280
        target_height = 720
        
        if video.w > target_width or video.h > target_height:
            video = video.resize(width=target_width)
            
        # Save optimized video
        output_path = f"{Path(video_path).stem}_optimized.mp4"
        video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            bitrate="2000k"
        )
        
        video.close()
        return output_path
        
    except Exception as e:
        raise Exception(f"Video optimization failed: {str(e)}")


async def generate_hashtags(
    content: str,
    platform: str,
    max_count: int = 10,
    include_trending: bool = True
) -> List[str]:
    """Generate relevant hashtags for content."""
    hashtags = []
    
    # Extract existing hashtags from content
    existing_hashtags = re.findall(r'#\w+', content)
    hashtags.extend([tag[1:] for tag in existing_hashtags])
    
    # Extract important words (simplified NLP)
    # In production, use proper NLP libraries
    words = re.findall(r'\b\w{4,}\b', content.lower())
    word_freq = Counter(words)
    
    # Get most common words as potential hashtags
    common_words = [word for word, _ in word_freq.most_common(5)]
    
    # Platform-specific hashtag strategies
    if platform == "instagram":
        # Instagram allows up to 30 hashtags
        max_count = min(max_count, 30)
        # Add niche and broad hashtags
        hashtags.extend(common_words)
        
    elif platform == "twitter":
        # Twitter best practice is 1-2 hashtags
        max_count = min(max_count, 3)
        hashtags.extend(common_words[:2])
        
    elif platform == "linkedin":
        # LinkedIn works well with 3-5 hashtags
        max_count = min(max_count, 5)
        # Professional hashtags
        hashtags.extend(common_words[:3])
        
    # Remove duplicates and limit count
    hashtags = list(dict.fromkeys(hashtags))[:max_count]
    
    return hashtags


async def find_optimal_posting_time(platforms: List[str]) -> datetime:
    """Find optimal posting time based on platform best practices."""
    now = datetime.now(timezone.utc)
    
    # Best posting times by platform (simplified)
    best_times = {
        "twitter": [9, 12, 15, 17, 20],  # Hours in UTC
        "instagram": [11, 13, 17, 19],
        "linkedin": [7, 10, 12, 17],
        "facebook": [9, 13, 15, 19]
    }
    
    # Find next best time across all platforms
    all_times = set()
    for platform in platforms:
        if platform in best_times:
            all_times.update(best_times[platform])
            
    if not all_times:
        # Default to next hour
        return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
    # Find next available time
    current_hour = now.hour
    future_times = [t for t in sorted(all_times) if t > current_hour]
    
    if future_times:
        next_hour = future_times[0]
        return now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
    else:
        # Next day, first available time
        next_hour = min(all_times)
        return (now + timedelta(days=1)).replace(
            hour=next_hour, minute=0, second=0, microsecond=0
        )


async def analyze_hashtag_performance(
    hashtags: List[str],
    platform: str
) -> List[HashtagRecommendation]:
    """Analyze hashtag performance and recommendations."""
    recommendations = []
    
    # This is a simplified implementation
    # In production, integrate with hashtag analytics APIs
    
    for hashtag in hashtags:
        # Simple scoring based on hashtag characteristics
        score = 0.5  # Base score
        
        # Length scoring
        if 5 <= len(hashtag) <= 15:
            score += 0.2
            
        # Not too generic
        generic_tags = ["love", "instagood", "photooftheday", "beautiful", "happy"]
        if hashtag.lower() not in generic_tags:
            score += 0.2
            
        # Platform-specific adjustments
        if platform == "instagram" and len(hashtag) < 20:
            score += 0.1
        elif platform == "twitter" and len(hashtag) < 15:
            score += 0.1
            
        recommendations.append(HashtagRecommendation(
            hashtag=hashtag,
            relevance_score=min(score, 1.0),
            competition_level="medium",  # Would need real data
            trending=False  # Would need real trending data
        ))
        
    # Sort by relevance score
    recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return recommendations


def calculate_engagement_rate(
    impressions: int,
    engagements: int
) -> float:
    """Calculate engagement rate."""
    if impressions == 0:
        return 0.0
    return (engagements / impressions) * 100


def format_caption_with_mentions(
    caption: str,
    mentions: List[str],
    platform: str
) -> str:
    """Format caption with proper mention syntax for platform."""
    mention_prefix = "@"
    
    # Add mentions to caption
    if mentions:
        if platform == "instagram":
            # Instagram mentions can be in caption or comments
            mention_text = " ".join(f"{mention_prefix}{m}" for m in mentions)
            caption = f"{caption}\n\n{mention_text}"
        elif platform == "twitter":
            # Twitter mentions at the beginning
            mention_text = " ".join(f"{mention_prefix}{m}" for m in mentions)
            caption = f"{mention_text} {caption}"
        else:
            # LinkedIn and Facebook
            mention_text = " ".join(f"{mention_prefix}{m}" for m in mentions)
            caption = f"{caption}\n\n{mention_text}"
            
    return caption


def validate_post_content(
    content: str,
    platform: str
) -> Tuple[bool, Optional[str]]:
    """Validate post content for platform requirements."""
    # Character limits by platform
    char_limits = {
        "twitter": 280,
        "instagram": 2200,
        "linkedin": 3000,
        "facebook": 63206
    }
    
    limit = char_limits.get(platform, 5000)
    
    if len(content) > limit:
        return False, f"Content exceeds {platform} character limit ({len(content)} > {limit})"
        
    # Check for platform-specific requirements
    if platform == "instagram" and not re.search(r'#\w+', content):
        # Warning, not error
        return True, "Instagram posts typically perform better with hashtags"
        
    return True, None


async def schedule_content_calendar(
    posts: List[Dict],
    strategy: str = "even_spacing"
) -> List[Dict]:
    """Schedule posts according to strategy."""
    scheduled_posts = []
    
    if strategy == "even_spacing":
        # Space posts evenly throughout the day
        start_hour = 9  # 9 AM
        end_hour = 20   # 8 PM
        
        total_hours = end_hour - start_hour
        if len(posts) > 0:
            interval = total_hours / len(posts)
            
            for i, post in enumerate(posts):
                hour = start_hour + int(i * interval)
                scheduled_time = datetime.now(timezone.utc).replace(
                    hour=hour, minute=0, second=0, microsecond=0
                )
                
                if scheduled_time < datetime.now(timezone.utc):
                    # Move to tomorrow
                    scheduled_time += timedelta(days=1)
                    
                post["scheduled_time"] = scheduled_time.isoformat()
                scheduled_posts.append(post)
                
    elif strategy == "peak_times":
        # Schedule at peak engagement times
        peak_times = [9, 12, 17, 19]  # Simplified peak times
        
        for i, post in enumerate(posts):
            time_index = i % len(peak_times)
            hour = peak_times[time_index]
            
            scheduled_time = datetime.now(timezone.utc).replace(
                hour=hour, minute=0, second=0, microsecond=0
            )
            
            if scheduled_time < datetime.now(timezone.utc):
                # Move to tomorrow
                scheduled_time += timedelta(days=1)
                
            # If multiple posts at same time, space by days
            if i >= len(peak_times):
                days_offset = i // len(peak_times)
                scheduled_time += timedelta(days=days_offset)
                
            post["scheduled_time"] = scheduled_time.isoformat()
            scheduled_posts.append(post)
            
    return scheduled_posts