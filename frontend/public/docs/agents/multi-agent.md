---
sidebar_position: 5
title: Multi-Agent Systems
---

# Multi-Agent Systems

Multi-agent systems enable multiple specialized agents to collaborate on complex tasks, each handling different aspects of a workflow.

## Basic Setup

```python
client = ChronosClient(api_key="your_key")

system = MultiAgentSystem(
    name="research-team",
    agents={
        "researcher": client.agents.get("web-researcher"),
        "summarizer": client.agents.get("text-summarizer"),
        "fact_checker": client.agents.get("fact-checker"),
    },
    coordinator={
        "model": "gemini-2.0-flash",
        "routing": "llm",
    }
)

# Run the system
result = await system.run(
    "Research the latest developments in quantum computing "
    "and give me a fact-checked summary"
)
```

## Shared Memory

Agents in a system can share memory:

```yaml
shared_memory:
  type: persistent
  scope: system              # All agents share this memory
  vector_search: true

agents:
  researcher:
    memory:
      shared: true           # Access shared memory
      private: true          # Also has private memory
```

## Communication Between Agents

Agents communicate via structured messages:

```python
# Agent A sends a task to Agent B
await self.delegate(
    to="analyst",
    task="Analyze this customer's usage data",
    context={"customer_id": "cust_123"},
    wait=True                # Wait for response
)
```

## Monitoring Multi-Agent Systems

The dashboard shows:
- **System View** — Visual graph of agent interactions
- **Message Flow** — Track messages between agents
- **Per-Agent Metrics** — Latency, tool usage, errors per agent
- **Bottleneck Detection** — Identify slow agents in pipelines

---

## Next Steps

- [Voice AI](../voice-ai/overview) — Add voice to your agent systems
- [Integrations](../integrations/overview) — Connect external services
