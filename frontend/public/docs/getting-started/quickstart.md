---
sidebar_position: 1
title: Quickstart
---

# Quickstart

Get your first Chronos AI agent running in under 5 minutes.

## Prerequisites

- Node.js 18+ or Python 3.10+
- A Chronos Studio account ([sign up](https://mohex.org))

## Step 1: Install the CLI

```bash
npm install -g @chronos-studio/cli
```

Or with Python:

```bash
pip install chronos-studio
```

## Step 2: Authenticate

```bash
chronos login
```

This opens your browser for authentication. Once complete, your API key is stored locally.

## Step 3: Create an Agent

```bash
chronos init my-agent --template starter
```

This scaffolds a new agent project:

```
my-agent/
├── agent.yaml          # Agent configuration
├── tools/              # Custom tool definitions
│   └── example.py
├── prompts/            # System prompts & templates
│   └── system.md
└── tests/              # Agent test cases
    └── test_basic.py
```

## Step 4: Configure Your Agent

Edit `agent.yaml`:

```yaml
name: my-agent
description: My first Chronos AI agent
model: gemini-2.0-flash
memory:
  type: persistent
  store: default
tools:
  - name: web_search
    builtin: true
  - name: calculator
    builtin: true
  - name: custom_tool
    path: ./tools/example.py
personality:
  tone: professional
  style: concise
```

## Step 5: Test Locally

```bash
chronos dev
```

This starts an interactive session where you can chat with your agent:

```
🤖 Agent "my-agent" is running locally
> What's the weather in Lagos?
Agent: Let me search for that...
[tool:web_search] Searching "weather in Lagos today"
The current weather in Lagos is 28°C with partly cloudy skies...
```

## Step 6: Deploy

```bash
chronos deploy
```

Your agent is now live and accessible via:
- **API endpoint**: `https://api.mohex.org/agents/my-agent`
- **Dashboard**: View in the Chronos Studio dashboard
- **Messaging**: Connect to WhatsApp, Telegram, Slack, and more

---

## What's Next?

- [Core Concepts](./concepts) — Understand agents, tools, memory, and blueprints
- [Creating Agents](../agents/creating-agents) — Deep dive into agent configuration
- [Voice AI](../voice-ai/getting-started) — Add voice capabilities to your agent
- [Connect Integrations](../integrations/overview) — Link your agent to external services
