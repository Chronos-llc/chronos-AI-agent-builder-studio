---
sidebar_position: 2
title: Creating Agents
---

# Creating Agents

This guide covers everything you need to configure and deploy a Chronos agent.

## Agent Configuration

Every agent is defined by an `agent.yaml` file:

```yaml
# agent.yaml — Complete configuration reference
name: my-agent                    # Unique identifier
description: What this agent does # Human-readable description
version: 1.0.0                   # Semantic version

# === Model ===
model: gemini-2.0-flash          # LLM to use
temperature: 0.7                 # 0.0 (deterministic) to 1.0 (creative)
max_tokens: 4096                 # Maximum response length
top_p: 0.9                       # Nucleus sampling (optional)

# === System Prompt ===
system_prompt: |
  You are a helpful assistant specialized in data analysis.
  Always provide sources for claims.
  Format responses with clear headers and bullet points.

# Or reference an external file:
# system_prompt_file: ./prompts/system.md

# === Memory ===
memory:
  type: persistent               # session | persistent | none
  ttl: 30d                       # How long to remember (persistent only)
  max_context_messages: 50       # Messages included in context window
  vector_search: true            # Enable semantic search over history

# === Tools ===
tools:
  # Built-in tools
  - name: web_search
    builtin: true
    config:
      max_results: 5

  - name: code_interpreter
    builtin: true

  # Custom tools
  - name: query_database
    path: ./tools/db_query.py
    config:
      connection_string: ${DATABASE_URL}

  # MCP tools
  - name: github
    mcp: true
    server: github-mcp-server

# === Channels ===
channels:
  - type: api                    # Always recommended
  - type: telegram
    config:
      bot_token: ${TELEGRAM_BOT_TOKEN}
  - type: whatsapp
    config:
      phone_number_id: ${WA_PHONE_ID}
      access_token: ${WA_ACCESS_TOKEN}
  - type: slack
    config:
      bot_token: ${SLACK_BOT_TOKEN}

# === Guardrails ===
guardrails:
  max_tool_calls: 10             # Max tool calls per turn
  blocked_topics: []             # Topics the agent should refuse
  pii_detection: true            # Detect and mask PII
  rate_limit: 100/min            # Max requests per minute

# === Scheduling (Autonomous Agents) ===
schedule:
  cron: "0 8 * * *"             # Run daily at 8 AM
  trigger: new_email             # Or trigger on events
  action: summarize_and_notify
```

## Creating via CLI

### From a Template

```bash
# List available templates
chronos templates list

# Create from template
chronos init my-agent --template customer-support
chronos init my-agent --template research-assistant
chronos init my-agent --template voice-receptionist
```

### From Scratch

```bash
chronos init my-agent --template blank
```

### From a Blueprint

```bash
chronos create --from blueprint:ecommerce-support
```

## Creating via Dashboard

1. Go to **Agents → New Agent**
2. Choose a starting point:
   - **Spark** — Describe in natural language
   - **Template** — Start from a template
   - **Blank** — Configure everything manually
3. Configure model, tools, memory
4. Test in the live preview
5. Deploy

## Creating via API

```python
from chronos import ChronosClient

client = ChronosClient(api_key="your_key")

agent = client.agents.create(
    name="data-analyst",
    model="gemini-2.0-flash",
    system_prompt="You are a data analyst...",
    tools=[
        {"name": "web_search", "builtin": True},
        {"name": "code_interpreter", "builtin": True},
    ],
    memory={"type": "persistent", "ttl": "30d"},
    channels=[{"type": "api"}],
)

print(f"Agent created: {agent.id}")
print(f"Endpoint: {agent.endpoint}")
```

## Environment Variables

Use `${VAR_NAME}` in `agent.yaml` for secrets:

```bash
# Set environment variables
chronos env set TELEGRAM_BOT_TOKEN="your_token"
chronos env set DATABASE_URL="postgres://..."

# View configured variables
chronos env list
```

## Local Development

```bash
# Start interactive dev mode
chronos dev

# Dev mode with hot reload (watches for file changes)
chronos dev --watch

# Dev mode with a specific test file
chronos dev --test tests/scenarios.yaml
```

## Deployment

```bash
# Deploy to production
chronos deploy

# Deploy to a specific environment
chronos deploy --env staging

# Deploy with a version tag
chronos deploy --tag v1.2.0
```

---

## Next Steps

- [Tools](./tools) — Add capabilities to your agent
- [Memory](./memory) — Configure persistent memory
- [Blueprints](./blueprints) — Save reusable templates
