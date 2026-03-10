---
sidebar_position: 3
title: Creating Agents
---

# Creating Agents

This guide walks you through creating AI agents in Chronos Studio using both the visual builder and programmatic approaches.

## Creating Agents via Dashboard

### Step 1: Access the Agent Builder
Navigate to the Agents section in your Chronos Studio dashboard and click "Create New Agent".

### Step 2: Define Basic Information
- **Name**: Enter a descriptive name for your agent
- **Description**: Briefly describe the agent's purpose
- **Type**: Select agent type (Conversational, Task, Voice, or Multi-Agent)

### Step 3: Configure Agent Behavior

**System Prompt**
Define the agent's personality and instructions:
```
You are a helpful customer support agent for Acme Corp.
You have extensive knowledge of our products and policies.
Always be polite, professional, and concise.
```

**Conversation Starters**
Set initial messages to guide users:
- "How can I help you today?"
- "Do you have questions about our products?"

**Response Preferences**
- Temperature setting (0.0-1.0)
- Max tokens limit
- Response format (plain text, JSON, markdown)

### Step 4: Add Tools
Configure tools to extend agent capabilities:
- Search tools
- API integrations
- Database queries
- Custom functions

### Step 5: Set Memory Configuration
- Conversation history length
- Persistent storage options
- Context window settings

### Step 6: Test and Deploy
Use the built-in chat to test your agent, then deploy to production.

## Creating Agents via API

### Using the REST API

```bash
curl -X POST https://api.chronos.studio/v1/agents \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Support Agent",
    "type": "conversational",
    "config": {
      "system_prompt": "You are a helpful support agent...",
      "temperature": 0.7,
      "max_tokens": 2048,
      "tools": ["search_knowledge_base", "create_ticket"],
      "memory": {
        "type": "conversation",
        "max_history": 50
      }
    }
  }'
```

### Response
```json
{
  "id": "agent_abc123",
  "name": "My Support Agent",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "endpoint": "https://api.chronos.studio/v1/agents/agent_abc123"
}
```

## Creating Agents via SDK

### Python SDK
```python
from chronos import Agent

agent = Agent.create(
    name="My Support Agent",
    type="conversational",
    config={
        "system_prompt": "You are a helpful support agent...",
        "temperature": 0.7,
        "tools": ["search_knowledge_base", "create_ticket"]
    }
)
```

### Node.js SDK
```javascript
const { Agent } = require('chronos-sdk');

const agent = await Agent.create({
  name: "My Support Agent",
  type: "conversational",
  config: {
    systemPrompt: "You are a helpful support agent...",
    temperature: 0.7,
    tools: ["search_knowledge_base", "create_ticket"]
  }
});
```

## Agent Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| name | string | Agent display name |
| type | enum | conversational, task, voice, multi |
| system_prompt | string | Instructions for the agent |
| temperature | float | Creativity vs determinism (0-1) |
| max_tokens | int | Maximum response length |
| tools | array | Enabled tool names |
| memory | object | Memory configuration |
| voice | object | Voice-specific settings |

## Best Practices

1. **Start Simple**: Begin with basic configuration and add complexity gradually
2. **Iterate**: Test frequently and refine prompts based on interactions
3. **Monitor**: Use analytics to track performance and identify issues
4. **Version**: Keep track of configuration changes
5. **Secure**: Follow security best practices for API keys and data

## Next Steps

- Learn about [Agent Memory](/docs/agents/memory)
- Explore [Tools Configuration](/docs/agents/tools)
- Set up [Multi-Agent Systems](/docs/agents/multi-agent)
