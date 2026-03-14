---
sidebar_position: 4
title: Jestha — Agentic Workspace
---

# Jestha — Agentic Workspace

Jestha is the copilot and agentic workspace application built on top of Chronos Studio. It's where humans and AI agents collaborate in a unified environment.

## What Is Jestha?

Think of Jestha as your AI-powered workspace — a place where you interact with multiple agents, delegate tasks, and orchestrate complex workflows through natural language.

## Key Features

### Unified Agent Access
Interact with all your Chronos agents from a single workspace. No switching between apps or endpoints.

```
You → Jestha: "Research the top 5 competitors in the voice AI space
               and create a comparison spreadsheet"

Jestha → [Routes to research-agent] → [Routes to doc-agent]
      → "Here's your competitor analysis. I've created a spreadsheet
         with 5 companies compared across 12 dimensions."
```

### Task Delegation
Describe complex tasks in plain language. Jestha breaks them down and routes to the right agents.

### Cross-Agent Orchestration
Jestha coordinates multiple agents working together:

```
"Summarize yesterday's sales calls, identify action items,
 and create follow-up email drafts for each prospect."

→ voice-transcriber: Processes call recordings
→ summarizer: Creates meeting summaries
→ action-extractor: Identifies follow-ups
→ email-drafter: Generates personalized emails
→ Jestha: Presents everything in one organized view
```

### Workspace Features

- **Conversations** — Persistent chat threads with context
- **Files & Documents** — Share and process files with agents
- **Workflows** — Save multi-step processes as reusable workflows
- **Notifications** — Get updates on agent tasks and completions
- **Team Collaboration** — Share agents and workflows with your team

## Getting Started with Jestha

### 1. Open the Workspace

Navigate to [jestha.mohex.org](https://jestha.mohex.org) or use the desktop app.

### 2. Connect Your Agents

All agents deployed on Chronos Studio are automatically available in Jestha. You can also connect external agents via MCP.

### 3. Start a Conversation

Just type naturally:

- "Help me write a blog post about AI agents"
- "Analyze this CSV and create a chart"
- "Schedule a meeting with the engineering team for next Tuesday"
- "What did we discuss about the product roadmap last week?"

### 4. Create Workflows

Save frequently used multi-step processes:

```
Workflow: "Daily Briefing"
Steps:
  1. Summarize unread emails
  2. List today's calendar events
  3. Check project status in Linear
  4. Generate a prioritized task list
Trigger: Every day at 8:00 AM
```

## Jestha vs. Direct Agent Access

| Feature | Direct API/Chat | Jestha Workspace |
|---------|----------------|------------------|
| Single agent interaction | ✓ | ✓ |
| Multi-agent orchestration | Manual | Automatic |
| Persistent context | Per agent | Across all agents |
| File handling | Limited | Full support |
| Saved workflows | ✗ | ✓ |
| Team collaboration | ✗ | ✓ |

---

## Next Steps

- [Creating Agents](../agents/creating-agents) — Build agents for your workspace
- [Integrations](../integrations/overview) — Connect external tools
- [Guides](../guides/workflow-automation) — Real-world workflow examples
