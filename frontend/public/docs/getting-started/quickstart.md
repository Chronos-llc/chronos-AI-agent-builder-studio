---
sidebar_position: 2
title: Quick Start
---

# Quick Start

Get up and running with Chronos Studio in under 5 minutes. This guide walks you through the essential steps to create your first agent and send first message.

## your Step 1: Get Your API Key

1. Log in to [Chronos Studio](https://chronos.studio)
2. Navigate to **Settings** → **API Keys**
3. Click **Create New Key**
4. Copy your API key (shown only once)

## Step 2: Install the SDK

```bash
# Python
pip install chronos-sdk

# Node.js
npm install chronos-sdk
```

## Step 3: Create Your First Agent

### Using the SDK

```python
from chronos import Chronos

# Initialize the client
client = Chronos(api_key="sk_live_...")

# Create an agent
agent = client.agents.create(
    name="My First Agent",
    type="conversational",
    config={
        "system_prompt": "You are a helpful assistant.",
        "temperature": 0.7
    }
)

print(f"Agent created: {agent.id}")
```

### Using the CLI

```bash
chronos agent create \
  --name "My First Agent" \
  --type conversational \
  --system-prompt "You are a helpful assistant."
```

## Step 4: Send a Message

```python
# Send a message to the agent
response = client.agents.chat(
    agent_id="agent_abc123",
    message="Hello! What can you help me with?"
)

print(response.message)
print(f"Tokens used: {response.metadata.tokens_used}")
```

## Step 5: Configure Tools (Optional)

```python
# Add web search capability
client.agents.update(
    agent_id="agent_abc123",
    config={
        "tools": ["web_search"]
    }
)
```

## What's Next?

You've created your first agent! Here are some next steps to explore:

### Add Voice Capabilities
Enable voice interactions for your agent:
```bash
chronos voice enable --agent agent_abc123
```

### Explore Templates
Use pre-built blueprints:
```bash
chronos blueprints list
```

### Build a Multi-Agent System
Create specialized agents that work together:
```python
group = client.agent_groups.create(
    name="Support Team",
    agents=[support_agent, billing_agent, technical_agent]
)
```

## Quick Reference

### CLI Commands
```bash
# List agents
chronos agent list

# Get agent info
chronos agent info agent_abc123

# Delete agent
chronos agent delete agent_abc123

# View logs
chronos logs agent_abc123
```

### SDK Basics
```python
# Initialize
client = Chronos(api_key="sk_live_...")

# Agents
agents = client.agents.list()
agent = client.agents.get("agent_abc123")
response = client.agents.chat(agent_id, message)

# Tools
tools = client.tools.list()

# Voice
calls = client.voice.calls.list()
```

## Example Projects

### Simple Chatbot
```python
from chronos import Chronos

client = Chronos(api_key="sk_live_...")
agent_id = "agent_abc123"

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    
    response = client.agents.chat(agent_id, user_input)
    print(f"Agent: {response.message}")
```

### Voice Assistant
```python
# Initiate a voice call
call = client.voice.calls.create(
    agent_id="agent_voice_123",
    to="+1234567890"
)
```

## Need Help?

- [Documentation](/docs/intro)
- [Community Forum](https://community.chronos.studio)
- [Support](/docs/resources/support)
