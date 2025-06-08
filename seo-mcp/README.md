# SEO Tools MCP Server

A powerful MCP server for search engine optimization, providing keyword research, site audits, competitor analysis, and performance tracking.

## Features

- **Keyword Research**: Discover high-value keywords and search intent
- **On-Page SEO**: Optimize content and meta tags
- **Technical SEO**: Site audits and performance analysis
- **Backlink Analysis**: Monitor and analyze link profiles
- **Competitor Tracking**: Monitor competitor SEO strategies
- **SERP Monitoring**: Track rankings and SERP features

## Installation

```bash
pip install -e .
```

## Configuration

Set the following environment variables:

```bash
# Google APIs
export GOOGLE_SEARCH_CONSOLE_CREDENTIALS="/path/to/credentials.json"
export GOOGLE_CUSTOM_SEARCH_API_KEY="your-api-key"
export GOOGLE_CUSTOM_SEARCH_CX="your-search-engine-id"

# SEO Tool APIs (optional)
export SEMRUSH_API_KEY="your-api-key"
export AHREFS_API_KEY="your-api-key"
export MOZ_ACCESS_ID="your-access-id"
export MOZ_SECRET_KEY="your-secret-key"

# Site Analysis
export SITE_URL="https://yoursite.com"
```

## Available Tools

### keyword_research
Discover and analyze keywords for SEO opportunities.

```python
await mcp.call_tool("keyword_research", {
    "seed_keywords": ["ai marketing", "marketing automation"],
    "location": "United States",
    "language": "en",
    "include_metrics": {
        "search_volume": true,
        "difficulty": true,
        "cpc": true,
        "trend": true,
        "serp_features": true
    },
    "num_suggestions": 50,
    "include_questions": true,
    "include_related": true
})
```

### analyze_page_seo
Analyze on-page SEO factors for a specific page.

```python
await mcp.call_tool("analyze_page_seo", {
    "url": "https://example.com/blog/ai-marketing-guide",
    "target_keyword": "AI marketing",
    "checks": [
        "title_tag", "meta_description", "headings",
        "keyword_density", "content_length", "readability",
        "internal_links", "external_links", "images",
        "schema_markup", "page_speed"
    ]
})
```

### technical_audit
Perform a comprehensive technical SEO audit.

```python
await mcp.call_tool("technical_audit", {
    "domain": "example.com",
    "crawl_depth": 3,
    "checks": [
        "crawlability", "indexability", "sitemap",
        "robots_txt", "https", "mobile_friendly",
        "page_speed", "core_web_vitals", "structured_data",
        "duplicate_content", "broken_links", "redirects"
    ],
    "export_format": "detailed_report"
})
```

### track_rankings
Monitor keyword rankings across search engines.

```python
await mcp.call_tool("track_rankings", {
    "domain": "example.com",
    "keywords": [
        "ai marketing tools",
        "marketing automation software",
        "best email marketing platform"
    ],
    "search_engines": ["google", "bing"],
    "locations": ["United States", "United Kingdom"],
    "device_types": ["desktop", "mobile"],
    "track_serp_features": true,
    "track_competitors": ["competitor1.com", "competitor2.com"]
})
```

### analyze_backlinks
Analyze backlink profile and opportunities.

```python
await mcp.call_tool("analyze_backlinks", {
    "domain": "example.com",
    "metrics": [
        "total_backlinks", "referring_domains",
        "domain_authority", "anchor_text_distribution",
        "follow_vs_nofollow", "link_quality"
    ],
    "find_opportunities": true,
    "analyze_competitors": ["competitor1.com", "competitor2.com"],
    "toxic_link_check": true
})
```

### content_optimization
Optimize content for target keywords.

```python
await mcp.call_tool("content_optimization", {
    "content": "Your article text here...",
    "target_keyword": "AI marketing strategy",
    "secondary_keywords": ["machine learning", "personalization"],
    "optimizations": {
        "keyword_placement": true,
        "semantic_keywords": true,
        "content_gaps": true,
        "readability": true,
        "structure": true
    },
    "competitor_analysis": true
})
```

### generate_schema
Generate structured data markup.

```python
await mcp.call_tool("generate_schema", {
    "page_type": "article",
    "data": {
        "headline": "10 AI Marketing Trends for 2024",
        "author": "Jane Doe",
        "datePublished": "2024-01-15",
        "description": "Discover the latest AI marketing trends...",
        "image": "https://example.com/image.jpg"
    },
    "additional_types": ["organization", "breadcrumb"]
})
```

### local_seo_audit
Analyze local SEO performance.

```python
await mcp.call_tool("local_seo_audit", {
    "business_name": "Acme Marketing Agency",
    "address": "123 Main St, San Francisco, CA",
    "check_listings": [
        "google_my_business", "bing_places",
        "apple_maps", "yelp", "facebook"
    ],
    "analyze_reviews": true,
    "check_citations": true,
    "local_keywords": ["marketing agency san francisco"]
})
```

## SEO Metrics Provided

### Keyword Metrics
- Monthly search volume
- Keyword difficulty (0-100)
- Cost per click (CPC)
- Search trends
- SERP features present
- Search intent classification

### Page Metrics
- Title tag optimization
- Meta description quality
- Heading structure (H1-H6)
- Content quality score
- Keyword density
- Page load speed
- Mobile friendliness
- Core Web Vitals

### Domain Metrics
- Domain authority
- Page authority
- Trust flow
- Citation flow
- Organic traffic estimates
- Indexed pages
- Crawl errors

### Backlink Metrics
- Total backlinks
- Referring domains
- Link quality score
- Anchor text distribution
- Follow vs nofollow ratio
- New/lost links

## SERP Features Tracked

- Featured snippets
- People Also Ask
- Knowledge panels
- Local pack
- Image pack
- Video carousel
- News results
- Shopping results
- Sitelinks

## Content Optimization

### On-Page Factors
1. **Title Tags**: 50-60 characters
2. **Meta Descriptions**: 150-160 characters
3. **URLs**: Short, keyword-rich
4. **Headings**: Logical H1-H6 structure
5. **Content**: Comprehensive, E-A-T focused

### Technical Factors
1. **Page Speed**: < 3 seconds load time
2. **Mobile**: Responsive design
3. **HTTPS**: SSL certificate required
4. **XML Sitemap**: Updated regularly
5. **Robots.txt**: Properly configured

## Competitor Analysis Features

- Keyword gap analysis
- Content gap identification
- Backlink opportunities
- SERP feature targeting
- Technical SEO comparison

## Reporting Formats

- **Dashboard**: Real-time metrics
- **PDF Reports**: Branded, shareable
- **CSV Export**: Raw data access
- **API Access**: Integration ready
- **Alerts**: Email/Slack notifications

## Best Practices

1. **Focus on Intent**: Match content to search intent
2. **E-A-T**: Expertise, Authoritativeness, Trustworthiness
3. **Core Web Vitals**: Prioritize user experience
4. **Mobile-First**: Design for mobile users
5. **Local SEO**: Optimize for local searches
6. **Regular Audits**: Monthly technical checks

## License

MIT License - see LICENSE file for details.