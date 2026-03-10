---
sidebar_position: 6
title: Tools & Integrations
---

# Tools & Integrations

Tools extend your agents' capabilities by enabling them to interact with external services, APIs, databases, and custom functions. This guide covers how to configure and use tools in Chronos Studio.

## Tool Types

### Built-in Tools
Chronos Studio provides pre-built tools for common operations:

| Tool | Description | Use Case |
|------|-------------|----------|
| web_search | Search the web for information | Research, fact-finding |
| calculator | Mathematical calculations | Numeric computations |
| code_interpreter | Execute code snippets | Data processing |
| file_reader | Read files from storage | Document access |
| http_request | Make HTTP API calls | External integrations |

### Custom Tools
Create custom tools to integrate with your services:

```python
from chronos.tools import Tool

class GetOrderStatus(Tool):
    name = "get_order_status"
    description = "Retrieve the status of an order by order ID"
    
    parameters = {
        "order_id": {"type": "string", "required": True}
    }
    
    def execute(self, order_id: str) -> dict:
        # Your integration logic here
        return {"status": "shipped", "tracking": "1Z999..."}
```

## Configuring Tools

### Via Dashboard
1. Open your agent configuration
2. Navigate to "Tools" section
3. Enable desired tools
4. Configure tool parameters
5. Save and deploy

### Via API
```bash
curl -X PUT https://api.chronos.studio/v1/agents/agent_123/tools \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tools": [
      {"name": "web_search", "enabled": true},
      {"name": "get_order_status", "enabled": true, "config": {...}}
    ]
  }'
```

### Via Configuration File
```yaml
# agent.yaml
agent:
  name: Support Agent
  tools:
    - name: web_search
      enabled: true
    - name: create_ticket
      enabled: true
      config:
        integration: zendesk
    - name: get_order_status
      enabled: true
```

## Tool Parameters

### Parameter Definitions
Define input parameters for your tools:

```python
class CustomTool(Tool):
    parameters = {
        "query": {
            "type": "string",
            "required": True,
            "description": "Search query"
        },
        "limit": {
            "type": "integer",
            "required": False,
            "default": 10,
            "description": "Maximum results"
        },
        "filters": {
            "type": "object",
            "required": False,
            "description": "Additional filters"
        }
    }
```

### Validation
Tools automatically validate input:
- Type checking
- Required field validation
- Format validation
- Range constraints

## Tool Execution

### Agent Tool Calls
When an agent decides to use a tool:

```python
# Agent reasoning output
{
  "tool": "get_order_status",
  "parameters": {"order_id": "ORD-12345"},
  "reasoning": "The user wants to know their order status"
}

# Tool execution result
{
  "status": "shipped",
  "estimated_delivery": "2024-01-20",
  "tracking_number": "1Z999AA10123456784"
}
```

### Tool Timeout
Configure timeout for long-running tools:

```yaml
tools:
  - name: long_running_task
    timeout: 300  # 5 minutes
    retry:
      attempts: 3
      backoff: exponential
```

## Tool Integrations

### API Integrations
Connect to external APIs:

```python
class APITool(Tool):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.example.com"
        self.headers = {"Authorization": f"Bearer {os.getenv('API_KEY')}"}
    
    def execute(self, endpoint: str, **kwargs):
        response = requests.get(
            f"{self.base_url}/{endpoint}",
            headers=self.headers,
            **kwargs
        )
        return response.json()
```

### Database Tools
Query databases directly:

```python
class DatabaseTool(Tool):
    name = "query_database"
    
    def execute(self, query: str, params: dict = None):
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
```

### Webhook Tools
Trigger webhooks:

```python
class WebhookTool(Tool):
    def execute(self, url: str, payload: dict):
        requests.post(url, json=payload)
        return {"status": "delivered"}
```

## Security

### API Key Management
Store sensitive credentials securely:

```python
from chronos.secrets import Secret

api_key = Secret.get("my_service_api_key")
# Use in tool implementation
```

### Tool Permissions
Control which tools agents can access:

```json
{
  "tool_permissions": {
    "allow_all": false,
    "allowed_tools": ["web_search", "calculator"],
    "denied_tools": ["admin_panel", "delete_data"]
  }
}
```

## Tool Development

### Testing Tools
```python
from chronos.tools.testing import ToolTester

tester = ToolTester(GetOrderStatus)
result = tester.run({"order_id": "ORD-123"})
assert result["status"] == "shipped"
```

### Debugging Tools
```bash
# Enable tool debugging
chronos agent debug agent_123 --tools

# View tool execution logs
chronos logs tools --agent agent_123
```

## Best Practices

1. **Minimal Tool Scope**: Each tool should do one thing well
2. **Clear Documentation**: Document parameters and return values
3. **Error Handling**: Always handle potential failures gracefully
4. **Rate Limiting**: Respect external API rate limits
5. **Caching**: Cache results when appropriate
6. **Logging**: Log tool usage for debugging and analytics

## Next Steps

- Explore [API Integrations](/docs/integrations/apis)
- Configure [Database Connections](/docs/integrations/databases)
- Set up [MCP Integrations](/docs/integrations/mcp)

## MCP Tools

Connect to Model Context Protocol servers for external tool access:

```yaml
tools:
  - name: github
    mcp: true
    server: github-mcp-server
    config:
      repo: "chronos-studio/main-app"
      token: ${GITHUB_TOKEN}

  - name: postgres
    mcp: true
    server: postgres-mcp-server
    config:
      connection: ${DATABASE_URL}
```

## Tool Best Practices

1. **Clear descriptions** — The LLM uses descriptions to decide when to use tools
2. **Type hints** — Always use Python type hints for parameters
3. **Error handling** — Return helpful error messages, don't raise exceptions
4. **Timeouts** — Set reasonable timeouts for external API calls
5. **Idempotency** — Make tools safe to retry when possible
6. **Least privilege** — Only give tools the permissions they need

## Testing Tools

```python
# tests/test_tools.py
from chronos.testing import ToolTestRunner

async def test_weather_tool():
    runner = ToolTestRunner("tools/weather.py")
    result = await runner.call("get_weather", city="Lagos")

    assert result["city"] == "Lagos"
    assert "temperature" in result
    assert "condition" in result
```

```bash
chronos test tools
```

---

## Next Steps

- [Memory](./memory) — Give agents persistent context
- [MCP Integrations](../integrations/mcp) — Connect MCP servers
- [API Reference: Tools](../api-reference/tools) — REST API for tool management
