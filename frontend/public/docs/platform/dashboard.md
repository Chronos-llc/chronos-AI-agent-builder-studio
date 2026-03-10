---
sidebar_position: 2
title: Dashboard Guide
---

# Dashboard Guide

The Chronos Studio dashboard provides a comprehensive interface for managing your agents and viewing analytics.

## Getting Started

### Navigation

```
Dashboard
├── Overview (home)
├── Agents
│   ├── List
│   ├── Create
│   └── Analytics
├── Voice
│   ├── Agents
│   ├── Calls
│   └── Numbers
├── Integrations
├── Analytics
├── Settings
│   ├── Profile
│   ├── Team
│   ├── Billing
│   └── API Keys
```

## Agent Management

### Creating Agents

1. Click **Agents** → **Create New**
2. Choose agent type
3. Configure settings
4. Test in simulator
5. Deploy

### Agent Cards

Each agent shows:
- Status indicator (active/inactive)
- Type icon
- Message count
- Average rating
- Quick actions

### Bulk Operations

Select multiple agents to:
- Start/stop
- Delete
- Export configuration
- Apply templates

## Analytics

### Overview Dashboard

Key metrics:
- **Total Conversations**: All-time messages
- **Active Users**: Unique users today
- **Avg Response Time**: Latency
- **Success Rate**: Task completion

### Agent Analytics

Per-agent metrics:
- Conversation volume over time
- Response distribution
- Tool usage breakdown
- Error rates
- User satisfaction

### Custom Reports

```bash
# Generate custom report
chronos reports generate \
  --agents agent_1,agent_2 \
  --metrics messages,tokens,cost \
  --date_range "last_30_days" \
  --format csv
```

## Settings

### Organization Settings

- Organization name
- Logo and branding
- Default timezone
- Data retention policies

### Team Management

Invite team members:
```bash
# Invite user
chronos team invite user@example.com --role admin

# List team
chronos team list

# Update role
chronos team update user@example.com --role viewer
```

### Billing

- View current plan
- Usage breakdown
- Payment methods
- Download invoices

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Quick search |
| `Ctrl+N` | New agent |
| `Ctrl+S` | Save |
| `Esc` | Close modal |

## Customization

### Dashboard Theme

```json
{
  "theme": {
    "mode": "dark",
    "accent_color": "#0066FF",
    "sidebar_collapsed": false
  }
}
```

### Saved Views

Save frequently used filters:

```bash
chronos views create \
  --name "Active Support Agents" \
  --filters "status=active,type=conversational"
```

## API Access

### Generating API Keys

1. Go to **Settings** → **API Keys**
2. Click **Create New Key**
3. Set name and permissions
4. Copy and store securely

### SDK Configuration

```python
from chronos import Chronos

client = Chronos(
    api_key=os.getenv("CHRONOS_API_KEY"),
    organization=os.getenv("CHRONOS_ORG_ID")
)
```

## Best Practices

1. **Regular monitoring** - Check analytics daily
2. **Organize agents** - Use tags and folders
3. **Set alerts** - Configure notifications
4. **Document** - Keep notes on configurations
