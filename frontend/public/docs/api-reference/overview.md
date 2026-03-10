---
sidebar_position: 1
title: API Overview
---

# API Reference

The Chronos Studio REST API gives you full programmatic control over agents, conversations, tools, and voice — everything available in the dashboard and CLI, accessible via HTTP.

## Base URL

```
https://api.chronos.studio/v1
```

## Authentication

All API requests require a Bearer token:

```bash
curl https://api.chronos.studio/v1/agents \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Generate API keys in the [Dashboard → Settings → API Keys](https://app.chronos.studio/settings/api-keys).

## Response Format

All responses are JSON:

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-03-09T12:00:00Z"
  }
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "code": "agent_not_found",
    "message": "Agent 'my-agent' does not exist",
    "status": 404
  }
}
```

## Rate Limits

| Plan | Requests/min | Concurrent |
|------|-------------|------------|
| Free | 60 | 5 |
| Pro | 600 | 50 |
| Enterprise | Custom | Custom |

Rate limit headers:
```
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 587
X-RateLimit-Reset: 1709964000
```

## API Sections

| Section | Description |
|---------|-------------|
| [Authentication](./authentication) | API keys, OAuth, tokens |
| [Agents](./agents) | Create, configure, manage agents |
| [Voice](./voice) | Voice sessions, phone numbers |
| [Tools](./tools) | Tool management and execution |
| [Webhooks](./webhooks) | Event subscriptions |

## SDKs

Use our official SDKs instead of raw HTTP when possible:

```python
# Python
pip install chronos-sdk
from chronos import ChronosClient
client = ChronosClient(api_key="your_key")
```

```typescript
// TypeScript
npm install @chronos-studio/sdk
import { ChronosClient } from '@chronos-studio/sdk';
const client = new ChronosClient({ apiKey: 'your_key' });
```

---

## Next Steps

- [Authentication](./authentication) — Set up API access
- [Agents API](./agents) — Manage agents programmatically
