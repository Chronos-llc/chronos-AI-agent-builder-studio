---
sidebar_position: 2
title: MCP Integration
---

# MCP (Model Context Protocol)

MCP is an open standard for connecting AI models to external data sources and tools. Chronos fully supports MCP — both hosting your own servers and connecting to existing ones.

## What Is MCP?

MCP provides a standardized way for AI agents to:
- **Read data** from external sources (databases, files, APIs)
- **Call tools** on external systems (create tickets, send emails)
- **Access context** beyond the model's training data

## Connecting to MCP Servers

### Via Configuration

```yaml
# agent.yaml
tools:
  - name: github
    mcp: true
    server:
      command: npx
      args: ["-y", "@modelcontextprotocol/server-github"]
      env:
        GITHUB_TOKEN: ${GITHUB_TOKEN}

  - name: postgres
    mcp: true
    server:
      command: npx
      args: ["-y", "@modelcontextprotocol/server-postgres"]
      env:
        DATABASE_URL: ${DATABASE_URL}
```

### Via Dashboard

1. Go to **Settings → Integrations → MCP**
2. Click **Add MCP Server**
3. Enter the server command or URL
4. Configure environment variables
5. Test the connection
6. Assign to agents

## Hosting MCP Servers

Chronos can host MCP servers for you:

```bash
# Deploy an MCP server
chronos mcp deploy ./my-mcp-server \
  --name "internal-docs" \
  --description "Access to internal documentation"
```

### Building a Custom MCP Server

```python
# my_mcp_server.py
from chronos.mcp import MCPServer, tool, resource

server = MCPServer(name="company-data")

@server.tool()
async def search_knowledge_base(query: str) -> list[dict]:
    """Search the company knowledge base."""
    results = await kb.search(query)
    return results

@server.resource("docs://{path}")
async def get_document(path: str) -> str:
    """Retrieve a specific document."""
    return await storage.read(f"docs/{path}")

if __name__ == "__main__":
    server.run()
```

## Popular MCP Servers

| Server | What It Provides |
|--------|-----------------|
| `server-github` | GitHub repos, issues, PRs |
| `server-postgres` | PostgreSQL database access |
| `server-slack` | Slack channels and messages |
| `server-filesystem` | Local file system access |
| `server-google-drive` | Google Drive files |
| `server-notion` | Notion pages and databases |
| `server-brave-search` | Web search via Brave |

## MCP Security

```yaml
mcp:
  security:
    sandboxed: true              # Run servers in isolated containers
    network_policy: restricted   # Limit network access
    read_only: false             # Allow write operations
    audit_log: true              # Log all MCP calls
```

---

## Next Steps

- [External APIs](./apis) — Connect non-MCP APIs
- [Tools](../agents/tools) — Use MCP tools in agents
