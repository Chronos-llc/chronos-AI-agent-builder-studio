---
sidebar_position: 4
title: Core Concepts
---

# Core Concepts

Understand the foundational building blocks of Chronos Studio.

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                  Chronos Studio                  │
├─────────────────────────────────────────────────┤
│  Channels          │  Dashboard & API            │
│  (Telegram, WA,    │  (Web UI, REST API,         │
│   Slack, Voice)    │   CLI, SDKs)                │
├─────────────────────────────────────────────────┤
│                 Agent Runtime                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  Models   │ │  Tools   │ │  Memory & State  │ │
│  │  (LLMs)  │ │  (Custom │ │  (Persistent,    │ │
│  │          │ │  +Built  │ │   Vector, KV)    │ │
│  │          │ │   -in)   │ │                  │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
├─────────────────────────────────────────────────┤
│              Integration Layer                   │
│  MCP Servers │ External APIs │ Databases │ ...  │
└─────────────────────────────────────────────────┘
```

## Key Concepts

### Agents

An **agent** is an autonomous AI system that can reason, use tools, maintain memory, and communicate through multiple channels. Every agent in Chronos has:

- **Model**: The underlying LLM (Gemini, GPT, Claude, open-source)
- **System Prompt**: Instructions defining personality and behavior
- **Tools**: Functions the agent can call to take actions
- **Memory**: Persistent context across conversations
- **Channels**: Where the agent communicates (API, messaging apps, voice)

### Tools

**Tools** extend what your agent can do beyond text generation. They are functions your agent can call autonomously.

```python
@tool(name="send_email", description="Send an email to a recipient")
async def send_email(to: str, subject: str, body: str) -> str:
    # Your implementation
    return "Email sent successfully"
```

Chronos provides **built-in tools** (web search, calculators, file operations) and supports **custom tools** you define in Python.

### Memory

**Memory** gives agents context across conversations:

| Type | Description | Use Case |
|------|-------------|----------|
| **Session** | Within a single conversation | Chat context |
| **Persistent** | Across conversations, per user | User preferences, history |
| **Vector** | Semantic search over stored data | Knowledge bases, RAG |
| **Key-Value** | Simple structured storage | Settings, counters |

### Blueprints

**Blueprints** are reusable agent templates. Clone, customize, and deploy — without starting from scratch.

```bash
# Use a community blueprint
chronos create --from blueprint:customer-support

# Save your agent as a blueprint
chronos blueprint save my-agent --name "Research Assistant v2"
```

### Multi-Agent Systems

The **Multi-Agent OS** lets agents collaborate. Agents can inherit prebuilt subagents for complex workflows:

```yaml
agents:
  - name: coordinator
    role: Orchestrates the research pipeline
    subagents:
      - researcher    # Searches and gathers information
      - summarizer    # Condenses findings
      - fact-checker  # Verifies claims
```

### Spark — The Meta-Agent

**Spark** is a meta-agent that builds other agents. Describe what you want in plain English:

> "I need an agent that monitors Twitter for mentions of my brand, summarizes sentiment daily, and sends me a Telegram digest."

Spark generates the complete agent configuration — tools, prompts, integrations — ready to deploy.

### Channels

**Channels** are how users interact with agents:

- **API** — REST endpoints for programmatic access
- **Messaging** — Telegram, WhatsApp, Slack, Discord
- **Voice** — Phone calls, WebRTC, SIP
- **Web Widget** — Embeddable chat component

### MCP (Model Context Protocol)

Chronos supports **MCP servers** — a standard protocol for connecting AI models to external data sources and tools. Host your own MCP servers or connect to existing ones.

---

## Platform Components

| Component | What It Does |
|-----------|-------------|
| **Chronos Studio** | The full platform — everything below in one stack |
| **Spark** | Natural language agent builder (meta-agent) |
| **Jestha** | Copilot & agentic workspace app for end users |
| **Agent Runtime** | Execution environment for deployed agents |
| **Dashboard** | Web UI for managing agents, analytics, and settings |
| **CLI** | Command-line tool for development and deployment |
| **SDKs** | Python and JavaScript libraries for API access |

---

## Next Steps

- [Create Your First Agent](./first-agent) — Hands-on tutorial
- [Agent Tools Deep Dive](../agents/tools) — Build powerful tools
- [Voice AI Overview](../voice-ai/overview) — Add voice capabilities
