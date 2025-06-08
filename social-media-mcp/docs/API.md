# Social Media MCP Server API Reference

## Overview

The Social Media MCP Server provides a unified interface for managing multiple social media platforms through the Model Context Protocol.

## Authentication

Each platform requires specific authentication credentials set as environment variables:

### Twitter/X
- `TWITTER_API_KEY` - API Key from Twitter Developer Portal
- `TWITTER_API_SECRET` - API Secret
- `TWITTER_ACCESS_TOKEN` - Access Token for your account
- `TWITTER_ACCESS_SECRET` - Access Token Secret

### LinkedIn
- `LINKEDIN_ACCESS_TOKEN` - OAuth 2.0 Access Token

### Instagram
- `INSTAGRAM_ACCESS_TOKEN` - Facebook Graph API Access Token
- `INSTAGRAM_BUSINESS_ID` - Instagram Business Account ID

### Facebook
- `FACEBOOK_ACCESS_TOKEN` - Page Access Token
- `FACEBOOK_PAGE_ID` - Facebook Page ID

## Tools

### create_post

Create and publish a post to one or more social media platforms.

**Parameters:**
```typescript
{
  platforms: string[];  // ["twitter", "linkedin", "instagram", "facebook"]
  content: {
    text: string;      // Post content (required)
    media?: {
      type: "image" | "video";
      path: string;    // Local file path
      alt_text?: string;
    }[];
    hashtags?: string[];  // Without # prefix
    mentions?: string[];  // Without @ prefix
  };
  schedule?: string;   // ISO 8601 datetime
  optimize_timing?: boolean;  // Auto-select best posting time
}
```

**Response:**
```typescript
{
  results: {
    [platform: string]: {
      success: boolean;
      post_id?: string;
      url?: string;
      error?: string;
      scheduled_time?: string;
    }
  };
  content: {
    text: string;
    hashtags: string[];
    media_count: number;
  };
}
```

**Example:**
```python
result = await mcp.call_tool("social-media", "create_post", {
    "platforms": ["twitter", "linkedin"],
    "content": {
        "text": "Exciting announcement coming soon!",
        "hashtags": ["announcement", "exciting"],
        "media": [{
            "type": "image",
            "path": "/path/to/image.jpg",
            "alt_text": "Teaser image"
        }]
    },
    "optimize_timing": True
})
```

### get_analytics

Retrieve analytics data for posts and accounts.

**Parameters:**
```typescript
{
  platforms: string[];
  metric_type?: "engagement" | "reach" | "impressions" | "clicks" | "conversions";
  date_range?: {
    start: string;  // YYYY-MM-DD
    end: string;    // YYYY-MM-DD
  };
  post_ids?: string[];  // Specific post IDs to analyze
}
```

**Response:**
```typescript
{
  platforms: {
    [platform: string]: {
      impressions?: number;
      engagement?: number;
      clicks?: number;
      shares?: number;
      comments?: number;
      likes?: number;
      reach?: number;
      conversions?: number;
      engagement_rate?: number;
      error?: string;
    }
  };
  aggregated: {
    total_impressions: number;
    total_engagement: number;
    engagement_rate: number;
  };
}
```

### schedule_posts

Schedule multiple posts with optional timing optimization.

**Parameters:**
```typescript
{
  posts: Array<{
    platforms: string[];
    content: {
      text: string;
      media?: Media[];
      hashtags?: string[];
    };
    schedule?: string;  // ISO 8601
  }>;
  optimize_spacing?: boolean;  // Automatically space posts
}
```

**Response:**
```typescript
{
  scheduled_count: number;
  results: Array<{
    results: {
      [platform: string]: {
        success: boolean;
        scheduled_time?: string;
        error?: string;
      }
    }
  }>;
}
```

### generate_hashtags

Generate relevant hashtags based on content and trends.

**Parameters:**
```typescript
{
  content: string;  // Post content to analyze
  platform?: string;  // Target platform
  max_hashtags?: number;  // Maximum hashtags to generate
  include_trending?: boolean;  // Include trending hashtags
}
```

**Response:**
```typescript
{
  hashtags: string[];
  count: number;
  platform: string;
}
```

### optimize_media

Optimize images and videos for social media platforms.

**Parameters:**
```typescript
{
  media_path: string;  // Path to media file
  platforms: string[];  // Target platforms
  media_type: "image" | "video";
}
```

**Response:**
```typescript
{
  original_path: string;
  optimized: {
    [platform: string]: {
      path?: string;
      success: boolean;
      error?: string;
    }
  };
}
```

### get_trending

Get trending topics and hashtags.

**Parameters:**
```typescript
{
  platforms: string[];
  category?: string;  // Filter by category
  location?: string;  // Geographic location
}
```

**Response:**
```typescript
{
  platforms: {
    [platform: string]: {
      trending_topics?: Array<{
        topic: string;
        volume?: number;
        url?: string;
      }>;
      error?: string;
    }
  };
  timestamp: string;
}
```

### manage_calendar

Manage content calendar and scheduled posts.

**Parameters:**
```typescript
{
  action: "view" | "update" | "delete" | "reschedule";
  date_range?: {
    start: string;  // YYYY-MM-DD
    end: string;    // YYYY-MM-DD
  };
  post_ids?: string[];  // For update/delete actions
}
```

**Response:**
```typescript
{
  scheduled_posts?: Array<{
    id: string;
    platform: string;
    scheduled_time: string;
    content: string;  // Truncated preview
    media_count: number;
    hashtags: string[];
  }>;
  total_count?: number;
  action: string;
  deleted_count?: number;
}
```

## Platform-Specific Features

### Twitter/X
- Character limit: 280
- Media: Up to 4 images or 1 video per tweet
- Video limits: 2:20 duration, 512MB
- Threads: Not yet supported (coming soon)

### LinkedIn
- Character limit: 3,000
- Best for B2B content
- Supports articles and documents
- Company page posting available

### Instagram
- Character limit: 2,200
- Hashtag limit: 30
- Stories and Reels: Coming soon
- Shopping tags: Coming soon

### Facebook
- Character limit: 63,206
- Supports various media types
- Event creation: Coming soon
- Audience targeting: Coming soon

## Error Handling

All tools return errors in a consistent format:

```typescript
{
  error: string;  // Error message
  tool: string;   // Tool that failed
  platform?: string;  // Platform where error occurred
}
```

Common error codes:
- `rate_limit`: API rate limit exceeded
- `auth_failed`: Authentication failed
- `invalid_media`: Media file invalid or too large
- `platform_error`: Platform-specific error

## Rate Limits

The server automatically handles rate limiting for each platform:

- **Twitter**: 300 posts/3 hours
- **LinkedIn**: 100 posts/day
- **Instagram**: 25 posts/day
- **Facebook**: No strict limit

## Best Practices

1. **Always optimize media** before posting for best quality and engagement
2. **Use platform-appropriate hashtags** - fewer for Twitter, more for Instagram
3. **Schedule posts during peak hours** for your audience
4. **Monitor analytics regularly** to optimize your strategy
5. **Test content variations** to see what works best

## Webhooks

Coming soon: Real-time notifications for comments, mentions, and engagement.

## Examples

See the [examples directory](../examples/) for complete usage examples.