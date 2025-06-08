"""Pytest configuration for Social Media MCP tests."""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables if not present."""
    # Only set dummy values if real ones aren't present
    test_env = {
        "TWITTER_API_KEY": "test_api_key",
        "TWITTER_API_SECRET": "test_api_secret", 
        "TWITTER_ACCESS_TOKEN": "test_access_token",
        "TWITTER_ACCESS_SECRET": "test_access_secret",
        "LINKEDIN_ACCESS_TOKEN": "test_linkedin_token",
        "INSTAGRAM_ACCESS_TOKEN": "test_instagram_token",
        "INSTAGRAM_BUSINESS_ID": "test_business_id",
        "FACEBOOK_ACCESS_TOKEN": "test_facebook_token",
        "FACEBOOK_PAGE_ID": "test_page_id"
    }
    
    for key, value in test_env.items():
        if not os.getenv(key):
            monkeypatch.setenv(key, value)


@pytest.fixture
def temp_media_dir(tmp_path):
    """Create a temporary directory for media files."""
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    return media_dir


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", 
        "integration: mark test as integration test (requires real API credentials)"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running"
    )