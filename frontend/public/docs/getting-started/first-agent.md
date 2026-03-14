---
sidebar_position: 3
title: Your First Agent
---

# Build Your First Agent

This guide walks you through creating a functional AI agent from scratch — with custom tools, memory, and a connected integration.

## What We'll Build

A **personal research assistant** that can:
- Search the web for information
- Remember past conversations
- Save notes to a connected database
- Respond via Telegram or WhatsApp

## Step 1: Scaffold the Project

```bash
chronos init research-assistant --template blank
cd research-assistant
```

## Step 2: Define the Agent

Edit `agent.yaml`:

```yaml
name: research-assistant
description: A personal research assistant with web search and memory
version: 1.0.0

model: gemini-2.0-flash
temperature: 0.7
max_tokens: 4096

system_prompt: |
  You are a helpful research assistant. You search the web for accurate,
  up-to-date information and provide concise, well-sourced answers.
  You remember previous conversations and build on them.
  Always cite your sources with links.

memory:
  type: persistent
  ttl: 30d                    # Remember conversations for 30 days
  max_context_messages: 50    # Include last 50 messages in context

tools:
  - name: web_search
    builtin: true
    config:
      max_results: 5
  - name: save_note
    path: ./tools/save_note.py
  - name: recall_notes
    path: ./tools/recall_notes.py

channels:
  - type: api                 # Always available via REST API
  - type: telegram            # Connect to Telegram
    config:
      bot_token: ${TELEGRAM_BOT_TOKEN}
```

## Step 3: Create Custom Tools

### Save Note Tool

Create `tools/save_note.py`:

```python
from chronos.tools import tool

@tool(
    name="save_note",
    description="Save a research note for later reference"
)
async def save_note(title: str, content: str, tags: list[str] = []) -> str:
    """Save a note to the agent's knowledge base."""
    # Chronos handles storage automatically
    return f"Note saved: {title}"
```

### Recall Notes Tool

Create `tools/recall_notes.py`:

```python
from chronos.tools import tool

@tool(
    name="recall_notes",
    description="Search and retrieve previously saved notes"
)
async def recall_notes(query: str, limit: int = 5) -> list[dict]:
    """Search saved notes by semantic similarity."""
    # Chronos provides built-in vector search over saved notes
    return []  # Results populated by the platform
```

## Step 4: Test Locally

```bash
chronos dev
```

```
🤖 research-assistant is running locally
> Search for the latest developments in AI agent frameworks in 2026
Agent: I'll search for the latest information...
[tool:web_search] Searching "AI agent frameworks 2026 developments"

Here are the key developments in AI agent frameworks in 2026:

1. **CrewAI** raised $18M and launched multi-agent orchestration...
2. **LangGraph** introduced stateful agent workflows...
3. **Google ADK** became the standard for Gemini-based agents...

Sources:
- [TechCrunch: AI Agent Landscape 2026](https://techcrunch.com/...)
- [The Information: Agent Wars](https://theinformation.com/...)

> Save that as a note tagged "market-research"
Agent: [tool:save_note] Saving note...
Note saved: "AI Agent Frameworks 2026" with tags: market-research
```

## Step 5: Deploy to Production

```bash
chronos deploy --env production
```

Output:

```
✓ Agent "research-assistant" deployed
✓ API: https://api.mohex.org/agents/research-assistant
✓ Telegram: Connected (@your_bot_username)
✓ Memory: Persistent store initialized
```

## Step 6: Test the API

```bash
curl -X POST https://api.mohex.org/agents/research-assistant/chat \
  -H "Authorization: Bearer $CHRONOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "What did we discuss about AI frameworks?"}'
```

---

## What's Next?

- [Agent Tools](../agents/tools) — Build powerful custom tools
- [Memory Systems](../agents/memory) — Deep dive into agent memory
- [Voice AI](../voice-ai/getting-started) — Add voice to your agent
- [Blueprints](../agents/blueprints) — Save and share agent templates
