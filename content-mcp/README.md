# Content Management MCP Server

An AI-powered MCP server for creating, managing, and optimizing marketing content across all formats and channels.

## Features

- **AI Content Generation**: Create blog posts, social media copy, emails, and more
- **Brand Voice Consistency**: Ensure all content matches your brand guidelines
- **Content Library**: Centralized repository for all marketing assets
- **Version Control**: Track changes and manage content iterations
- **Collaboration**: Multi-user editing and approval workflows
- **Performance Tracking**: Monitor content performance metrics

## Installation

```bash
pip install -e .
```

## Configuration

Set the following environment variables:

```bash
# AI Model Configuration
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Content Storage
export CONTENT_STORAGE_PATH="/path/to/content/library"
export DATABASE_URL="postgresql://user:pass@localhost/content_db"

# Brand Guidelines
export BRAND_VOICE_CONFIG="/path/to/brand_voice.json"
```

## Available Tools

### generate_content
Generate various types of marketing content.

```python
await mcp.call_tool("generate_content", {
    "type": "blog_post",
    "topic": "10 AI Marketing Trends for 2024",
    "keywords": ["AI marketing", "marketing automation", "personalization"],
    "tone": "professional",
    "length": 1500,
    "include_seo": true,
    "brand_voice": true
})
```

### optimize_content
Optimize existing content for better performance.

```python
await mcp.call_tool("optimize_content", {
    "content_id": "blog_12345",
    "optimization_goals": ["seo", "readability", "engagement"],
    "target_audience": "marketing professionals",
    "preserve_voice": true
})
```

### manage_library
Manage content library operations.

```python
await mcp.call_tool("manage_library", {
    "action": "search",
    "filters": {
        "type": "blog_post",
        "tags": ["ai", "marketing"],
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        }
    },
    "sort_by": "performance_score"
})
```

### create_variations
Generate content variations for A/B testing.

```python
await mcp.call_tool("create_variations", {
    "original_content": "Your AI marketing assistant is here",
    "variation_count": 5,
    "variation_type": "headline",
    "optimization_goal": "click_through_rate"
})
```

### check_brand_consistency
Ensure content aligns with brand guidelines.

```python
await mcp.call_tool("check_brand_consistency", {
    "content": "Check out this awesome deal!",
    "content_type": "social_post",
    "suggest_improvements": true
})
```

### translate_content
Translate content for international markets.

```python
await mcp.call_tool("translate_content", {
    "content_id": "email_campaign_001",
    "target_languages": ["es", "fr", "de"],
    "maintain_tone": true,
    "localize": true
})
```

## Content Types Supported

### Written Content
- Blog Posts & Articles
- Social Media Posts
- Email Campaigns
- Landing Page Copy
- Ad Copy (Search, Display, Social)
- Press Releases
- Case Studies
- White Papers

### Visual Content Templates
- Social Media Graphics
- Infographics
- Email Headers
- Banner Ads
- Presentation Slides

### Content Formats
- Long-form (1000+ words)
- Short-form (< 500 words)
- Microcopy (CTAs, tooltips)
- Video Scripts
- Podcast Outlines

## Brand Voice Configuration

Create a `brand_voice.json` file:

```json
{
  "tone": {
    "primary": "professional",
    "secondary": "approachable",
    "avoid": ["slang", "jargon"]
  },
  "vocabulary": {
    "preferred": ["innovative", "solution", "transform"],
    "avoid": ["cheap", "deal", "buy now"]
  },
  "style": {
    "sentence_length": "medium",
    "paragraph_length": 3-5,
    "active_voice": true
  }
}
```

## Content Performance Metrics

- **Engagement Rate**: Likes, shares, comments
- **Read Time**: Average time spent
- **Conversion Rate**: Actions taken
- **SEO Performance**: Rankings, traffic
- **Sentiment Score**: Reader perception

## Workflow Integration

The server supports content workflows:

1. **Ideation**: AI-powered topic suggestions
2. **Creation**: Generate initial drafts
3. **Review**: Automated quality checks
4. **Approval**: Multi-level approval process
5. **Publishing**: Direct integration with CMS
6. **Analysis**: Performance tracking

## Best Practices

1. **Define Clear Guidelines**: Set up comprehensive brand voice rules
2. **Use Templates**: Create reusable content templates
3. **Regular Updates**: Keep brand guidelines current
4. **Version Control**: Track all content changes
5. **Performance Review**: Regularly analyze content metrics

## License

MIT License - see LICENSE file for details.