---
sidebar_position: 1
title: Integrations Overview
---

# Integrations Overview

Connect your agents to the tools and services your business already uses. Chronos supports built-in integrations, MCP servers, and custom API connections.

## Integration Categories

### Messaging Platforms
Connect agents to the channels your users prefer:
- **Telegram** — Bot API integration
- **WhatsApp** — Business API
- **Slack** — Slack App with events
- **Discord** — Bot integration
- **SMS** — Via Twilio, Vonage

### APIs & Services
- **Stripe** — Payments and billing
- **HubSpot / Salesforce** — CRM
- **Google Workspace** — Gmail, Calendar, Drive
- **Notion** — Knowledge bases
- **GitHub / GitLab** — Code repositories

### Databases
- **PostgreSQL** — Relational data
- **MongoDB** — Document storage
- **Redis** — Caching and real-time data
- **Pinecone / Weaviate** — Vector databases

### MCP Servers
Connect to any MCP-compatible server for unlimited extensibility.

## Quick Setup

### Via Dashboard
1. Go to **Settings → Integrations**
2. Click **Add Integration**
3. Select the service
4. Authenticate (OAuth or API key)
5. Assign to agents

### Via CLI
```bash
# List available integrations
chronos integrations list

# Connect an integration
chronos integrations add telegram --bot-token $BOT_TOKEN

# Assign to an agent
chronos integrations assign telegram my-agent
```

### Via agent.yaml
```yaml
channels:
  - type: telegram
    config:
      bot_token: ${TELEGRAM_BOT_TOKEN}

  - type: whatsapp
    config:
      phone_number_id: ${WA_PHONE_ID}
      access_token: ${WA_ACCESS_TOKEN}

  - type: slack
    config:
      bot_token: ${SLACK_BOT_TOKEN}
      app_token: ${SLACK_APP_TOKEN}
```

---

## Next Steps

- [MCP Integration](./mcp) — Connect MCP servers
- [External APIs](./apis) — Connect any REST API
- [Messaging Platforms](./messaging) — Set up messaging channels
- [Databases](./databases) — Connect data stores
