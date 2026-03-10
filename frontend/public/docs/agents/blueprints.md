---
sidebar_position: 2
title: Agent Blueprints
---

# Agent Blueprints

Agent blueprints are pre-configured agent templates that provide a starting point for common use cases. They include predefined configurations, tools, prompts, and behaviors that you can customize for your specific needs.

## Voice Configuration

Blueprints include built-in voice capabilities with configurable settings:

```yaml
voice:
  provider: "elevenlabs"  # or "cartesia", "custom"
  voice_id: "rachel"
  model: "eleven_multilingual_v2"
  stability: 0.5
  similarity_boost: 0.75
  style: 0.5
  speaker_boost: true
  latency_optimization: 4
```

### Voice Providers

| Provider | Languages | Features |
|----------|-----------|----------|
| ElevenLabs | 29+ | Real-time, emotion control |
| Cartesia | 80+ | Ultra-low latency |
| Custom | Any | Full control |

### Voice Settings

- **stability**: Controls consistency (0-1)
- **similarity_boost**: How closely to match voice (0-1)
- **style**: Emotional range (0-1)
- **latency_optimization**: 0-10 scale for speed vs quality

## Blueprint Variables

Blueprints support dynamic variables that can be customized at runtime:

```yaml
variables:
  company_name:
    type: string
    required: true
    description: "Your company name"
  support_email:
    type: string
    required: true
  max_ticket_age_days:
    type: number
    default: 30
  escalation_threshold:
    type: number
    default: 3
```

### Variable Types

- **string**: Text values
- **number**: Numeric values
- **boolean**: True/false flags
- **enum**: Predefined options
- **secret**: Encrypted sensitive values

### Using Variables in Prompts

```yaml
system_prompt: |
  You are a support agent for {{company_name}}.
  Contact: {{support_email}}
  Handle tickets older than {{max_ticket_age_days}} days as priority.
```

## Sharing Blueprints

### Export Command

```bash
chronos blueprint export customer-support-agent \
  --output ./my-blueprint.yaml
```

### Import Command

```bash
chronos blueprint import ./my-blueprint.yaml
```

### Share via Registry

```bash
# Login to blueprint registry
chronos login

# Publish to organization
chronos blueprint publish customer-support \
  --org my-company \
  --visibility private

# Publish publicly
chronos blueprint publish customer-support \
  --visibility public
```

### Clone a Blueprint

```bash
chronos blueprint clone customer-support my-custom-support
```

## Popular Blueprints

The following blueprints are available from the manifest:

| Blueprint ID | Name | Category | Use Case | Popularity |
|--------------|------|----------|----------|------------|
| customer-support | Customer Support Agent | Support | Helpdesk, FAQ, ticket handling | 98% |
| sales-assistant | Sales Assistant | Sales | Lead qualification, product recommendations | 95% |
| voice-receptionist | Voice Receptionist | Voice | Call handling, appointment scheduling | 92% |
| data-analyst | Data Analysis Agent | Analytics | SQL queries, visualizations, reports | 89% |
| research-assistant | Research Assistant | Research | Web search, summarization, citations | 87% |
| workflow-automation | Workflow Automation | Operations | Task orchestration, approvals | 85% |
| onboarding-agent | User Onboarding | Customer Success | Tutorials, walkthroughs | 83% |
| scheduler | Meeting Scheduler | Productivity | Calendar management, booking | 80% |
| hr-assistant | HR Assistant | HR | Policy questions, benefits info | 78% |
| it-helpdesk | IT Helpdesk | IT | Technical support, troubleshooting | 76% |

## Using Blueprints

### Via Dashboard

1. Navigate to the Agent Builder
2. Click "Create New Agent"
3. Browse the blueprint gallery
4. Select a blueprint
5. Configure variables
6. Customize settings
7. Deploy

### Via CLI

```bash
chronos agents create \
  --blueprint customer-support \
  --name "My Support Agent" \
  --variables company_name="Acme Corp" \
  --variables support_email="support@acme.com"
```

### Via API

```bash
POST /api/agents
{
  "blueprint": "customer-support",
  "name": "My Support Agent",
  "variables": {
    "company_name": "Acme Corp",
    "support_email": "support@acme.com"
  }
}
```

## Customizing Blueprints

Blueprints serve as starting points. You can customize:

- **System Prompts**: Modify agent behavior and personality
- **Tools**: Add or remove capabilities
- **Memory Settings**: Configure persistence and context
- **Integrations**: Connect to your services
- **UI/UX**: Customize chat interfaces and voice settings
- **Voice Config**: Adjust voice model and parameters

## Creating Custom Blueprints

Save your agent configurations as reusable blueprints:

```bash
# Export current agent as blueprint
chronos agents export agent_abc123 \
  --name "My Custom Blueprint" \
  --description "Custom agent template" \
  --output ./blueprint.yaml
```

Or via API:

```bash
POST /api/blueprints
{
  "name": "My Custom Blueprint",
  "description": "Custom agent template",
  "config": { ... }
}
```

Blueprints can be shared across teams or kept private.

## Blueprint Manifest

The blueprint manifest (`blueprints.yaml`) defines available blueprints:

```yaml
version: "1.0"
blueprints:
  - id: customer-support
    name: Customer Support Agent
    description: Comprehensive support agent
    category: support
    tags: [support, helpdesk, faq]
    variables:
      - name: company_name
        type: string
        required: true
      - name: max_ticket_age_days
        type: number
        default: 30
    voice_enabled: true
    tools:
      - search_knowledge_base
      - create_ticket
      - send_email
```

## Next Steps

- Learn about [Creating Agents](/docs/agents/creating-agents)
- Explore [Agent Memory](/docs/agents/memory)
- Configure [Tools and Integrations](/docs/agents/tools)
