---
sidebar_position: 4
title: Memory
---

# Agent Memory

Memory gives agents context that persists across conversations. Without memory, every interaction starts from zero. With memory, agents learn user preferences, build knowledge, and maintain continuity.

## Memory Types

### Session Memory

Exists only during a single conversation. Automatically cleared when the conversation ends.

```yaml
memory:
  type: session
  max_context_messages: 20
```

**Use for:** Chatbots, one-off interactions, stateless assistants.

### Persistent Memory

Survives across conversations. Agents remember past interactions and build on them.

```yaml
memory:
  type: persistent
  ttl: 90d                       # Auto-expire after 90 days
  max_context_messages: 50       # Include recent messages in context
  vector_search: true            # Enable semantic search
  per_user: true                 # Separate memory per user
```

**Use for:** Personal assistants, support agents, research tools.

### Key-Value Memory

Simple structured storage for settings, preferences, and state.

```yaml
memory:
  type: persistent
  kv_store: true
```

```python
# In a custom tool
from chronos.memory import kv

# Store a value
await kv.set("user_preference_language", "en")

# Retrieve a value
lang = await kv.get("user_preference_language")

# Delete
await kv.delete("user_preference_language")
```

### Vector Memory

Semantic search over stored information. Perfect for knowledge bases and RAG.

```yaml
memory:
  type: persistent
  vector_search: true
  embedding_model: text-embedding-004
  similarity_threshold: 0.7
```

```python
from chronos.memory import vector

# Store a document
await vector.store(
    content="Chronos Studio supports multi-agent orchestration...",
    metadata={"source": "docs", "topic": "features"}
)

# Semantic search
results = await vector.search(
    query="How do agents work together?",
    limit=5
)
```

## Memory in Action

### Example: Support Agent with Memory

```
--- Conversation 1 (Monday) ---
User: "I'm having trouble with my billing. My account is jesse@example.com"
Agent: [Looks up account, resolves billing issue]
Agent: [Stores: user_email = jesse@example.com, issue = billing]

--- Conversation 2 (Wednesday) ---
User: "Hey, me again. Different issue this time."
Agent: "Welcome back, Jesse! I see we resolved a billing issue on Monday.
        What can I help you with today?"
```

### Example: Research Assistant with Vector Memory

```
--- Session 1 ---
User: "Research the AI agent market size for 2026"
Agent: [Searches web, stores findings in vector memory]

--- Session 2 ---
User: "What did we find about the agent market?"
Agent: [Searches vector memory, retrieves stored research]
Agent: "Based on our earlier research, the AI agent market is projected
        to reach $XX billion by 2026, driven by..."
```

## Memory Configuration Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | string | `session` | `session`, `persistent`, or `none` |
| `ttl` | string | `30d` | Time to live (persistent only) |
| `max_context_messages` | int | `20` | Messages in context window |
| `vector_search` | bool | `false` | Enable semantic search |
| `per_user` | bool | `true` | Separate memory per user |
| `kv_store` | bool | `false` | Enable key-value storage |
| `embedding_model` | string | auto | Model for vector embeddings |
| `similarity_threshold` | float | `0.7` | Minimum similarity for vector search |

## Best Practices

1. **Start with session memory** — Add persistence only when needed
2. **Set TTLs** — Don't store data forever; set appropriate expiry
3. **Use per-user memory** — Keep user data isolated
4. **Combine memory types** — Use KV for settings, vector for knowledge
5. **Monitor storage** — Track memory usage in the dashboard

---

## Next Steps

- [Blueprints](./blueprints) — Save agent configurations as templates
- [Multi-Agent Systems](./multi-agent) — Share memory across agents
