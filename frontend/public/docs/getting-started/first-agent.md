---
sidebar_position: 3
title: Build Your First Agent
---

# Build Your First Agent

This step-by-step tutorial guides you through creating a functional AI agent using Chronos Studio. By the end, you'll have a working customer support agent ready to handle inquiries.

## Prerequisites

- Chronos Studio account
- API key configured
- SDK or CLI installed

## Step 1: Define Your Agent's Purpose

Before coding, define your agent:
- **Role**: Customer Support Agent
- **Capabilities**: Answer product questions, troubleshoot issues, create tickets
- **Personality**: Friendly, professional, helpful

## Step 2: Create the Agent

### Using the Dashboard

1. Log in to Chronos Studio
2. Navigate to **Agents** → **Create New**
3. Fill in the configuration:

```yaml
name: Support Agent
type: conversational
description: Handles customer support inquiries

config:
  system_prompt: |
    You are a customer support agent for Acme Products.
    You are friendly, professional, and concise.
    Always try to resolve issues on the first contact.
    If you cannot help, escalate to a human agent.
    
  temperature: 0.7
  max_tokens: 1024
```

### Using the API

```bash
curl -X POST https://api.chronos.studio/v1/agents \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Support Agent",
    "type": "conversational",
    "config": {
      "system_prompt": "You are a customer support agent for Acme Products...",
      "temperature": 0.7
    }
  }'
```

## Step 3: Add Tools

Expand your agent's capabilities with tools:

### Web Search
```bash
chronos tools enable web_search --agent agent_abc123
```

### Custom Tool: Order Lookup
Create a custom tool to look up orders:

```python
from chronos.tools import Tool

class OrderLookup(Tool):
    name = "lookup_order"
    description = "Look up customer order status"
    
    parameters = {
        "order_id": {"type": "string", "required": True}
    }
    
    def execute(self, order_id):
        # Connect to your order system
        order = database.orders.find(order_id)
        return {
            "status": order.status,
            "items": order.items,
            "shipping": order.shipping_info
        }
```

Register the tool:
```bash
chronos tools register order_lookup.py --agent agent_abc123
```

## Step 4: Configure Memory

Enable conversation history:

```json
{
  "memory": {
    "type": "conversation",
    "max_history": 50
  }
}
```

For persistent user memory:

```json
{
  "memory": {
    "type": "persistent",
    "storage": "database"
  }
}
```

## Step 5: Test Your Agent

### In the Dashboard
Use the built-in chat to test:
1. Open your agent
2. Click "Test Chat"
3. Try various queries

### Programmatically
```python
from chronos import Chronos

client = Chronos(api_key="sk_live_...")

# Test conversation
response = client.agents.chat(
    agent_id="agent_abc123",
    message="I need help with my order #12345"
)

print(response.message)
```

## Step 6: Deploy

Once testing is complete, deploy to production:

```bash
chronos agent deploy agent_abc123 --env production
```

Get your production endpoint:
```bash
chronos agent info agent_abc123
# endpoint: https://api.chronos.studio/v1/agents/agent_abc123
```

## Complete Example

```python
from chronos import Chronos
from chronos.tools import register_tool

# Initialize
client = Chronos(api_key="sk_live_...")

# Register custom tool
@register_tool
def create_support_ticket(issue: str, priority: str = "medium"):
    """Create a support ticket in the ticketing system."""
    ticket = {
        "subject": issue,
        "priority": priority,
        "status": "open"
    }
    return ticket

# Create agent with tools
agent = client.agents.create(
    name="Support Agent",
    type="conversational",
    config={
        "system_prompt": """You are a support agent for Acme.
        Use create_support_ticket when users report issues.""",
        "temperature": 0.7,
        "tools": ["web_search", "create_support_ticket"]
    }
)

# Test
response = client.agents.chat(
    agent_id=agent.id,
    message="My account is locked and I can't access my orders!"
)

print(response.message)
# I'll help you with that! Let me create a support ticket...
```

## Monitoring

Track your agent's performance:

```bash
# View statistics
chronos agent stats agent_abc123

# View recent conversations
chronos logs agent_abc123 --lines 50
```

## Next Steps

- [Add Voice Capabilities](/docs/voice-ai/getting-started)
- [Configure Webhooks](/docs/api-reference/webhooks)
- [Set Up Multi-Agent System](/docs/agents/multi-agent)
