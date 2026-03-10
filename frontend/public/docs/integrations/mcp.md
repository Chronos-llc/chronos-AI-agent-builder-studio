---
sidebar_position: 4
title: MCP Integrations
---

# MCP Integrations

The Model Context Protocol (MCP) provides a standardized way to connect AI models with external tools and services.

## Overview

MCP enables:
- Standardized tool definitions
- Dynamic capability discovery
- Secure credential handling
- Cross-platform compatibility

## Supported MCP Servers

### Official MCP Servers

| Server | Description |
|--------|-------------|
| Filesystem | Read/write local files |
| Git | Git operations |
| PostgreSQL | Database queries |
| Slack | Slack messaging |
| GitHub | Repository operations |

### Community MCP Servers

| Server | Description |
|--------|-------------|
| Puppeteer | Browser automation |
| AWS | AWS resource management |
| Google Drive | File operations |

## Installation

### Install MCP CLI

```bash
npm install -g @modelcontextprotocol/cli
```

### Install Servers

```bash
# Install filesystem server
mcp install filesystem --path /path/to/allowed/directory

# Install GitHub server
mcp install github --token $GITHUB_TOKEN
```

## Configuration

### Global Configuration

```json
// ~/.mcp/servers.json
{
  "servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_..."
      }
    }
  }
}
```

### Per-Agent Configuration

```python
agent = client.agents.create(
    name="Developer Agent",
    config={
        "mcp_servers": [
            {"name": "filesystem", "enabled": True},
            {"name": "github", "enabled": True}
        ]
    }
)
```

## Using MCP Tools

### Automatic Tool Discovery

```python
# List available MCP tools
tools = client.mcp.list_tools()
# Returns: [Tool(name='read_file'), Tool(name='write_file'), ...]
```

### Direct Tool Usage

```python
# Use filesystem tools
result = client.mcp.execute("filesystem.read_file", {
    "path": "/data/readme.txt"
})

# Use GitHub tools
commits = client.mcp.execute("github.list_commits", {
    "owner": "chronos",
    "repo": "studio"
})
```

## Creating Custom MCP Servers

### Server Implementation

```python
from mcp.server import MCPServer
from mcp.types import Tool, Resource

class CustomMCPServer(MCPServer):
    name = "custom_server"
    version = "1.0.0"
    
    def get_tools(self):
        return [
            Tool(
                name="get_weather",
                description="Get weather for a location",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    },
                    "required": ["location"]
                }
            )
        ]
    
    async def execute_tool(self, name, arguments):
        if name == "get_weather":
            return await self.get_weather(arguments["location"])
    
    async def get_weather(self, location):
        # Implementation
        return {"temp": 72, "condition": "sunny"}
```

### Register Server

```bash
mcp register custom_server \
  --command "python" \
  --args ["server.py"]
```

## MCP Resources

### Expose Resources

```python
class DataServer(MCPServer):
    def get_resources(self):
        return [
            Resource(
                uri="data://users",
                name="User List",
                mimeType="application/json",
                description="List of all users"
            ),
            Resource(
                uri="data://config",
                name="Configuration",
                mimeType="application/json"
            )
        ]
    
    async def read_resource(self, uri):
        if uri == "data://users":
            return json.dumps(get_all_users())
```

### Consume Resources

```python
# Agent can read resources
agent = client.agents.create(
    config={
        "system_prompt": "Use the config resource to understand settings."
    }
)

# Agent automatically gets access to resources
```

## Security

### Credential Management

```bash
# Store credentials securely
mcp config set-secret github GITHUB_TOKEN "ghp_..."
mcp config set-secret aws AWS_ACCESS_KEY_ID "AKIA..."
```

### Access Control

```json
{
  "servers": {
    "sensitive_server": {
      "allowed_tools": ["read_data"],
      "denied_tools": ["delete_data", "admin"]
    }
  }
}
```

## Debugging

### View Logs

```bash
# View MCP server logs
mcp logs --server github

# Enable debug mode
mcp logs --level debug
```

### Test Tools

```bash
# Test a specific tool
mcp test github.list_repos --owner chronos
```

## Best Practices

1. **Minimal permissions** - Only enable needed tools
2. **Credential security** - Use secrets management
3. **Resource limits** - Set timeouts and limits
4. **Monitoring** - Track tool usage
5. **Updates** - Keep servers updated
