---
sidebar_position: 3
title: Creating Agents
---

# Creating Agents

This guide walks you through creating AI agents in Chronos Studio using the visual builder, CLI, API, and programmatic approaches.

## Agent Configuration Guide

### Core Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| name | string | Yes | Agent display name |
| type | enum | Yes | conversational, task, voice, multi |
| system_prompt | string | Yes | Instructions for the agent |
| temperature | float | No | Creativity vs determinism (0-1, default: 0.7) |
| max_tokens | int | No | Maximum response length |
| tools | array | No | Enabled tool names |
| memory | object | No | Memory configuration |
| voice | object | No | Voice-specific settings |

### Configuration File Format

```yaml
# agent.yaml
name: "My Support Agent"
type: "conversational"
version: "1.0.0"

system_prompt: |
  You are a helpful customer support agent for Acme Corp.
  You have extensive knowledge of our products and policies.
  Always be polite, professional, and concise.

config:
  temperature: 0.7
  max_tokens: 2048
  response_format: "markdown"

tools:
  - search_knowledge_base
  - create_ticket
  - send_email
  - get_order_status

memory:
  type: "conversation"
  max_history: 50
  persist: true

voice:
  enabled: true
  provider: "elevenlabs"
  voice_id: "rachel"
```

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

## Creating Agents via CLI

### Installation

```bash
npm install -g @chronos/cli
```

### Create a New Agent

```bash
# Interactive creation
chronos agents create

# Non-interactive with flags
chronos agents create \
  --name "My Support Agent" \
  --type conversational \
  --system-prompt "You are a helpful support agent..." \
  --config ./agent.yaml
```

### CLI Commands

```bash
# List agents
chronos agents list

# Get agent details
chronos agents get agent_abc123

# Update agent
chronos agents update agent_abc123 --config ./updated-config.yaml

# Delete agent
chronos agents delete agent_abc123

# Deploy agent
chronos agents deploy agent_abc123 --env production

# View logs
chronos agents logs agent_abc123 --tail 100
```

### Agent YAML Configuration

```yaml
# agent.yaml
name: "Support Agent"
type: "conversational"
version: "1.0.0"

system_prompt: |
  You are a helpful customer support agent.

config:
  temperature: 0.7
  max_tokens: 2048

tools:
  - name: "search_knowledge_base"
    enabled: true
  - name: "create_ticket"
    enabled: true

environment:
  NODE_ENV: "production"
  LOG_LEVEL: "info"
```

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

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /v1/agents | Create new agent |
| GET | /v1/agents | List all agents |
| GET | /v1/agents/:id | Get agent details |
| PUT | /v1/agents/:id | Update agent |
| DELETE | /v1/agents/:id | Delete agent |
| POST | /v1/agents/:id/deploy | Deploy agent |
| GET | /v1/agents/:id/logs | Get agent logs |

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

## Environment Variables

### Agent Configuration

```bash
# Required
CHRONOS_API_KEY=sk_xxxxx

# Optional - Agent settings
CHRONOS_AGENT_NAME=MyAgent
CHRONOS_AGENT_TYPE=conversational
CHRONOS_MAX_TOKENS=2048
CHRONOS_TEMPERATURE=0.7

# Optional - Memory
CHRONOS_MEMORY_TYPE=conversation
CHRONOS_MEMORY_MAX_HISTORY=50

# Optional - Voice
CHRONOS_VOICE_ENABLED=true
CHRONOS_VOICE_PROVIDER=elevenlabs
CHRONOS_VOICE_ID=rachel

# Optional - Tools
CHRONOS_TOOLS_ENABLED=true
CHRONOS_CUSTOM_TOOLS_PATH=./tools
```

### Using Environment Variables

```python
import os
from chronos import Agent

agent = Agent.create(
    name=os.getenv("CHRONOS_AGENT_NAME", "Default Agent"),
    type=os.getenv("CHRONOS_AGENT_TYPE", "conversational"),
    config={
        "temperature": float(os.getenv("CHRONOS_TEMPERATURE", "0.7"))
    }
)
```

## Local Development

### Setting Up Local Dev Environment

```bash
# Clone the agent template
chronos init my-agent --template support-agent

# Navigate to project
cd my-agent

# Install dependencies
npm install

# Configure local environment
cp .env.example .env
# Edit .env with your API keys

# Start local development server
chronos dev

# Run tests
chronos test

# Build for production
chronos build
```

### Local Development Server

```bash
# Start with hot reload
chronos dev --port 3000 --debug

# Run with specific config
chronos dev --config ./dev-config.yaml

# Enable verbose logging
chronos dev --verbose
```

### Testing Agents Locally

```bash
# Interactive chat
chronos chat

# Run test suite
chronos test

# Test with specific input
chronos test --input "Hello, I need help"
```

## Deployment

### Deploy to Production

```bash
# Via CLI
chronos agents deploy agent_abc123 --env production

# Via API
curl -X POST https://api.chronos.studio/v1/agents/agent_abc123/deploy \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"environment": "production"}'
```

### Deployment Options

| Option | Description |
|--------|-------------|
| staging | Deploy to staging environment |
| production | Deploy to production |
| canary | Canary deployment (gradual rollout) |
| rollback | Rollback to previous version |

### Docker Deployment

```dockerfile
FROM chronos/agent-runtime:latest

COPY agent.yaml /app/agent.yaml
COPY tools /app/tools

ENV CHRONOS_API_KEY=${API_KEY}

CMD ["chronos", "start", "--config", "/app/agent.yaml"]
```

```bash
# Build and run
docker build -t my-agent .
docker run -e API_KEY=xxx my-agent
```

### Kubernetes Deployment

```yaml
apiVersion: chronos.ai/v1
kind: Agent
metadata:
  name: my-support-agent
spec:
  version: "1.0.0"
  replicas: 3
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
```

### Monitoring Deployment

```bash
# View deployment status
chronos agents status agent_abc123

# Check logs
chronos agents logs agent_abc123 --follow

# View metrics
chronos agents metrics agent_abc123
```

## Best Practices

1. **Start Simple**: Begin with basic configuration and add complexity gradually
2. **Iterate**: Test frequently and refine prompts based on interactions
3. **Monitor**: Use analytics to track performance and identify issues
4. **Version**: Keep track of configuration changes
5. **Secure**: Follow security best practices for API keys and data
6. **Scale**: Plan for traffic growth and configure auto-scaling
7. **Backup**: Maintain backups of agent configurations

## Next Steps

- Learn about [Agent Memory](/docs/agents/memory)
- Explore [Agent Blueprints](/docs/agents/blueprints)
- Configure [Tools Configuration](/docs/agents/tools)
- Set up [Multi-Agent Systems](/docs/agents/multi-agent)
