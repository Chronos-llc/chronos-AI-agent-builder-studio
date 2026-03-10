---
sidebar_position: 4
title: Tools API
---

# Tools API

The Tools API allows you to register, configure, and manage custom tools that extend your agents' capabilities.

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /tools | List available tools |
| POST | /tools | Register a new tool |
| GET | /tools/{id} | Get tool details |
| PUT | /tools/{id} | Update tool |
| DELETE | /tools/{id} | Delete tool |
| POST | /tools/{id}/test | Test tool execution |

## List Tools

```bash
GET /tools
```

### Query Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| type | string | Filter by tool type |
| enabled | boolean | Filter by enabled status |

### Response
```json
{
  "data": [
    {
      "id": "tool_web_search",
      "name": "web_search",
      "description": "Search the web for information",
      "type": "builtin",
      "enabled": true,
      "parameters": {
        "query": {"type": "string", "required": true},
        "limit": {"type": "integer", "required": false}
      }
    }
  ]
}
```

## Register Tool

```bash
POST /tools
```

### Request Body
```json
{
  "name": "get_weather",
  "description": "Get current weather for a location",
  "type": "custom",
  "enabled": true,
  "parameters": {
    "location": {
      "type": "string",
      "required": true,
      "description": "City name or coordinates"
    },
    "units": {
      "type": "string",
      "required": false,
      "enum": ["celsius", "fahrenheit"],
      "default": "celsius"
    }
  },
  "handler": {
    "type": "function",
    "code": "async(location, units='c def executeelsius'):\n    # Your code here\n    return {\"temp\": 22, \"condition\": \"sunny\"}"
  },
  "secrets": ["WEATHER_API_KEY"]
}
```

### Response
```json
{
  "id": "tool_get_weather",
  "name": "get_weather",
  "description": "Get current weather for a location",
  "type": "custom",
  "enabled": true,
  "created_at": "2024-01-15T14:00:00Z"
}
```

## Tool Handler Types

### Function Code
```json
{
  "handler": {
    "type": "function",
    "code": "async def execute(params):\n    result = await external_api.call(params)\n    return result"
  }
}
```

### HTTP Endpoint
```json
{
  "handler": {
    "type": "http",
    "url": "https://api.example.com/tools/weather",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{ secrets.API_KEY }}"
    }
  }
}
```

### Webhook
```json
{
  "handler": {
    "type": "webhook",
    "url": "https://your-server.com/webhook/tool",
    "secret": "your_webhook_secret"
  }
}
```

## Tool Parameters Schema

Define input parameters using JSON Schema:

```json
{
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query",
        "minLength": 1,
        "maxLength": 500
      },
      "limit": {
        "type": "integer",
        "description": "Maximum results",
        "minimum": 1,
        "maximum": 100,
        "default": 10
      },
      "filters": {
        "type": "object",
        "description": "Optional filters",
        "properties": {
          "date_from": {"type": "string", "format": "date"},
          "date_to": {"type": "string", "format": "date"}
        }
      }
    },
    "required": ["query"]
  }
}
```

## Test Tool

```bash
POST /tools/{id}/test
```

### Request Body
```json
{
  "parameters": {
    "location": "San Francisco",
    "units": "celsius"
  }
}
```

### Response
```json
{
  "success": true,
  "result": {
    "temp": 18,
    "condition": "partly_cloudy",
    "humidity": 65
  },
  "execution_time": 0.234
}
```

## Tool Types

| Type | Description | Handler |
|------|-------------|---------|
| `builtin` | Pre-built Chronos tools | Native |
| `custom` | Your custom functions | Function code, HTTP, or webhook |
| `integration` | Third-party integrations | Pre-configured |

## Managing Secrets

Store sensitive credentials securely:

```bash
# Create secret
POST /tools/secrets
{
  "name": "weather_api_key",
  "value": "your_api_key_here"
}
```

Reference in tool handlers:
```json
{
  "handler": {
    "headers": {
      "X-API-Key": "{{ secrets.weather_api_key }}"
    }
  }
}
```

## Rate Limiting

Tools have separate rate limits:
- Custom function tools: 1000 calls/minute
- HTTP endpoint tools: Subject to target API limits
- Webhook tools: 500 calls/minute

## Error Handling

Tool errors return structured responses:

```json
{
  "success": false,
  "error": {
    "code": "TOOL_EXECUTION_ERROR",
    "message": "Failed to fetch weather data",
    "details": "API rate limit exceeded"
  }
}
```

## Best Practices

1. **Validate parameters** - Define strict parameter schemas
2. **Handle errors gracefully** - Return meaningful error messages
3. **Implement timeouts** - Set appropriate execution timeouts
4. **Log usage** - Track tool performance and errors
5. **Secure secrets** - Never expose credentials in code
