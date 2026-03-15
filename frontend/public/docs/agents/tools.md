---
sidebar_position: 3
title: Tools
---

# Agent Tools

Tools are functions that extend your agent beyond text generation — enabling it to search the web, query databases, call APIs, send messages, and interact with the real world.

## Built-in Tools

Chronos provides production-ready tools out of the box:

| Tool | Description |
|------|-------------|
| `web_search` | Search the web for real-time information |
| `code_interpreter` | Execute Python code in a sandboxed environment |
| `file_reader` | Read and parse uploaded documents (PDF, DOCX, CSV) |
| `calculator` | Perform mathematical calculations |
| `image_generator` | Generate images from text descriptions |
| `email_sender` | Send emails via configured SMTP |
| `calendar` | Read/write calendar events |

### Enable Built-in Tools

```yaml
tools:
  - name: web_search
    builtin: true
    config:
      max_results: 10
      safe_search: true

  - name: code_interpreter
    builtin: true
    config:
      timeout: 30s
      max_memory: 256MB
```

## Custom Tools

Build your own tools in Python:

### Basic Tool

```python
# tools/weather.py
from chronos.tools import tool

@tool(
    name="get_weather",
    description="Get current weather for a city"
)
async def get_weather(city: str, units: str = "celsius") -> dict:
    """Fetch weather data from an external API."""
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.com/v1/current",
            params={"city": city, "units": units}
        )
        data = response.json()

    return {
        "city": city,
        "temperature": data["temp"],
        "condition": data["condition"],
        "humidity": data["humidity"]
    }
```

### Tool with Authentication

```python
# tools/crm_lookup.py
from chronos.tools import tool
from chronos.config import env

@tool(
    name="crm_lookup",
    description="Look up a customer in the CRM by email or name"
)
async def crm_lookup(query: str, search_by: str = "email") -> dict:
    """Search the CRM for customer records."""
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{env('CRM_API_URL')}/customers/search",
            params={search_by: query},
            headers={"Authorization": f"Bearer {env('CRM_API_KEY')}"}
        )
        return response.json()
```

### Tool with Confirmation

For sensitive operations, require user confirmation:

```python
@tool(
    name="process_refund",
    description="Process a customer refund",
    requires_confirmation=True  # Agent asks user before executing
)
async def process_refund(order_id: str, amount: float, reason: str) -> str:
    # Only executes after user confirms
    result = await payment_api.refund(order_id, amount, reason)
    return f"Refund of ${amount} processed for order {order_id}"
```

## Tool Input/Output Types

Tools support rich input and output types:

```python
from pydantic import BaseModel
from chronos.tools import tool

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    relevance_score: float

@tool(name="search_knowledge_base")
async def search_kb(
    query: str,
    category: str | None = None,
    limit: int = 5
) -> list[SearchResult]:
    """Search the internal knowledge base."""
    results = await kb.search(query, category=category, limit=limit)
    return [SearchResult(**r) for r in results]
```

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
