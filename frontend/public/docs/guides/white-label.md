---
sidebar_position: 3
title: White-Label Solution
---

# White-Label Solution

Chronos Studio provides comprehensive white-label capabilities, allowing you to rebrand and resell the platform under your own brand.

## Overview

White-label Chronos Studio enables you to:
- Use your own branding (logo, colors, domain)
- Offer AI agents as part of your product
- Set custom pricing and packages
- Control the user experience
- Maintain customer relationships

## Getting Started

### Requirements
- Business entity
- Custom domain
- Logo and brand assets
- Legal agreements

### Activation
White-label is available on Enterprise plans. Contact sales to enable.

## Branding Configuration

### Custom Domain

```bash
# Configure custom domain
chronos white-label set-domain \
  --domain agents.yourcompany.com \
  --ssl true
```

### DNS Configuration

Add these records to your DNS:

| Type | Host | Value |
|------|------|-------|
| CNAME | agents | yourcompany.chronos.studio |
| TXT | _acme-challenge.agents | verification-token |

### Brand Assets

```bash
# Upload logo
chronos white-label upload-logo \
  --light /path/to/logo-light.png \
  --dark /path/to/logo-dark.png

# Set brand colors
chronos white-label set-colors \
  --primary "#0066FF" \
  --secondary "#00CC66" \
  --accent "#FF6600" \
  --background "#FFFFFF" \
  --text "#333333"
```

### Email Templates

Customize transactional emails:

```bash
chronos white-label customize-emails \
  --welcome /path/to/welcome.html \
  --reset-password /path/to/reset.html \
  --invoice /path/to/invoice.html
```

## Dashboard Customization

### UI Configuration

```json
{
  "white_label": {
    "enabled": true,
    "company_name": "Acme AI",
    "company_url": "https://acme.ai",
    "support_email": "support@acme.ai",
    
    "dashboard": {
      "title": "Acme AI Studio",
      "favicon": "/assets/favicon.ico",
      "login_background": "/assets/login-bg.jpg"
    },
    
    "chat_widget": {
      "company_name": "Acme Support",
      "welcome_message": "Hi! How can Acme help you?",
      "colors": {
        "primary": "#0066FF",
        "secondary": "#00CC66"
      }
    }
  }
}
```

### Custom CSS

```css
/* custom-styles.css */
.dashboard-header {
  background: linear-gradient(135deg, #0066FF, #00CC66);
}

.chat-message.agent {
  background: #E8F4FF;
  border-left: 4px solid #0066FF;
}

.btn-primary {
  background: #0066FF;
  border-radius: 8px;
}
```

## Agent Customization

### Agent Personality

```python
# Create branded agent
agent = client.agents.create(
    name="Acme Assistant",
    config={
        "system_prompt": """
        You are Acme Assistant, created by Acme AI.
        Represent Acme professionally.
        Never mention Chronos or other third parties.
        """,
        "response_style": {
            "format": "friendly",
            "signature": "Best regards,\nAcme AI Team"
        }
    }
)
```

### Chat Widget

Embed a branded chat widget:

```html
<!-- Acme AI Chat Widget -->
<script>
  window.acmeConfig = {
    agent: 'agent_abc123',
    brand: {
      name: 'Acme AI',
      logo: 'https://acme.ai/logo.png',
      colors: {
        primary: '#0066FF',
        text: '#333333'
      }
    },
    greeting: "Welcome to Acme AI! How can I help?",
    position: 'bottom-right'
  };
</script>
<script src="https://acme.ai/widget.js"></script>
```

## Multi-Tenant Architecture

### Organization Management

```bash
# Create sub-organizations
chronos orgs create \
  --name "Customer A" \
  --plan "pro" \
  --custom_domain "ai.customera.com"

chronos orgs create \
  --name "Customer B" \
  --plan "enterprise" \
  --dedicated_hosting true
```

### Isolated Data

Each white-label customer gets:
- Isolated database
- Dedicated API endpoints
- Separate analytics
- Custom configurations

## Billing & Invoicing

### Custom Pricing

```bash
# Set custom pricing for white-label customer
chronos billing set-pricing \
  --org_id org_abc123 \
  --base_price 499 \
  --per_agent_price 49 \
  --included_agents 5 \
  --overage_rate 79
```

### Invoice Customization

```json
{
  "invoice": {
    "from": "Your Company\n123 Business St\nCity, ST 12345",
    "tax_id": "XX-XXXXXXX",
    "notes": "Thank you for your business!",
    "payment_terms": "Net 30"
  }
}
```

## API Access

### White-Label API

```bash
# API requests go through your domain
curl -X GET https://agents.yourcompany.com/api/v1/agents \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Customer API Keys

```bash
# Create API keys for your customers
chronos api-keys create \
  --org_id org_customer \
  --name "Customer Production" \
  --scopes "agents:read,agents:write,tools:manage"
```

## Security & Compliance

### Data Isolation

- SOC 2 Type II certified
- GDPR compliant
- Data residency options
- Encryption at rest and in transit

### Custom SSL

```bash
# Upload custom certificate
chronos ssl upload \
  --domain agents.yourcompany.com \
  --cert /path/to/cert.pem \
  --key /path/to/key.pem \
  --ca /path/to/ca.pem
```

## Monitoring & Analytics

### White-Label Analytics

```bash
# View across all white-label customers
chronos analytics white-label \
  --date_range "last_30_days" \
  --metrics "agents,conversions,revenue"
```

### Customer Reports

```bash
# Generate customer report
chronos reports generate \
  --org_id org_customer \
  --type "monthly_usage" \
  --format pdf \
  --email customer@example.com
```

## Support

### Customer Support

Configure support channels:

```bash
chronos white-label set-support \
  --email support@yourcompany.com \
  --phone "+1-800-555-0100" \
  --hours "Mon-Fri 9am-6pm EST"
```

### Escalation

```bash
chronos white-label set-escalation \
  --tickets_endpoint "https://yourcompany.com/api/tickets"
```

## Best Practices

1. **Consistent branding** - Apply to all touchpoints
2. **Clear pricing** - Transparent costs for customers
3. **Dedicated support** - Maintain customer relationships
4. **Regular updates** - Keep customers informed
5. **Monitor usage** - Track and optimize
