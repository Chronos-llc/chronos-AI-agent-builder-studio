---
sidebar_position: 6
title: Multi-Agent Systems
---

# Multi-Agent Systems

The Multi-Agent OS lets multiple agents collaborate on complex tasks. Instead of one monolithic agent, you compose specialized agents that work together.

## Why Multi-Agent?

| Single Agent | Multi-Agent |
|-------------|-------------|
| One model handles everything | Specialized models for each task |
| One long prompt | Focused, smaller prompts |
| All tools loaded | Tools scoped per agent |
| Complex debugging | Clear responsibility per agent |

## Architecture Patterns

### Coordinator Pattern

A central agent routes tasks to specialist agents:

```yaml
# coordinator.yaml
name: coordinator
description: Routes tasks to the right specialist
model: gemini-2.0-flash

subagents:
  - name: researcher
    agent: research-agent
    description: Handles web research and data gathering

  - name: writer
    agent: content-writer
    description: Creates written content and documentation

  - name: analyst
    agent: data-analyst
    description: Analyzes data and creates visualizations

routing:
  strategy: llm              # LLM decides which subagent to use
  fallback: coordinator      # Coordinator handles unmatched tasks
```

### Pipeline Pattern

Agents process tasks sequentially:

```yaml
# pipeline.yaml
name: content-pipeline
type: pipeline

stages:
  - agent: researcher
    input: user_request
    output: research_data

  - agent: writer
    input: research_data
    output: draft

  - agent: editor
    input: draft
    output: final_content

  - agent: publisher
    input: final_content
    output: published_url
```

### Parallel Pattern

Multiple agents work simultaneously:

```yaml
# parallel.yaml
name: market-analysis
type: parallel

agents:
  - name: competitor-researcher
    agent: competitor-agent
    task: "Research competitor ${company}"

  - name: market-data
    agent: data-agent
    task: "Gather market size data for ${industry}"

  - name: trend-analyst
    agent: trend-agent
    task: "Identify trends in ${industry}"

aggregator:
  agent: report-writer
  task: "Compile findings into a comprehensive report"
```

## Defining Multi-Agent Systems

### Via YAML

```yaml
# system.yaml
name: customer-success-team
description: AI team handling customer success

agents:
  support:
    model: gemini-2.0-flash
    system_prompt: Handle customer support inquiries
    tools: [ticket_lookup, knowledge_base, escalate]

  analyst:
    model: gemini-2.0-flash
    system_prompt: Analyze customer data and health scores
    tools: [crm_query, analytics_dashboard]

  success_manager:
    model: gemini-2.0-pro
    system_prompt: |
      You manage customer relationships.
      Coordinate between support and analytics.
    subagents: [support, analyst]
    tools: [email_send, calendar_schedule]

entry_point: success_manager
```

### Via Python SDK

```python
from chronos import ChronosClient, MultiAgentSystem

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
