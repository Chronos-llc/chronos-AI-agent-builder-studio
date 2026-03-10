---
sidebar_position: 2
title: FAQ
---

# Frequently Asked Questions

## General

### What is Chronos Studio?
Chronos Studio is an AI agent platform that helps developers build, deploy, and manage intelligent agents for customer service, sales, and automation use cases.

### How do I get started?
1. Sign up at https://chronos.studio
2. Create your first agent
3. Configure tools and integrations
4. Deploy and monitor

### What languages/models do you support?
- GPT-4, GPT-3.5
- Claude
- Custom fine-tuned models via Spark

### What is the pricing?
- Free tier: 1,000 messages/month
- Pro: $99/month
- Enterprise: Custom pricing

## Agents

### How do I create an agent?
Use the dashboard, CLI, or API:
```bash
chronos agent create --name "My Agent" --type conversational
```

### Can I customize agent behavior?
Yes, via system prompts, temperature settings, and custom tools.

### How does memory work?
Agents can use conversation memory (session-based) or persistent memory (across sessions).

### Can I use my own model?
Yes, via Spark platform for fine-tuning and deployment.

## Voice AI

### How does voice work?
Voice agents use speech-to-text for input and text-to-speech for output, with the agent processing中间.

### What languages are supported?
English, Spanish, French, German, Japanese, and more.

### Can I use my own voice?
Yes, upload custom voice samples for synthesis.

### How is call quality?
High-quality audio with echo cancellation and noise reduction.

## Integrations

### What integrations are available?
CRM, helpdesk, database, messaging platforms, and more. See the integrations section.

### Can I build custom integrations?
Yes, using MCP or custom tool definitions.

### How do I connect to my database?
Configure via dashboard or configuration file with credentials.

## Security

### Is my data secure?
Yes, encryption at rest and in transit, SOC 2 certified.

### Where is data stored?
US, EU, or custom regions available.

### Do you support HIPAA?
Yes, HIPAA-compliant options available for Enterprise.

## Billing

### How does billing work?
Monthly subscription based on plan tier.

### Can I change plans?
Yes, upgrade or downgrade anytime.

### Do you offer annual billing?
Yes, with 20% discount.
