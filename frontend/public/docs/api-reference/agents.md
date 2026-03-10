---
sidebar_position: 3
title: Agents API
---

# Agents API

The Agents API allows you to create, configure, and manage AI agents programmatically.

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /agents | List all agents |
| POST | /agents | Create a new agent |
| GET | /agents/{id} | Get agent details |
| PUT | /agents/{id} | Update agent |
| DELETE | /agents/{id} | Delete agent |
| POST | /agents/{id}/chat | Send message to agent |

## List Agents

```bash
GET /agents
```

### Query Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | Page number (default: 1) |
| limit | integer | Items per page (default: 20) |
| type | string | Filter by agent type |
| status | string | Filter by status (active, inactive) |
| search | string | Search by name |

### Response
```json
{
  "data": [
    {
      "id": "agent_abc123",
      "name": "Customer Support",
      "type": "conversational",
      "status": "active",
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-15T12:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

## Create Agent

```bash
POST /agents
```

### Request Body
```json
{
  "name": "My Support Agent",
  "type": "conversational",
  "description": "Handles customer support inquiries",
  "config": {
    "system_prompt": "You are a helpful customer support agent...",
    "temperature": 0.7,
    "max_tokens": 2048,
    "tools": ["web_search", "create_ticket"],
    "memory": {
      "type": "conversation",
      "max_history": 50
    }
  }
}
```

### Response
```json
{
  "id": "agent_xyz789",
  "name": "My Support Agent",
  "type": "conversational",
  "status": "active",
  "endpoint": "https://api.chronos.studio/v1/agents/agent_xyz789",
  "created_at": "2024-01-15T14:00:00Z"
}
```

## Get Agent

```bash
GET /agents/{id}
```

### Response
```json
{
  "id": "agent_xyz789",
  "name": "My Support Agent",
  "type": "conversational",
  "description": "Handles customer support inquiries",
  "status": "active",
  "config": {
    "system_prompt": "You are a helpful customer support agent...",
    "temperature": 0.7,
    "max_tokens": 2048,
    "tools": ["web_search", "create_ticket"],
    "memory": {
      "type": "conversation",
      "max_history": 50
    }
  },
  "statistics": {
    "total_conversations": 1250,
    "messages_today": 45,
    "average_rating": 4.5
  },
  "created_at": "2024-01-15T14:00:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

## Update Agent

```bash
PUT /agents/{id}
```

### Request Body
```json
{
  "name": "Updated Support Agent",
  "config": {
    "temperature": 0.8,
    "tools": ["web_search", "create_ticket", "get_order_status"]
  }
}
```

## Delete Agent

```bash
DELETE /agents/{id}
```

### Response
```json
{
  "success": true,
  "message": "Agent deleted successfully"
}
```

## Send Message to Agent

```bash
POST /agents/{id}/chat
```

### Request Body
```json
{
  "message": "I need help with my order",
  "session_id": "session_abc123",
  "context": {
    "user_id": "user_xyz789",
    "metadata": {
      "source": "website"
    }
  }
}
```

### Response
```json
{
  "message_id": "msg_def456",
  "response": "I'd be happy to help you with your order. Could you please provide your order number?",
  "session_id": "session_abc123",
  "tool_calls": [
    {
      "tool": "get_order_status",
      "parameters": {"order_id": null},
      "status": "pending"
    }
  ],
  "metadata": {
    "tokens_used": 150,
    "model": "gpt-4"
  }
}
```

## Agent Types

| Type | Description |
|------|-------------|
| `conversational` | Standard chat-based agent |
| `task` | Task-oriented agent |
| `voice` | Voice-enabled agent |
| `multi` | Multi-agent system |

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| system_prompt | string | - | Agent instructions |
| temperature | float | 0.7 | Response creativity |
| max_tokens | integer | 2048 | Max response length |
| tools | array | [] | Enabled tool names |
| memory.type | string | conversation | Memory type |
| memory.max_history | integer | 50 | History messages |
| voice.enabled | boolean | false | Voice activation |
| voice.voice_id | string | - | Voice model ID |

## Webhooks for Agent Events

Configure webhooks to receive:
- `agent.message.received` - New message
- `agent.message.completed` - Response complete
- `agent.tool_called` - Tool execution
- `agent.error` - Error occurred
