---
sidebar_position: 4
title: "Guide: White-Label Solutions"
---

# Guide: White-Label Solutions

Deploy Chronos-powered agents under your own brand for your clients.

## What Is White-Labeling?

White-labeling lets you:
- Remove all Chronos branding
- Use your own domain, logo, and colors
- Resell agent capabilities to your clients
- Manage multiple client deployments from one account

## Setup

### Configure Your Brand

```yaml
# white-label.yaml
brand:
  name: "YourCompany AI"
  domain: ai.yourcompany.com
  logo: ./assets/logo.svg
  favicon: ./assets/favicon.ico
  colors:
    primary: "#FF6B35"
    secondary: "#004E89"
    background: "#FFFFFF"
  support_email: support@yourcompany.com
```

### Deploy Custom Domain

```bash
chronos white-label setup \
  --domain ai.yourcompany.com \
  --config white-label.yaml
```

### Create Client Workspaces

```python
from chronos import ChronosClient

client = ChronosClient(api_key="your_key")

# Create a workspace for each client
workspace = client.workspaces.create(
    name="Client ABC",
    brand="yourcompany-ai",
    limits={
        "agents": 5,
        "messages_per_month": 10000,
        "voice_minutes": 500
    }
)
```

## Client Management

### Per-Client Configuration
Each client gets:
- Isolated agents and data
- Separate API keys
- Custom usage limits
- Independent analytics

### Usage Tracking
```bash
# View usage across all clients
chronos white-label usage --period monthly

# Per-client breakdown
chronos white-label usage --client "Client ABC"
```

## Pricing Models

White-label supports flexible billing:

| Model | How It Works |
|-------|-------------|
| **Per-agent** | Charge per deployed agent |
| **Per-message** | Charge per conversation/message |
| **Per-minute** | Charge per voice minute |
| **Flat fee** | Monthly subscription per client |
| **Custom** | Any combination |

## Web Widget

Embed AI chat in your clients' websites:

```html
<!-- Fully branded — no mention of Chronos -->
<script src="https://ai.yourcompany.com/widget.js"></script>
<yourcompany-chat
  agent="client-support-bot"
  theme="light"
  position="bottom-right"
></yourcompany-chat>
```

---

## Next Steps

- [API Reference](../api-reference/overview) — Full API documentation
- [Resources](../resources/faq) — FAQ and support
