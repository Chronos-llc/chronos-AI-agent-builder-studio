---
sidebar_position: 2
title: Dashboard
---

# Dashboard

The Chronos Studio Dashboard is your central hub for managing agents, monitoring performance, and configuring your workspace.

## Accessing the Dashboard

Navigate to [app.mohex.org](https://app.mohex.org) and sign in with your Chronos account.

## Dashboard Sections

### Home

The home view shows:
- **Active Agents** — All deployed agents with status indicators
- **Recent Activity** — Latest conversations, tool calls, and events
- **Usage Metrics** — API calls, token usage, and costs for the current period
- **Quick Actions** — Create agent, import blueprint, open Spark

### Agents

Manage all your agents from one view:

- **List View** — See all agents with status, last active, and message count
- **Agent Detail** — Configuration, logs, analytics, and connected channels
- **Live Testing** — Chat with any agent directly from the dashboard
- **Version History** — Track changes and roll back configurations

### Spark Studio

The visual agent builder powered by Spark:

1. Describe your agent in natural language
2. Spark generates a blueprint
3. Review and customize tools, prompts, and settings
4. Deploy with one click

### Analytics

Track agent performance:

- **Conversation Metrics** — Total conversations, avg length, resolution rate
- **Tool Usage** — Which tools are called most, success/failure rates
- **Latency** — Response times (P50, P95, P99)
- **User Satisfaction** — Ratings and feedback scores
- **Cost Tracking** — Token usage and estimated costs by agent

### Integrations

Connect external services:

- **MCP Servers** — Add and manage MCP connections
- **Messaging Channels** — Configure Telegram, WhatsApp, Slack bots
- **API Keys** — Manage third-party API credentials
- **Webhooks** — Set up event notifications

### Settings

- **Workspace** — Team members, roles, permissions
- **Billing** — Plan details, usage, invoices
- **API Keys** — Generate and manage Chronos API keys
- **Security** — 2FA, audit logs, access controls

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Command palette |
| `Cmd/Ctrl + N` | New agent |
| `Cmd/Ctrl + S` | Save changes |
| `Cmd/Ctrl + D` | Deploy current agent |

---

## Next Steps

- [Spark Agent Builder](./spark) — Create agents with natural language
- [API Reference](../api-reference/overview) — Programmatic access
