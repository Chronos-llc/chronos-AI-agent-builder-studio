---
sidebar_position: 1
title: Platform Overview
---

# Platform Overview

Chronos Studio consolidates the entire agent creation lifecycle — from design through tool integration, voice model selection, and production deployment — into one orchestrated environment.

## The Problem We Solve

The AI landscape is fragmented. Developers navigate:
- Disjointed tools for text-based agents
- Separate platforms for voice synthesis
- Disconnected pipelines for deployment
- No unified memory or state management

Chronos Studio resolves this systemic inefficiency.

## Platform Architecture

```
┌────────────────────────────────────────────────────────┐
│                    User Interfaces                      │
│   Dashboard  │  CLI  │  SDKs  │  Jestha Workspace      │
├────────────────────────────────────────────────────────┤
│                    Spark Engine                         │
│          Natural Language → Agent Blueprint              │
├────────────────────────────────────────────────────────┤
│                   Agent Runtime                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐ │
│  │ General  │  │  Voice  │  │  Multi  │  │ Blueprint│ │
│  │ Agents   │  │ Agents  │  │ -Agent  │  │ Registry │ │
│  └─────────┘  └─────────┘  └─────────┘  └──────────┘ │
├────────────────────────────────────────────────────────┤
│                  Infrastructure                         │
│  Memory  │  Tools  │  MCP  │  Channels  │  Analytics   │
├────────────────────────────────────────────────────────┤
│                  Cloud Platform                         │
│  Compute  │  Storage  │  CDN  │  Monitoring  │  SLA    │
└────────────────────────────────────────────────────────┘
```

## Core Products

### 1. General AI Agents
Build intelligent agents equipped with custom tools, memory systems, and autonomous decision-making. Connect to external APIs, databases, and social media ecosystems.

**Key Features:**
- Multiple LLM providers (Gemini, GPT, Claude, open-source)
- Custom and built-in tool support
- Persistent memory with vector search
- Multi-channel deployment

### 2. Voice AI Agents
Deploy real-time voice agents engineered for human-grade conversation.

**Key Features:**
- Sub-second latency for natural conversation
- Emotional awareness and sentiment detection
- Human-like vocal fidelity
- Enterprise-grade telephony (99.9% SLA)
- SIP/WebRTC/PSTN support

### 3. Spark — The Agent Builder
A meta-agent that creates other agents from natural language descriptions.

**Key Features:**
- Describe intent → receive complete agent blueprint
- Auto-generates tools, prompts, and configurations
- Iterative refinement through conversation
- One-click deployment

### 4. Jestha — Agentic Workspace
The end-user product — a copilot workspace where agents and humans collaborate.

**Key Features:**
- Unified workspace for all your agents
- Natural language task delegation
- Cross-agent orchestration
- Real-time collaboration

## No-Code to Pro-Code

Chronos serves every skill level:

| Level | Interface | Best For |
|-------|-----------|----------|
| **No-Code** | Dashboard + Spark | Non-technical users, rapid prototyping |
| **Low-Code** | YAML configs + CLI | Developers who want control without boilerplate |
| **Pro-Code** | SDKs + Custom Tools | Full programmatic control, complex architectures |

## Deployment Options

- **Chronos Cloud** — Fully managed, auto-scaling, global edge
- **Self-Hosted** — Deploy on your own infrastructure
- **Hybrid** — Cloud runtime with on-premise data stores

---

## Next Steps

- [Dashboard Guide](./dashboard) — Navigate the web interface
- [Spark](./spark) — Build agents with natural language
- [Jestha Workspace](./jestha) — The copilot experience
