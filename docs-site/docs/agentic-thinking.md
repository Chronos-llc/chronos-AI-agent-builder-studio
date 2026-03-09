---
id: agentic-thinking
title: Agentic Thinking
sidebar_label: Agentic Thinking
slug: /agentic-thinking
---

# Agentic Thinking (Beta / Experimental)

## Overview
Agentic Thinking is an experimental planning mode for premium users that mirrors internal human self-dialogue before action.  
Instead of immediately executing tools, the orchestrator agent first runs an internal reasoning loop using temporary dialogue subagents.

## Why It Exists
- Improve plan quality before tool execution.
- Reduce avoidable tool calls and retries.
- Expose transparent internal reasoning for auditability in Agent Suite.

## Availability
- Enabled only for `Pro` and `Enterprise` plans.
- Marked as `Beta / Experimental` in Studio and Agent Suite.

## Runtime Behavior
1. User toggles Agentic Thinking from Bot Settings or invokes it from Agent Suite chat.
2. Orchestrator starts a dialogue session for the active conversation.
3. Temporary dialogue agents are created with default model `gpt-4o`.
4. Dialogue agents are tool-less and only exchange reasoning messages.
5. Dialogue messages are persisted in conversation dialogue history.
6. When planning is complete, dialogue session is closed and temporary agents are discarded.
7. Orchestrator proceeds with execution against the final internal plan.

## Architecture
- API:
  - `POST /api/v1/agents/{id}/agentic-thinking/start`
  - `POST /api/v1/agents/{id}/agentic-thinking/stop`
  - `GET /api/v1/conversations/{id}/dialogues`
- Data model:
  - `dialogue_sessions`
  - `dialogue_messages`
  - `conversation_dialogues`
- Services:
  - `app/core/agentic_thinking.py` manages session lifecycle and internal dialogue records.

## Guardrails
- Plan gating checks user subscription before session start.
- Dialogues are internal-only and never granted tool execution directly.
- Internal logs are visible to the owner in Agent Suite via `Show Dialogue`.

