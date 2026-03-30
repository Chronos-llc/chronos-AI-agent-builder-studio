---
id: reasoning-thinking
title: Reasoning & Thinking Mode
sidebar_label: Reasoning & Thinking Mode
slug: /reasoning-thinking
---

# Reasoning & Thinking Mode

## Overview

Reasoning Mode (also called Thinking Mode) enables the Aegis Agent to perform an explicit internal deliberation step before responding or taking action. When active, the agent works through the problem — considering angles, catching potential mistakes, and forming a plan — before committing to a course of action.

This is distinct from the agent simply "being smart." Reasoning Mode allocates dedicated compute budget to the deliberation phase, producing noticeably more thorough analysis, better-structured plans, and fewer avoidable errors on complex tasks.

---

## Supported Providers

Reasoning Mode is available across all major model providers supported by Chronos AI. The mechanism differs slightly per provider but the user experience is uniform:

| Provider | Reasoning Mechanism |
|---|---|
| **OpenAI** | Extended thinking via `o1`, `o3`, and `o4` model variants |
| **Anthropic** | Extended thinking budget via Claude 3.5 / 3.7 Sonnet and Opus |
| **Google** | Deep Think via Gemini 2.0 / 2.5 Flash and Pro |
| **xAI (Grok)** | Think mode via Grok 3 and later |
| **DeepSeek** | Chain-of-thought reasoning via DeepSeek R1 and R2 |

You do not need to select a different model to enable Reasoning Mode — the toggle activates the appropriate reasoning capability for whichever model is currently configured for your agent.

---

## Enabling Reasoning Mode

Reasoning Mode is accessed via the **Plus (+) menu** in the Chat input bar:

1. Click the **+** icon at the left side of the input bar
2. Select **Reasoning** from the menu that appears
3. A reasoning indicator appears in the input bar confirming the mode is active
4. Send your message as normal

To disable Reasoning Mode, click the **+** icon again and deselect **Reasoning**, or click the reasoning indicator chip in the input bar.

Reasoning Mode applies per-message — it does not stay on permanently unless you enable it in the agent's default settings (see [Persisting Reasoning Mode](#persisting-reasoning-mode)).

---

## The Thinking Card

When Reasoning Mode is active, the agent's response begins with a **Thinking Card** — a collapsible block that shows the agent's internal deliberation before its final answer.

### What the Thinking Card Shows

The Thinking Card contains the agent's raw reasoning trace: the chain of thought it worked through before producing its response. This typically includes:

- Problem restatement and decomposition
- Consideration of multiple approaches
- Identification of edge cases or constraints
- Selection of a strategy and rationale

The Thinking Card is collapsed by default to keep the interface clean. Click **"Show thinking"** to expand it and inspect the full deliberation.

### Why Show the Thinking Trace?

Exposing the reasoning trace serves several purposes:

- **Auditability** — you can verify that the agent considered the right factors
- **Debugging** — if the final answer is wrong, the thinking trace often reveals where the reasoning went astray
- **Trust** — transparent reasoning is easier to evaluate than a response that appears from nowhere

The content of the Thinking Card is read-only. It is not editable and does not affect the agent's output retroactively.

---

## Think Harder Mode

**Think Harder** is an intensified version of Reasoning Mode available within the Plus menu. It allocates a larger compute and token budget to the deliberation step, instructing the model to reason more exhaustively before responding.

Use Think Harder when:

- The task involves multi-step logical reasoning or math
- You are dealing with a high-stakes decision and want maximum thoroughness
- Standard Reasoning Mode produced an answer that felt rushed or incomplete
- The problem requires synthesizing a large number of constraints simultaneously

### Think Harder vs. Standard Reasoning

| | Standard Reasoning | Think Harder |
|---|---|---|
| Deliberation depth | Moderate | Extensive |
| Response latency | Moderate increase | Significant increase |
| Token cost | Higher than standard | Highest |
| Best for | Most complex tasks | Highest-stakes tasks |

Think Harder is best reserved for genuinely complex problems — for routine tasks, standard Reasoning Mode or no reasoning at all will be faster and more cost-efficient.

---

## Reasoning Mode and Tools

When Reasoning Mode is enabled, the agent deliberates before deciding which tools to call, not just before producing text. This means:

- **Fewer unnecessary tool calls** — the agent reasons about whether a tool call is actually needed before making it
- **Better-sequenced tool use** — the agent plans the order of tool calls to minimize redundant fetches
- **Improved HITL interaction** — when the agent needs to pause for approval, its reasoning trace shows why it wanted to take that action, making approval decisions easier

Reasoning Mode does not bypass tool permission checks. All approval requirements remain in effect regardless of whether the agent is in Reasoning Mode.

---

## Persisting Reasoning Mode

To enable Reasoning Mode as the default for all messages to an agent:

1. Open the **Agent Settings** panel
2. Navigate to **Model & Behavior**
3. Enable the **Always use Reasoning Mode** toggle
4. Optionally select **Think Harder as default** for maximum deliberation on every message

When always-on reasoning is enabled, the reasoning indicator appears permanently in the input bar and the Thinking Card will be present on every response.

> **Note:** Enabling Think Harder as the default will increase per-message token usage significantly. Monitor your usage on the Billing page if you enable this on high-traffic agents.

---

## Plan Availability

| Plan | Reasoning Mode | Think Harder |
|---|---|---|
| Free | Limited (up to 10 uses/day) | Not available |
| Starter | Available | Limited |
| Pro | Available | Available |
| Enterprise | Available | Available + custom budget |

Reasoning Mode uses additional tokens per message. These tokens are counted against your plan's token quota.

---

## Tips for Getting the Most from Reasoning Mode

- **Enable it for complex questions**, not simple lookups. "What's the capital of France?" doesn't benefit from Reasoning Mode. "Design an architecture for a multi-tenant SaaS application that handles 10,000 concurrent users" does.
- **Read the Thinking Card** when an answer surprises you — the deliberation trace usually explains how the agent arrived at its conclusion.
- **Use Think Harder sparingly** — it has a real cost and latency impact. Use it when the quality of the answer genuinely matters more than speed.
- **Combine with Sub-Agents** — the orchestrator uses its reasoning budget to plan sub-agent decomposition more effectively when Reasoning Mode is on.

---

## Related Topics

- [Sub-Agents](./sub-agents.md) — How Reasoning Mode improves orchestrator planning for parallel tasks
- [Chat & Browser Mode](./chat-browser-mode.md) — Where the Plus menu and Thinking Card appear in the UI
- [Tool Permissions](./tool-permissions.md) — How Reasoning Mode interacts with approval flows
