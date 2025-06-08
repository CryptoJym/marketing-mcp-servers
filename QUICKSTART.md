# Marketing MCP Servers - Quick Start Guide

Get your marketing automation up and running in minutes!

## 🚀 5-Minute Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/marketing-mcp-servers.git
cd marketing-mcp-servers
```

### 2. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure API Keys
```bash
cp .env.template .env
# Edit .env with your API credentials
```

### 4. Test Your Setup
```bash
cd social-media-mcp
python test_server.py
```

## 🔑 Getting API Keys

### Twitter/X
1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Create a new app
3. Generate API keys and access tokens

### LinkedIn
1. Visit [linkedin.com/developers](https://www.linkedin.com/developers)
2. Create an app
3. Request Marketing Developer Platform access

### Instagram
1. Use [Facebook Developer Console](https://developers.facebook.com)
2. Create app with Instagram Basic Display
3. Add Instagram Business Account

### Facebook
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create app
3. Generate Page Access Token

## 📝 Your First Post

### Using with Claude Desktop or Any MCP Client

1. Add to your MCP client config:
```json
{
  "mcpServers": {
    "social-media": {
      "command": "python",
      "args": ["-m", "social_media_mcp"],
      "cwd": "/path/to/marketing-mcp-servers/social-media-mcp"
    }
  }
}
```

2. Create your first post:
```python
# In your MCP client
await use_mcp_tool("social-media", "create_post", {
    "platforms": ["twitter"],
    "content": {
        "text": "Hello from Marketing MCP! 🚀"
    }
})
```

## 🎯 Common Use Cases

### 1. Morning Social Media Update
```python
# Post to all platforms
await use_mcp_tool("social-media", "create_post", {
    "platforms": ["twitter", "linkedin", "instagram", "facebook"],
    "content": {
        "text": "Good morning! Here's today's marketing tip...",
        "media": [{
            "type": "image",
            "path": "/path/to/tip-graphic.png"
        }]
    },
    "optimize_timing": true
})
```

### 2. Schedule Week's Content
```python
# Schedule posts for the week
posts = [
    {"content": {"text": "Monday Motivation"}, "schedule": "2024-01-15T09:00:00Z"},
    {"content": {"text": "Tech Tuesday"}, "schedule": "2024-01-16T09:00:00Z"},
    # ... more posts
]

await use_mcp_tool("social-media", "schedule_posts", {
    "posts": posts,
    "platforms": ["twitter", "linkedin"],
    "optimize_spacing": true
})
```

### 3. Track Campaign Performance
```python
# Get analytics for your campaign
analytics = await use_mcp_tool("social-media", "get_analytics", {
    "platforms": ["twitter", "instagram"],
    "date_range": {
        "start": "2024-01-01",
        "end": "2024-01-07"
    }
})
```

## 🔧 Troubleshooting

### "Platform not configured"
- Check that you've set all required environment variables
- Verify API credentials are correct
- Ensure you've activated the virtual environment

### "Media upload failed"
- Check file size limits (varies by platform)
- Verify file format is supported
- Ensure file path is correct

### "Rate limit exceeded"
- Wait before making more requests
- Consider upgrading API access tier
- Use scheduling to spread out posts

## 🎓 Next Steps

1. **Explore Other Servers**: Try analytics-mcp, content-mcp, etc.
2. **Integrate with A2A**: Connect agents for advanced automation
3. **Build Workflows**: Create multi-step marketing campaigns
4. **Monitor Performance**: Use analytics to optimize strategy

## 📚 Resources

- [Full Documentation](./README.md)
- [Integration Guide](./INTEGRATION_GUIDE.md)
- [API Reference](./docs/API.md)
- [Examples](./examples/)

## 💬 Get Help

- GitHub Issues: Report bugs or request features
- Discord: Join our community
- Email: support@example.com

Happy Marketing! 🚀