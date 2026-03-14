---
sidebar_position: 5
title: Tools API
---

# Tools API

Manage and execute agent tools via the API.

## List Agent Tools

```
GET /v1/agents/:agent_id/tools
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "name": "web_search",
      "type": "builtin",
      "description": "Search the web for information",
      "parameters": {
        "query": {"type": "string", "required": true},
        "max_results": {"type": "integer", "default": 5}
      }
    },
    {
      "name": "query_database",
      "type": "custom",
      "description": "Query the customer database",
      "parameters": {
        "email": {"type": "string"},
        "user_id": {"type": "string"}
      }
    }
  ]
}
```

## Add Tool to Agent

```
POST /v1/agents/:agent_id/tools
```

```bash
curl -X POST https://api.mohex.org/v1/agents/agt_abc123/tools \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "send_notification",
    "description": "Send a push notification to a user",
    "parameters": {
      "user_id": {"type": "string", "required": true},
      "title": {"type": "string", "required": true},
      "body": {"type": "string", "required": true}
    },
    "webhook_url": "https://your-api.com/notifications"
  }'
```

## Execute Tool Directly

```
POST /v1/agents/:agent_id/tools/:tool_name/execute
```

```bash
curl -X POST https://api.mohex.org/v1/agents/agt_abc123/tools/web_search/execute \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agent market size 2026"}'
```

## Remove Tool

```
DELETE /v1/agents/:agent_id/tools/:tool_name
```

## Tool Execution Logs

```
GET /v1/agents/:agent_id/tools/logs?period=24h
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "tool": "web_search",
      "status": "success",
      "duration_ms": 1200,
      "input": {"query": "weather in Lagos"},
      "conversation_id": "conv_xyz",
      "timestamp": "2026-03-09T12:00:00Z"
    }
  ]
}
```

---

## Next Steps

- [Webhooks](./webhooks) — Event subscriptions
