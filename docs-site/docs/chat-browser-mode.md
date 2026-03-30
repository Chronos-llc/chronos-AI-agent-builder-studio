---
id: chat-browser-mode
title: Chat & Browser Mode
sidebar_label: Chat & Browser Mode
slug: /chat-browser-mode
---

# Chat & Browser Mode

## Overview

The Aegis UI Agent provides two primary interaction modes accessible from the top of the agent panel: **Chat Mode** and **Browser Mode**. Each mode gives you a different interface surface depending on whether you want to converse with your agent or observe it operating a live browser session.

Switching between modes is instant — the agent's context and memory are preserved regardless of which mode is active.

---

## Switching Between Modes

A toggle control at the top of the Aegis Agent panel lets you switch between Chat and Browser mode at any time.

| Mode | What you see |
|---|---|
| **Chat** | Conversational message thread with tool call cards, file attachments, and input controls |
| **Browser** | Live browser viewport showing the agent's active web session |

> **Note:** Browser Mode is only available when the agent has at least one browser-capable tool enabled. If no browser integration is configured, the toggle will default to Chat Mode.

---

## Chat Mode

Chat Mode is the primary interface for interacting with the Aegis Agent through natural language. It presents a scrollable conversation thread and a rich input bar at the bottom.

### Conversation Thread

The conversation thread displays:

- **Your messages** — plain text or rich input (file attachments, voice transcripts)
- **Agent responses** — markdown-rendered prose, code blocks, and structured cards
- **Tool call cards** — expandable cards showing which tools the agent invoked, their inputs, and their outputs
- **System notices** — inline status updates such as "Agent is thinking…" or "Awaiting your approval"

#### Tool Call Cards

Every time the agent invokes a tool, a collapsible **Tool Call Card** is inserted into the thread. Each card shows:

- The tool name and the integration it belongs to (e.g., `web_search` via Search Connector)
- The input parameters the agent passed to the tool
- The result returned, truncated with a "Show more" control for long outputs
- Timing information (how long the tool call took)

Tool Call Cards are read-only. They exist purely for transparency and auditability — you can review exactly what the agent did and why at any point in the conversation.

#### Code Cards

When the agent returns code — whether as part of an explanation or as a runnable artifact — it is rendered in a **Code Card** with:

- Syntax highlighting based on the detected language
- A **Copy** button in the top-right corner that copies the full code block to your clipboard with one click
- An optional language label (e.g., `python`, `sql`, `bash`)

Code Cards are also used to display structured outputs like JSON payloads and configuration files.

---

### Input Bar

The input bar at the bottom of the Chat panel contains several controls beyond the standard text field.

#### Connector Picker

The **Connector Picker** (the plug icon in the input bar) lets you scope the agent's tool access for your next message. Clicking it opens a popover listing all connectors currently available to the agent. You can:

- Enable or disable individual connectors for a single turn
- Restrict the agent to only a subset of its tools when you want tighter control
- Re-enable all connectors at any time

Changes to the connector scope apply only to the current message — subsequent messages revert to the agent's default connector configuration unless you make another selection.

#### File Attachments

Click the **paperclip icon** or drag and drop files into the input bar to attach files to your message. The agent can process the content of attached files as part of its response.

Supported file types include:

- Documents: `.pdf`, `.docx`, `.txt`, `.md`, `.csv`
- Images: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`
- Spreadsheets: `.xlsx`, `.xls`
- Code files: most plain-text source formats

Attached files are displayed as chips above the text field before you send. You can remove a file by clicking the × on its chip. File size limits depend on your plan.

#### Voice Input

Click the **microphone icon** to activate voice input. The agent will:

1. Record your spoken input via your device microphone
2. Transcribe it using speech-to-text
3. Populate the text field with the transcript so you can review and edit it before sending

Voice input is an additive feature — the transcript goes into the same text field as typed input, so you can combine voice and text freely. The transcript is editable before submission.

> **Permissions:** Your browser will request microphone access the first time you use voice input. This permission is required and can be revoked from your browser settings at any time.

---

## Browser Mode

Browser Mode gives you a live view into the agent's active browser session. When the agent is performing web-based tasks — navigating pages, filling forms, scraping content, or clicking through interfaces — you can watch it happen in real time inside the panel.

### The Browser Viewport

The viewport renders a full, interactive preview of the browser the agent controls. You can:

- Observe page navigation and interactions as they happen
- Pause or interrupt the agent if it appears to be going down the wrong path
- Review the current URL and page title in the viewport header

The viewport is **read-only by default** — the agent drives the browser, not you. However, depending on your agent's configuration, Human-in-the-Loop (HITL) checkpoints may pause execution and ask you to confirm a specific action before the agent proceeds. See [Tool Permissions](./tool-permissions.md) for details.

### Switching Back to Chat

At any point during a browser session, you can switch back to Chat Mode to send follow-up instructions, review the conversation history, or redirect the agent. The browser session continues running in the background until the agent completes its task or you explicitly stop it.

---

## Tips and Best Practices

- **Use the Connector Picker** when you want to run a quick query and don't want the agent reaching out to external APIs unnecessarily.
- **Attach files** rather than pasting large text blocks — the agent processes attachments more efficiently than inline text for structured documents.
- **Use Code Card copy buttons** to quickly grab agent-generated scripts or queries without re-typing.
- **Switch to Browser Mode** when you've asked the agent to complete a multi-step web task and want to verify it's on track.
- **Voice input** is particularly useful on mobile or when drafting longer instructions.

---

## Related Topics

- [Sub-Agents](./sub-agents.md) — How the agent spawns and orchestrates parallel sub-agents
- [Tool Permissions](./tool-permissions.md) — Controlling which tools the agent can use and when
- [Reasoning & Thinking Mode](./reasoning-thinking.md) — Enabling deeper planning before the agent acts
