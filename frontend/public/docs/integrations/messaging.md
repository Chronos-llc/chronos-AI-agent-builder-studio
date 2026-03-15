---
sidebar_position: 4
title: Messaging Platforms
---

# Messaging Platform Integrations

Connect your agents to the messaging apps your users already use.

## Telegram

```yaml
channels:
  - type: telegram
    config:
      bot_token: ${TELEGRAM_BOT_TOKEN}
      commands:
        - command: /start
          response: "Welcome! I'm your AI assistant. How can I help?"
        - command: /help
          response: "Just type your question and I'll help you out."
      features:
        inline_mode: true
        group_chats: true
        file_uploads: true
```

### Setup
1. Create a bot via [@BotFather](https://t.me/BotFather) on Telegram
2. Copy the bot token
3. Set it as an environment variable: `chronos env set TELEGRAM_BOT_TOKEN=your_token`
4. Deploy your agent

## WhatsApp

```yaml
channels:
  - type: whatsapp
    config:
      phone_number_id: ${WA_PHONE_ID}
      access_token: ${WA_ACCESS_TOKEN}
      verify_token: ${WA_VERIFY_TOKEN}
      features:
        media_messages: true      # Images, documents, audio
        template_messages: true   # Pre-approved templates
        interactive_messages: true # Buttons and lists
```

### Setup
1. Create a Meta Business account
2. Set up WhatsApp Business API
3. Configure webhook URL: `https://api.mohex.org/webhooks/whatsapp/your-agent`
4. Set environment variables and deploy

## Slack

```yaml
channels:
  - type: slack
    config:
      bot_token: ${SLACK_BOT_TOKEN}
      app_token: ${SLACK_APP_TOKEN}
      features:
        threads: true
        reactions: true
        slash_commands:
          - command: /ask
            description: Ask the AI agent a question
        events:
          - message.channels
          - app_mention
```

## Discord

```yaml
channels:
  - type: discord
    config:
      bot_token: ${DISCORD_BOT_TOKEN}
      features:
        slash_commands: true
        threads: true
        voice_channels: false
```

## SMS

```yaml
channels:
  - type: sms
    config:
      provider: twilio
      phone_number: ${TWILIO_PHONE}
      account_sid: ${TWILIO_SID}
      auth_token: ${TWILIO_TOKEN}
```

## Multi-Channel Deployment

Deploy an agent to multiple channels simultaneously:

```yaml
channels:
  - type: api
  - type: telegram
    config:
      bot_token: ${TELEGRAM_BOT_TOKEN}
  - type: whatsapp
    config:
      phone_number_id: ${WA_PHONE_ID}
      access_token: ${WA_ACCESS_TOKEN}
  - type: slack
    config:
      bot_token: ${SLACK_BOT_TOKEN}
```

The agent maintains separate conversation contexts per channel and per user, but shares the same tools and knowledge.

---

## Next Steps

- [Databases](./databases) — Connect data stores
- [MCP](./mcp) — Extend with MCP servers
