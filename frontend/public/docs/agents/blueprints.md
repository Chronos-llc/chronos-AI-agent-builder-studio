---
sidebar_position: 5
title: Blueprints
---

# Agent Blueprints

Blueprints are reusable agent templates — snapshot an agent's configuration, share it, and let others clone and customize it.

## What's in a Blueprint?

A blueprint captures:
- Agent configuration (model, temperature, tokens)
- System prompt
- Tool definitions (built-in + custom tool interfaces)
- Memory settings
- Channel configurations
- Guardrails

It does **not** capture:
- Memory data (conversations, stored knowledge)
- Environment variables / secrets
- Deployment state

## Using Blueprints

### Browse Community Blueprints

```bash
chronos blueprints list

# Filter by category
chronos blueprints list --category support
chronos blueprints list --category voice
chronos blueprints list --category automation
```

### Create from a Blueprint

```bash
chronos create --from blueprint:customer-support-pro
```

### Via Dashboard

1. Navigate to **Agents → New → From Blueprint**
2. Browse or search blueprints
3. Preview the configuration
4. Click **Use This Blueprint**
5. Customize and deploy

## Creating Blueprints

### Save an Existing Agent as Blueprint

```bash
# Save your agent as a blueprint
chronos blueprint save my-agent \
  --name "E-commerce Support Agent" \
  --description "Full-featured support agent with order tracking, refunds, and FAQ" \
  --category support \
  --tags ecommerce,support,orders
```

### Create a Blueprint from YAML

```yaml
# blueprint.yaml
blueprint:
  name: "Voice Receptionist"
  description: "Professional voice agent for business phone lines"
  category: voice
  tags: [voice, telephony, receptionist]
  author: chronos-studio

agent:
  model: gemini-2.0-flash
  temperature: 0.5
  system_prompt: |
    You are a professional receptionist for {{company_name}}.
    You answer calls, take messages, transfer to departments,
    and schedule appointments. Be warm, professional, and efficient.

  variables:
    - name: company_name
      description: Your company name
      required: true
    - name: departments
      description: List of departments for call routing
      required: true

  tools:
    - name: transfer_call
      builtin: true
    - name: schedule_appointment
      builtin: true
    - name: take_message
      builtin: true

  voice:
    provider: elevenlabs
    voice_id: professional-female-1
    language: en
    speed: 1.0

  channels:
    - type: voice
      config:
        phone_number: ${PHONE_NUMBER}
```

## Blueprint Variables

Use `{{variable}}` for customizable fields:

```yaml
system_prompt: |
  You work for {{company_name}} in the {{industry}} industry.
  Your primary language is {{language}}.

variables:
  - name: company_name
    description: Company name
    required: true
  - name: industry
    description: Industry vertical
    default: "technology"
  - name: language
    description: Primary response language
    default: "English"
```

When someone uses the blueprint, they're prompted to fill in variables.

## Sharing Blueprints

```bash
# Publish to the Chronos community
chronos blueprint publish my-blueprint --public

# Share privately (generates a link)
chronos blueprint share my-blueprint
# → https://app.mohex.org/blueprints/abc123

# Export as file
chronos blueprint export my-blueprint -o blueprint.yaml
```

## Popular Blueprints

| Blueprint | Category | Description |
|-----------|----------|-------------|
| `customer-support-pro` | Support | Full CS agent with ticket management |
| `voice-receptionist` | Voice | Business phone line receptionist |
| `research-assistant` | Productivity | Web research + knowledge base |
| `sales-outreach` | Sales | Lead qualification + email drafts |
| `code-reviewer` | Dev Tools | PR reviews and code analysis |
| `social-media-manager` | Marketing | Content creation + scheduling |

---

## Next Steps

- [Multi-Agent Systems](./multi-agent) — Combine multiple agents
- [Spark](../platform/spark) — Generate blueprints from natural language
