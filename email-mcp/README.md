# Email Marketing MCP Server

A comprehensive MCP server for email marketing automation, campaign management, and subscriber engagement.

## Features

- **Campaign Management**: Create, schedule, and manage email campaigns
- **List Management**: Segment and manage subscriber lists
- **Personalization**: Dynamic content and merge tags
- **A/B Testing**: Test subject lines, content, and send times
- **Automation**: Drip campaigns and triggered emails
- **Analytics**: Detailed performance metrics and reporting

## Installation

```bash
pip install -e .
```

## Configuration

Set the following environment variables:

### SendGrid
```bash
export SENDGRID_API_KEY="your-api-key"
```

### Mailchimp
```bash
export MAILCHIMP_API_KEY="your-api-key"
export MAILCHIMP_SERVER_PREFIX="us1"  # Your datacenter
```

### Custom SMTP
```bash
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-username"
export SMTP_PASSWORD="your-password"
export SMTP_USE_TLS="true"
```

## Available Tools

### create_campaign
Create and configure email campaigns.

```python
await mcp.call_tool("create_campaign", {
    "name": "Holiday Sale 2024",
    "subject": "🎁 Exclusive Holiday Deals Inside!",
    "from_name": "Your Brand",
    "from_email": "hello@yourbrand.com",
    "reply_to": "support@yourbrand.com",
    "list_id": "list_12345",
    "template_id": "holiday_template_v2",
    "personalization": {
        "use_first_name": true,
        "dynamic_content": {
            "vip_customers": "vip_content_block",
            "regular_customers": "regular_content_block"
        }
    }
})
```

### send_campaign
Send or schedule email campaigns.

```python
await mcp.call_tool("send_campaign", {
    "campaign_id": "camp_12345",
    "send_time": "2024-12-20T10:00:00Z",
    "timezone": "America/New_York",
    "segment": {
        "conditions": [
            {"field": "last_purchase", "operator": "within", "value": "30_days"},
            {"field": "engagement", "operator": "equals", "value": "high"}
        ]
    }
})
```

### manage_subscribers
Manage email subscribers and lists.

```python
await mcp.call_tool("manage_subscribers", {
    "action": "add",
    "list_id": "list_12345",
    "subscribers": [
        {
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "tags": ["prospect", "webinar_attendee"],
            "custom_fields": {
                "company": "Acme Corp",
                "role": "Marketing Manager"
            }
        }
    ],
    "update_existing": true
})
```

### create_automation
Set up automated email sequences.

```python
await mcp.call_tool("create_automation", {
    "name": "Welcome Series",
    "trigger": "subscriber_added",
    "list_id": "list_12345",
    "emails": [
        {
            "delay": "immediate",
            "subject": "Welcome to {{company_name}}!",
            "template": "welcome_email_1"
        },
        {
            "delay": "3_days",
            "subject": "Getting started with {{product_name}}",
            "template": "welcome_email_2"
        },
        {
            "delay": "7_days",
            "subject": "Your exclusive offer",
            "template": "welcome_email_3",
            "condition": {"field": "opened_email_2", "value": true}
        }
    ]
})
```

### test_campaign
Run A/B tests on campaigns.

```python
await mcp.call_tool("test_campaign", {
    "campaign_id": "camp_12345",
    "test_type": "subject_line",
    "variants": [
        {"name": "A", "subject": "Limited Time: 50% Off Everything"},
        {"name": "B", "subject": "Flash Sale - Half Price on All Items"},
        {"name": "C", "subject": "{{first_name}}, your exclusive 50% discount"}
    ],
    "test_size": 0.3,  # 30% of list
    "winner_criteria": "open_rate",
    "test_duration_hours": 4
})
```

### get_campaign_analytics
Retrieve detailed campaign performance data.

```python
await mcp.call_tool("get_campaign_analytics", {
    "campaign_id": "camp_12345",
    "metrics": [
        "opens", "unique_opens", "open_rate",
        "clicks", "unique_clicks", "click_rate",
        "unsubscribes", "bounces", "spam_reports"
    ],
    "include_link_clicks": true,
    "include_geographic_data": true,
    "include_device_data": true
})
```

### create_template
Create reusable email templates.

```python
await mcp.call_tool("create_template", {
    "name": "Product Announcement",
    "html": "<html>...</html>",
    "text": "Plain text version...",
    "variables": ["product_name", "product_image", "cta_link"],
    "sections": {
        "hero": "editable",
        "features": "repeatable",
        "footer": "locked"
    }
})
```

## Email Types Supported

### Transactional Emails
- Welcome emails
- Password resets
- Order confirmations
- Shipping notifications
- Account updates

### Marketing Emails
- Newsletters
- Promotional campaigns
- Product announcements
- Event invitations
- Survey requests

### Automated Sequences
- Onboarding series
- Abandoned cart recovery
- Re-engagement campaigns
- Birthday/anniversary emails
- Post-purchase follow-ups

## Personalization Features

### Dynamic Content
- First name, last name
- Company information
- Purchase history
- Behavioral data
- Geographic location
- Device preferences

### Smart Segmentation
- Demographics
- Engagement level
- Purchase behavior
- Email preferences
- Custom attributes

## Deliverability Features

- **SPF/DKIM Setup**: Authentication configuration
- **IP Warming**: Gradual sending for new IPs
- **Bounce Handling**: Automatic list cleaning
- **Spam Testing**: Pre-send spam score analysis
- **Engagement Tracking**: Monitor sender reputation

## Analytics & Reporting

### Campaign Metrics
- Open rate & unique opens
- Click rate & unique clicks
- Conversion tracking
- Revenue attribution
- Device & client analysis
- Geographic performance

### List Health Metrics
- Growth rate
- Engagement trends
- Churn analysis
- Segment performance
- Quality scoring

## Best Practices

1. **Permission-Based**: Always use double opt-in
2. **Mobile Optimization**: 60%+ emails opened on mobile
3. **Subject Lines**: Keep under 50 characters
4. **Send Times**: Test for your audience
5. **Frequency**: Balance engagement with fatigue
6. **Unsubscribe**: Make it easy and clear

## Compliance

The server includes features for:
- GDPR compliance
- CAN-SPAM compliance
- CASL compliance
- Unsubscribe management
- Data retention policies

## License

MIT License - see LICENSE file for details.