#!/usr/bin/env python3
"""
Test the complete marketing MCP servers setup.

This script verifies that all components are properly installed and configured.
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path
import json


def check_python_version():
    """Check Python version is 3.8+."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (need 3.8+)")
        return False


def check_directory_structure():
    """Verify directory structure is correct."""
    print("\nChecking directory structure...")
    
    expected_dirs = [
        "social-media-mcp",
        "social-media-mcp/src",
        "social-media-mcp/src/social_media_mcp",
        "social-media-mcp/src/social_media_mcp/platforms",
        "social-media-mcp/tests",
        "social-media-mcp/examples",
        "social-media-mcp/docs"
    ]
    
    all_exist = True
    for dir_path in expected_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} missing")
            all_exist = False
    
    return all_exist


def check_dependencies():
    """Check if key dependencies can be imported."""
    print("\nChecking dependencies...")
    
    dependencies = [
        ("mcp", "MCP Protocol"),
        ("tweepy", "Twitter API"),
        ("pydantic", "Data validation"),
        ("PIL", "Image processing"),
        ("cv2", "Video processing"),
        ("pytest", "Testing framework"),
        ("httpx", "HTTP client")
    ]
    
    all_imported = True
    for module, name in dependencies:
        try:
            importlib.import_module(module)
            print(f"✅ {name} ({module})")
        except ImportError:
            print(f"❌ {name} ({module}) - not installed")
            all_imported = False
    
    return all_imported


def check_environment_variables():
    """Check if API credentials are configured."""
    print("\nChecking environment variables...")
    
    env_vars = {
        "Twitter": [
            "TWITTER_API_KEY",
            "TWITTER_API_SECRET",
            "TWITTER_ACCESS_TOKEN",
            "TWITTER_ACCESS_SECRET"
        ],
        "LinkedIn": ["LINKEDIN_ACCESS_TOKEN"],
        "Instagram": ["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ID"],
        "Facebook": ["FACEBOOK_ACCESS_TOKEN", "FACEBOOK_PAGE_ID"]
    }
    
    configured_platforms = []
    
    for platform, vars in env_vars.items():
        all_set = all(os.getenv(var) for var in vars)
        if all_set:
            print(f"✅ {platform} configured")
            configured_platforms.append(platform)
        else:
            missing = [var for var in vars if not os.getenv(var)]
            print(f"⚠️  {platform} not configured (missing: {', '.join(missing)})")
    
    return len(configured_platforms) > 0


def test_server_import():
    """Test that the server can be imported."""
    print("\nTesting server import...")
    
    try:
        # Add to path
        sys.path.insert(0, str(Path("social-media-mcp/src")))
        
        from social_media_mcp.server import SocialMediaMCPServer
        from social_media_mcp.models import Post, MediaAsset
        from social_media_mcp.utils import generate_hashtags
        
        print("✅ Server modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def run_basic_tests():
    """Run basic unit tests."""
    print("\nRunning basic tests...")
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "social-media-mcp/tests/test_server.py::TestUtilityFunctions", "-v"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Basic tests passed")
            return True
        else:
            print("❌ Some tests failed")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Could not run tests: {e}")
        return False


def check_mcp_config():
    """Check if MCP configuration is valid."""
    print("\nChecking MCP configuration...")
    
    config_path = Path("mcp-config.json")
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            if "mcpServers" in config and "social-media" in config["mcpServers"]:
                print("✅ MCP configuration found")
                return True
            else:
                print("⚠️  MCP configuration incomplete")
                return False
        except Exception as e:
            print(f"❌ Invalid configuration: {e}")
            return False
    else:
        print("⚠️  No mcp-config.json found (will be created by setup.sh)")
        return True


def main():
    """Run all checks."""
    print("🔍 Marketing MCP Servers Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Directory Structure", check_directory_structure),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_environment_variables),
        ("Server Import", test_server_import),
        ("Basic Tests", run_basic_tests),
        ("MCP Configuration", check_mcp_config)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{'='*50}")
        result = check_func()
        results.append((name, result))
    
    print(f"\n{'='*50}")
    print("\n📊 Summary:")
    print("-" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<25} {status}")
    
    print("-" * 30)
    print(f"Total: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Set up API credentials in .env file")
        print("2. Run: python social-media-mcp/test_server.py")
        print("3. Configure your MCP client with mcp-config.json")
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
        print("\nTroubleshooting:")
        print("1. Run: ./setup.sh to install dependencies")
        print("2. Check README.md for configuration instructions")
        print("3. Ensure you're in the correct directory")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())