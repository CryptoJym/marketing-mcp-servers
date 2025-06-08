# Analytics MCP Server

A powerful MCP server for comprehensive marketing analytics across multiple channels including web, social media, email, and paid advertising.

## Features

- **Multi-Channel Analytics**: Aggregate data from Google Analytics, Adobe Analytics, Mixpanel, and more
- **Custom Dashboards**: Create and manage personalized analytics dashboards
- **ROI Tracking**: Calculate return on investment across campaigns
- **A/B Testing**: Analyze test results and statistical significance
- **Competitor Analysis**: Track competitor performance metrics
- **Automated Reporting**: Generate and distribute reports automatically

## Installation

```bash
pip install -e .
```

## Configuration

Set the following environment variables:

### Google Analytics 4
```bash
export GA4_PROPERTY_ID="your-property-id"
export GA4_CREDENTIALS_PATH="/path/to/credentials.json"
```

### Adobe Analytics
```bash
export ADOBE_CLIENT_ID="your-client-id"
export ADOBE_CLIENT_SECRET="your-client-secret"
export ADOBE_COMPANY_ID="your-company-id"
```

### Mixpanel
```bash
export MIXPANEL_TOKEN="your-project-token"
export MIXPANEL_API_SECRET="your-api-secret"
```

### Amplitude
```bash
export AMPLITUDE_API_KEY="your-api-key"
export AMPLITUDE_SECRET_KEY="your-secret-key"
```

## Available Tools

### generate_report
Generate comprehensive analytics reports across channels.

```python
await mcp.call_tool("generate_report", {
    "metrics": ["sessions", "conversions", "revenue", "bounce_rate"],
    "channels": ["organic", "paid", "social", "email"],
    "date_range": {
        "start": "2024-01-01",
        "end": "2024-01-31"
    },
    "format": "dashboard",
    "comparison_period": "previous_month"
})
```

### track_roi
Calculate ROI for marketing campaigns.

```python
await mcp.call_tool("track_roi", {
    "campaign_id": "holiday_2024",
    "include_channels": ["google_ads", "facebook_ads", "email"],
    "attribution_model": "data_driven",
    "cost_data": {
        "google_ads": 5000,
        "facebook_ads": 3000,
        "email": 500
    }
})
```

### analyze_ab_test
Analyze A/B test results with statistical significance.

```python
await mcp.call_tool("analyze_ab_test", {
    "test_name": "homepage_cta_test",
    "control_group": "variant_a",
    "test_groups": ["variant_b", "variant_c"],
    "metrics": ["conversion_rate", "average_order_value"],
    "confidence_level": 0.95
})
```

### competitor_benchmark
Compare performance against competitors.

```python
await mcp.call_tool("competitor_benchmark", {
    "competitors": ["competitor1.com", "competitor2.com"],
    "metrics": ["traffic", "engagement", "market_share"],
    "channels": ["organic_search", "paid_search", "social"],
    "period": "last_quarter"
})
```

### create_dashboard
Create custom analytics dashboards.

```python
await mcp.call_tool("create_dashboard", {
    "name": "Executive Marketing Dashboard",
    "widgets": [
        {
            "type": "line_chart",
            "metric": "revenue",
            "dimension": "date",
            "period": "last_30_days"
        },
        {
            "type": "pie_chart",
            "metric": "sessions",
            "dimension": "channel",
            "period": "last_30_days"
        },
        {
            "type": "scorecard",
            "metric": "conversion_rate",
            "comparison": "previous_period"
        }
    ],
    "refresh_interval": "daily"
})
```

### forecast_metrics
Predict future performance based on historical data.

```python
await mcp.call_tool("forecast_metrics", {
    "metrics": ["revenue", "conversions", "traffic"],
    "forecast_period": 90,  # days
    "seasonality": true,
    "include_confidence_intervals": true
})
```

## Metrics Available

### Web Analytics
- Sessions, Users, Pageviews
- Bounce Rate, Session Duration
- Goal Completions, E-commerce Revenue
- Device & Browser Breakdowns
- Geographic Data

### Social Media
- Impressions, Reach, Engagement
- Follower Growth
- Share of Voice
- Sentiment Analysis

### Email Marketing
- Open Rate, Click Rate
- Conversion Rate
- List Growth
- Revenue per Email

### Paid Advertising
- Impressions, Clicks, CTR
- CPC, CPM, CPA
- ROAS (Return on Ad Spend)
- Quality Score

## Report Formats

1. **Dashboard**: Interactive web dashboard
2. **PDF**: Formatted PDF reports
3. **Excel**: Detailed data exports
4. **Email**: HTML email summaries
5. **API**: JSON data for integration

## Attribution Models

- **Last Click**: Credit to final touchpoint
- **First Click**: Credit to first touchpoint
- **Linear**: Equal credit distribution
- **Time Decay**: Recent touches weighted more
- **Data-Driven**: ML-based attribution

## Best Practices

1. **Data Sampling**: Be aware of sampling in large datasets
2. **Privacy Compliance**: Respect GDPR, CCPA regulations
3. **Data Freshness**: Understand platform data delays
4. **Metric Definitions**: Ensure consistent definitions across platforms
5. **Segmentation**: Use appropriate user segments for analysis

## License

MIT License - see LICENSE file for details.