# Social Media MCP Server

A comprehensive MCP server for managing social media presence across multiple platforms including Twitter/X, LinkedIn, Instagram, and Facebook.

## Features

- **Multi-Platform Posting**: Create and schedule posts across all major social platforms
- **Media Optimization**: Automatically optimize images and videos for each platform
- **Analytics Tracking**: Monitor engagement, reach, and performance metrics
- **Hashtag Generation**: AI-powered hashtag recommendations
- **Content Calendar**: Manage and schedule posts with optimal timing
- **Trending Topics**: Track trending topics and hashtags

## Installation

```bash
pip install -e .
```

## Configuration

Set the following environment variables for the platforms you want to use:

### Twitter/X
```bash
export TWITTER_API_KEY="your-api-key"
export TWITTER_API_SECRET="your-api-secret"
export TWITTER_ACCESS_TOKEN="your-access-token"
export TWITTER_ACCESS_SECRET="your-access-secret"
```

### LinkedIn
```bash
export LINKEDIN_ACCESS_TOKEN="your-access-token"
```

### Instagram
```bash
export INSTAGRAM_ACCESS_TOKEN="your-access-token"
export INSTAGRAM_BUSINESS_ID="your-business-account-id"
```

### Facebook
```bash
export FACEBOOK_ACCESS_TOKEN="your-page-access-token"
export FACEBOOK_PAGE_ID="your-page-id"
```

## MCP Client Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "social-media": {
      "command": "python",
      "args": ["-m", "social_media_mcp"],
      "env": {
        "TWITTER_API_KEY": "${TWITTER_API_KEY}",
        "TWITTER_API_SECRET": "${TWITTER_API_SECRET}",
        "TWITTER_ACCESS_TOKEN": "${TWITTER_ACCESS_TOKEN}",
        "TWITTER_ACCESS_SECRET": "${TWITTER_ACCESS_SECRET}",
        "LINKEDIN_ACCESS_TOKEN": "${LINKEDIN_ACCESS_TOKEN}",
        "INSTAGRAM_ACCESS_TOKEN": "${INSTAGRAM_ACCESS_TOKEN}",
        "INSTAGRAM_BUSINESS_ID": "${INSTAGRAM_BUSINESS_ID}",
        "FACEBOOK_ACCESS_TOKEN": "${FACEBOOK_ACCESS_TOKEN}",
        "FACEBOOK_PAGE_ID": "${FACEBOOK_PAGE_ID}"
      }
    }
  }
}
```

## Available Tools

### create_post
Create and publish a post to one or more platforms.

```python
await mcp.call_tool("create_post", {
    "platforms": ["twitter", "linkedin"],
    "content": {
        "text": "Exciting news! Our new product launches today! 🚀",
        "media": [{
            "type": "image",
            "path": "/path/to/image.jpg",
            "alt_text": "Product launch graphic"
        }],
        "hashtags": ["productlaunch", "innovation", "tech"]
    },
    "optimize_timing": true
})
```

### get_analytics
Retrieve analytics data for posts and accounts.

```python
await mcp.call_tool("get_analytics", {
    "platforms": ["twitter", "instagram"],
    "metric_type": "engagement",
    "date_range": {
        "start": "2024-01-01",
        "end": "2024-01-31"
    }
})
```

### schedule_posts
Schedule multiple posts with optimal spacing.

```python
await mcp.call_tool("schedule_posts", {
    "posts": [
        {
            "platforms": ["twitter"],
            "content": {"text": "Morning motivation! ☀️"},
            "schedule": "2024-12-25T09:00:00Z"
        },
        {
            "platforms": ["linkedin"],
            "content": {"text": "Industry insights..."},
            "schedule": "2024-12-25T14:00:00Z"
        }
    ],
    "optimize_spacing": true
})
```

### generate_hashtags
Generate relevant hashtags based on content.

```python
await mcp.call_tool("generate_hashtags", {
    "content": "Launching our AI-powered marketing platform",
    "platform": "instagram",
    "max_hashtags": 15,
    "include_trending": true
})
```

### optimize_media
Optimize images and videos for social platforms.

```python
await mcp.call_tool("optimize_media", {
    "media_path": "/path/to/large-image.png",
    "platforms": ["twitter", "instagram"],
    "media_type": "image"
})
```

### get_trending
Get trending topics and hashtags.

```python
await mcp.call_tool("get_trending", {
    "platforms": ["twitter"],
    "category": "technology",
    "location": "United States"
})
```

### manage_calendar
Manage content calendar and scheduled posts.

```python
await mcp.call_tool("manage_calendar", {
    "action": "view",
    "date_range": {
        "start": "2024-12-01",
        "end": "2024-12-31"
    }
})
```

## Media Specifications

The server automatically optimizes media according to platform requirements:

### Twitter/X
- **Images**: Max 5MB, up to 4096x4096px
- **Videos**: Max 512MB, up to 140 seconds
- **Formats**: JPG, PNG, GIF, WEBP (images), MP4, MOV (videos)

### Instagram
- **Images**: Max 8MB, 320x320 to 1080x1350px
- **Videos**: Max 100MB, up to 60 seconds (feed)
- **Aspect Ratios**: 1:1, 4:5, 1.91:1

### LinkedIn
- **Images**: Max 10MB, 552x276 to 4000x4000px
- **Videos**: Max 5GB, up to 10 minutes
- **Formats**: JPG, PNG, GIF (images), MP4, AVI, MOV (videos)

### Facebook
- **Images**: Max 4MB, min 200x200px
- **Videos**: Max 4GB, up to 240 minutes
- **Recommended**: 1200x630px for images

## Best Practices

1. **Hashtags**:
   - Twitter: 1-2 hashtags
   - Instagram: 10-30 hashtags
   - LinkedIn: 3-5 hashtags
   - Facebook: 1-3 hashtags

2. **Posting Times** (UTC):
   - Twitter: 9am, 12pm, 3pm, 5pm, 8pm
   - Instagram: 11am, 1pm, 5pm, 7pm
   - LinkedIn: 7am, 10am, 12pm, 5pm
   - Facebook: 9am, 1pm, 3pm, 7pm

3. **Content Length**:
   - Twitter: 280 characters
   - Instagram: 2,200 characters
   - LinkedIn: 3,000 characters
   - Facebook: 63,206 characters

## Error Handling

The server provides detailed error messages for common issues:
- Invalid API credentials
- Rate limiting
- Media file issues
- Platform-specific errors

## Development

### Running Tests
```bash
pytest tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.