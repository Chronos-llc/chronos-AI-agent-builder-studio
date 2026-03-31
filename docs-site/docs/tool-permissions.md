---
id: tool-permissions
title: Tool Permissions
sidebar_label: Tool Permissions
slug: /tool-permissions
---

# Tool Permissions

## Overview

Tool Permissions give you fine-grained control over what actions the Aegis Agent is allowed to take, and whether those actions require your explicit approval before execution. Every tool available to the agent has a permission mode that determines how it behaves at runtime.

Getting tool permissions right is one of the most important parts of configuring a reliable and trustworthy agent — especially for agents that interact with external systems, send communications, or modify data.

---

## How Tools Are Gated

Tools in the Aegis Agent fall into two gating categories:

### Bot Integration Gating

**Bot integration tools** are capabilities tied to the agent's own platform-level integrations — things like reading conversation history, managing agent memory, or interacting with the Aegis platform itself. These tools are available to the agent by default without requiring external OAuth.

Bot integration tools are controlled through the **Agent Settings → Tool Permissions** panel and respect the approve/auto mode settings described below.

### OAuth Connector Gating

**OAuth connector tools** require an active, authenticated connection to a third-party service (e.g., Gmail, Slack, Google Calendar, Notion, GitHub). These tools are only available to the agent if:

1. A connector for the service has been added to your workspace
2. The connector has been explicitly granted to the agent
3. The OAuth token for the connection is valid and not expired

If a connector's OAuth token expires or is revoked, the agent will surface a notice in the chat thread and the tool will be unavailable until the connection is re-authenticated. You can manage connector authentication from the **Integrations Hub**.

---

## System Tools

System tools are built-in capabilities that are always available to the agent and do not require external connectors. These include:

| Tool | Description |
|---|---|
| **Web Search** | Search the web for current information |
| **Code Execution** | Run sandboxed code (Python, JavaScript, etc.) |
| **Document Parser** | Extract and process content from attached files |
| **Image Analysis** | Analyze and describe image content |
| **Calculator** | Perform precise numeric computations |

System tools are subject to the same approve/auto mode settings as other tools, but they are always present — they cannot be removed from the agent's toolset.

---

## Always-On Tools

Two categories of tools are permanently active and cannot be disabled or set to require approval:

### Memory Tools

Memory tools allow the agent to read from and write to its persistent memory store. These are always-on because disabling memory mid-conversation would create an inconsistent agent state. Memory tools include:

- Reading stored facts, preferences, and context from prior sessions
- Writing new observations or user-specified preferences to memory
- Searching memory for relevant context

You can view and edit the agent's memory contents from the **Memory** tab in Agent Settings.

### Cron / Scheduled Task Tools

Cron tools allow the agent to schedule and manage recurring tasks on your behalf. These are always-on because scheduled tasks may need to trigger autonomously without user interaction. Cron tools include:

- Creating scheduled tasks with a natural-language or cron-expression schedule
- Listing and cancelling existing scheduled tasks
- Triggering immediate one-off runs of a scheduled task

> **Important:** While cron tools are always-on, the *actions* those scheduled tasks perform when they run are still subject to the tool permissions configured at run time. A scheduled task that sends an email will respect the Gmail connector's permission mode when it executes.

---

## Permission Modes: Approve vs. Auto

Every non-always-on tool can be set to one of two execution modes:

### Auto Mode

In **Auto mode**, the agent executes the tool immediately when it decides to use it, without interrupting you for confirmation. The tool call is still recorded in a Tool Call Card in the chat thread for transparency, but no approval is required.

Use Auto mode for:
- Read-only operations (fetching data, searching, reading files)
- Low-risk actions you are comfortable with the agent taking autonomously
- High-frequency tools where interruptions would impair the agent's usefulness

### Approve Mode

In **Approve mode**, the agent pauses before executing the tool and surfaces a **Confirmation Card** in the chat thread. You must click **Approve** or **Reject** before the agent proceeds.

Use Approve mode for:
- Write operations (sending emails, creating calendar events, posting to Slack)
- Actions that interact with external parties
- Operations that modify or delete data
- Any tool where you want an audit trail with explicit human sign-off

---

## Confirmation Cards in Chat

When a tool in Approve mode is triggered, a **Confirmation Card** appears in the chat thread:

```
The agent wants to perform an action:

  Tool: Send Email (Gmail)
  To: client@example.com
  Subject: Project Update - March 2026
  Body: "Hi Sarah, following up on our last meeting..."

  [Approve]   [Reject]   [Edit & Approve]
```

### Card Controls

| Control | Behavior |
|---|---|
| **Approve** | The agent executes the tool immediately with the shown parameters |
| **Reject** | The tool call is cancelled; the agent may attempt an alternative approach |
| **Edit & Approve** | Opens an editable form of the tool's parameters before approving |

**Edit & Approve** is particularly useful for tools like email sending or message composition — you can review the generated content, make changes, and approve the modified version in one step without having to reject and re-prompt.

### Confirmation Card Timeout

Unanswered Confirmation Cards expire after **10 minutes** by default. When a card expires:

- The pending tool call is cancelled
- The agent receives a timeout notice and may either retry, attempt an alternative, or wait for your next message
- The expired card is visually updated in the chat thread to show it timed out

The timeout duration can be changed in **Agent Settings → Tool Permissions → Approval Timeout**.

---

## Configuring Tool Permissions

### From Agent Settings

1. Open your agent in Agent Builder
2. Navigate to **Settings → Tool Permissions**
3. Each connected tool is listed with its current mode (Auto / Approve / Disabled)
4. Click the mode badge next to any tool to cycle through available modes
5. Save your changes

### From the Chat Interface

You can also adjust tool permissions inline from the chat panel using the **Connector Picker** in the input bar. This provides per-message scoping (not permanent mode changes). For permanent changes, use Agent Settings.

### Bulk Configuration

For agents with many connectors, use the **Set all to Approve** or **Set all write tools to Approve** shortcuts in the Tool Permissions panel. These are recommended defaults for agents that interact with external services.

---

## Recommended Permission Policies

### Read-heavy research agents

| Tool category | Recommended mode |
|---|---|
| Web search, document reading | Auto |
| Database reads | Auto |
| Any write operation | Approve |

### Action-taking agents (email, calendar, CRM)

| Tool category | Recommended mode |
|---|---|
| Read/fetch operations | Auto |
| Creating records | Approve |
| Sending communications | Approve |
| Deleting or modifying records | Approve |

### Fully autonomous agents (scheduled/unattended)

For agents running on a schedule without a human actively watching:
- Set write tools to **Auto** only if you have independently verified the agent's judgment through supervised sessions
- Keep high-risk tools (send email, post to Slack, call external APIs with side effects) on **Approve** until you are confident in the agent's behavior
- Review the Tool Call Cards in the conversation history regularly to audit what the agent is doing

---

## Tool Permissions and Sub-Agents

When the orchestrator spawns sub-agents, each sub-agent inherits a scoped subset of the parent's tool permissions. Sub-agents respect the same approve/auto modes as the parent.

If a sub-agent triggers an Approve-mode tool, the Confirmation Card appears in the **main chat thread** (not inside the sub-agent's detail panel) so you always see approvals in one consistent place. See [Sub-Agents](./sub-agents.md) for full details.

---

## Related Topics

- [Sub-Agents](./sub-agents.md) — How tool permissions propagate to sub-agents
- [Chat & Browser Mode](./chat-browser-mode.md) — How Confirmation Cards and Connector Picker appear in the UI
- [Reasoning & Thinking Mode](./reasoning-thinking.md) — How Reasoning Mode influences tool-use decisions
