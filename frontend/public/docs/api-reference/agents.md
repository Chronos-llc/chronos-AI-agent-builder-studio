---
sidebar_position: 3
title: Agents API
---

# Agents API

Create, manage, and interact with agents programmatically.

## List Agents

```
GET /v1/agents
```

```bash
curl https://api.mohex.org/v1/agents \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "agt_abc123",
      "name": "support-agent",
      "description": "Customer support agent",
      "model": "gemini-2.0-flash",
      "status": "deployed",
      "created_at": "2026-03-01T00:00:00Z",
      "updated_at": "2026-03-09T12:00:00Z"
    }
  ],
  "meta": { "total": 1, "page": 1, "per_page": 20 }
}
```

## Create Agent

```
POST /v1/agents
```

```bash
curl -X POST https://api.mohex.org/v1/agents \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "support-agent",
    "description": "Customer support agent",
    "model": "gemini-2.0-flash",
    "temperature": 0.7,
    "system_prompt": "You are a helpful customer support agent...",
    "tools": [
      {"name": "web_search", "builtin": true}
    ],
    "memory": {
      "type": "persistent",
      "ttl": "30d"
    }
  }'
```

## Get Agent

```
GET /v1/agents/:agent_id
```

## Update Agent

```
PATCH /v1/agents/:agent_id
```

```bash
curl -X PATCH https://api.mohex.org/v1/agents/agt_abc123 \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 0.5,
    "system_prompt": "Updated system prompt..."
  }'
```

## Delete Agent

```
DELETE /v1/agents/:agent_id
```

## Chat with Agent

```
POST /v1/agents/:agent_id/chat
```

```bash
curl -X POST https://api.mohex.org/v1/agents/agt_abc123/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your business hours?",
    "conversation_id": "conv_xyz789",
    "user_id": "user_123"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Our business hours are Monday through Friday, 9 AM to 6 PM EST.",
    "conversation_id": "conv_xyz789",
    "tools_used": [],
    "tokens": { "input": 45, "output": 23 },
    "latency_ms": 342
  }
}
```

### Streaming

```bash
curl -X POST https://api.mohex.org/v1/agents/agt_abc123/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about AI agents", "stream": true}'
```

Returns Server-Sent Events (SSE):
```
data: {"type": "text", "content": "AI agents are "}
data: {"type": "text", "content": "autonomous systems "}
data: {"type": "tool_call", "tool": "web_search", "status": "started"}
data: {"type": "tool_call", "tool": "web_search", "status": "completed"}
data: {"type": "text", "content": "that can reason and take actions."}
data: {"type": "done", "tokens": {"input": 12, "output": 87}}
```

## Deploy Agent

```
POST /v1/agents/:agent_id/deploy
```

```bash
curl -X POST https://api.mohex.org/v1/agents/agt_abc123/deploy \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"environment": "production", "tag": "v1.2.0"}'
```

## Agent Analytics

```
GET /v1/agents/:agent_id/analytics?period=7d
```

**Response:**
```json
{
  "success": true,
  "data": {
    "period": "7d",
    "conversations": 1247,
    "messages": 8934,
    "avg_response_time_ms": 450,
    "tool_calls": 3201,
    "tokens_used": {"input": 890000, "output": 445000},
    "satisfaction_score": 4.3
  }
}
```

---

## Next Steps

- [Voice API](./voice) — Manage voice sessions
- [Tools API](./tools) — Manage tools
