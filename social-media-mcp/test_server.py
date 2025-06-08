#!/usr/bin/env python3
"""Test script for Social Media MCP Server."""

import asyncio
import os
import sys
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from social_media_mcp.server import SocialMediaMCPServer


async def test_server():
    """Test basic server functionality."""
    print("🚀 Testing Social Media MCP Server...")
    
    # Create server instance
    server = SocialMediaMCPServer()
    await server.initialize()
    
    # Test listing tools
    print("\n📋 Available tools:")
    tools = await server.handle_list_tools()
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test creating a simple post
    print("\n📝 Testing post creation...")
    test_args = {
        "platforms": ["twitter"],
        "content": {
            "text": "Test post from Social Media MCP Server! 🚀",
            "hashtags": ["test", "mcp", "automation"]
        }
    }
    
    try:
        result = await server.handle_call_tool("create_post", test_args)
        print("Result:", result[0].text)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test hashtag generation
    print("\n🏷️ Testing hashtag generation...")
    hashtag_args = {
        "content": "Launching our new AI-powered marketing automation platform",
        "platform": "instagram",
        "max_hashtags": 5
    }
    
    try:
        result = await server.handle_call_tool("generate_hashtags", hashtag_args)
        print("Generated hashtags:", result[0].text)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✅ Server test complete!")


if __name__ == "__main__":
    # Set dummy environment variables for testing
    if not os.getenv("TWITTER_API_KEY"):
        print("⚠️  No Twitter credentials found. Using test mode.")
        os.environ["TWITTER_API_KEY"] = "test_key"
        os.environ["TWITTER_API_SECRET"] = "test_secret"
        os.environ["TWITTER_ACCESS_TOKEN"] = "test_token"
        os.environ["TWITTER_ACCESS_SECRET"] = "test_secret"
    
    asyncio.run(test_server())