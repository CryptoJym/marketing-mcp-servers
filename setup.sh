#!/bin/bash

# Marketing MCP Servers Setup Script

echo "🚀 Setting up Marketing MCP Servers..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

if ! command_exists pip; then
    echo -e "${RED}Error: pip is not installed${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install base dependencies
echo -e "${BLUE}Installing base dependencies...${NC}"
pip install --upgrade pip
pip install mcp

# Install each server
SERVERS=("social-media-mcp")

for server in "${SERVERS[@]}"; do
    echo -e "${BLUE}Setting up $server...${NC}"
    cd "$server"
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    if [ -f "pyproject.toml" ]; then
        pip install -e .
    fi
    
    cd ..
    echo -e "${GREEN}✓ $server setup complete${NC}"
done

# Create environment template
echo -e "${BLUE}Creating environment template...${NC}"
cat > .env.template << 'EOF'
# Social Media MCP
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
LINKEDIN_ACCESS_TOKEN=
INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_BUSINESS_ID=
FACEBOOK_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=

# Analytics MCP
GA4_PROPERTY_ID=
GA4_CREDENTIALS_PATH=
ADOBE_CLIENT_ID=
ADOBE_CLIENT_SECRET=
ADOBE_COMPANY_ID=
MIXPANEL_TOKEN=
MIXPANEL_API_SECRET=
AMPLITUDE_API_KEY=
AMPLITUDE_SECRET_KEY=

# Content MCP
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
CONTENT_STORAGE_PATH=./content
DATABASE_URL=postgresql://user:pass@localhost/content_db
BRAND_VOICE_CONFIG=./brand_voice.json

# Email MCP
SENDGRID_API_KEY=
MAILCHIMP_API_KEY=
MAILCHIMP_SERVER_PREFIX=
SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=true

# SEO MCP
GOOGLE_SEARCH_CONSOLE_CREDENTIALS=
GOOGLE_CUSTOM_SEARCH_API_KEY=
GOOGLE_CUSTOM_SEARCH_CX=
SEMRUSH_API_KEY=
AHREFS_API_KEY=
MOZ_ACCESS_ID=
MOZ_SECRET_KEY=
SITE_URL=
EOF

# Create MCP client configuration template
echo -e "${BLUE}Creating MCP client configuration...${NC}"
cat > mcp-config.json << 'EOF'
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
    },
    "analytics": {
      "command": "python",
      "args": ["-m", "analytics_mcp"],
      "env": {
        "GA4_PROPERTY_ID": "${GA4_PROPERTY_ID}",
        "GA4_CREDENTIALS_PATH": "${GA4_CREDENTIALS_PATH}",
        "ADOBE_CLIENT_ID": "${ADOBE_CLIENT_ID}",
        "ADOBE_CLIENT_SECRET": "${ADOBE_CLIENT_SECRET}",
        "MIXPANEL_TOKEN": "${MIXPANEL_TOKEN}",
        "AMPLITUDE_API_KEY": "${AMPLITUDE_API_KEY}"
      }
    },
    "content": {
      "command": "python",
      "args": ["-m", "content_mcp"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "CONTENT_STORAGE_PATH": "${CONTENT_STORAGE_PATH}",
        "DATABASE_URL": "${DATABASE_URL}"
      }
    },
    "email": {
      "command": "python",
      "args": ["-m", "email_mcp"],
      "env": {
        "SENDGRID_API_KEY": "${SENDGRID_API_KEY}",
        "MAILCHIMP_API_KEY": "${MAILCHIMP_API_KEY}",
        "MAILCHIMP_SERVER_PREFIX": "${MAILCHIMP_SERVER_PREFIX}"
      }
    },
    "seo": {
      "command": "python",
      "args": ["-m", "seo_mcp"],
      "env": {
        "GOOGLE_SEARCH_CONSOLE_CREDENTIALS": "${GOOGLE_SEARCH_CONSOLE_CREDENTIALS}",
        "GOOGLE_CUSTOM_SEARCH_API_KEY": "${GOOGLE_CUSTOM_SEARCH_API_KEY}",
        "SITE_URL": "${SITE_URL}"
      }
    }
  }
}
EOF

# Create example brand voice configuration
echo -e "${BLUE}Creating brand voice template...${NC}"
cat > brand_voice.json << 'EOF'
{
  "tone": {
    "primary": "professional",
    "secondary": "approachable",
    "avoid": ["slang", "excessive_jargon", "aggressive_sales"]
  },
  "vocabulary": {
    "preferred": ["innovative", "solution", "transform", "empower"],
    "avoid": ["cheap", "deal", "buy now", "limited time"]
  },
  "style": {
    "sentence_length": "medium",
    "paragraph_length": "3-5",
    "active_voice": true,
    "oxford_comma": true
  },
  "personality": {
    "traits": ["knowledgeable", "helpful", "forward-thinking"],
    "voice": "We are your trusted partner in marketing innovation"
  }
}
EOF

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env and fill in your API credentials"
echo "2. Review and customize brand_voice.json for your brand"
echo "3. Add mcp-config.json to your MCP client configuration"
echo "4. Start using the Marketing MCP Servers!"
echo ""
echo "For detailed documentation, see README.md in each server directory"