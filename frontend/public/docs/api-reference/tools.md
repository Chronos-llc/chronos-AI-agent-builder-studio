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
