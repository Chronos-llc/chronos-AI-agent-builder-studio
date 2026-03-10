---
sidebar_position: 5
title: Messaging Platforms
---

# Messaging Platforms

Deploy your agents on popular messaging platforms to reach users where they are.

## Supported Platforms

| Platform | Status | Features |
|----------|--------|----------|
| Slack | Supported | Channels, DMs, threads |
| Discord | Supported | Servers, channels, DMs |
| Microsoft Teams | Supported | Channels, meetings |
| WhatsApp | Supported | Business API |
| Telegram | Supported | Bots, groups |
| Web Chat | Supported | Custom widget |

## Slack Integration

### Setup

1. Create Slack App at https://api.slack.com/apps
2. Enable Bot Token Scopes
3. Install to workspace
4. Configure Chronos integration

### Required Scopes

```json
{
  "bot_token_scopes": [
    "chat:write",
    "channels:read",
    "groups:read",
    "im:read",
    "mpim:read",
    "users:read"
  ]
}
```

### Configuration

```bash
chronos integrations add slack \
  --token xoxb-... \
  --signing-secret ...
```

### Usage

```python
from chronos.integrations import Slack

slack = SlackIntegration(token="xoxb-...")

# Create bot
bot = slack.bots.create(
    name="Support Bot",
    default_channel="#support"
)

# Handle events
@slack.event("message")
def handle_message(event):
    if not event.user == bot.user_id:
        response = agent.chat(event.text)
        bot.reply(event.channel, event.ts, response)
```

### Interactive Components

```python
# Buttons
bot.add_action("button_click", handle_button)

# Menus
bot.add_action("select_menu", handle_menu)

# Modals
@slack.command("/help")
def handle_help(command):
    bot.open_modal(command.trigger_id, "help_modal")
```

## Discord Integration

### Setup

1. Create Application at https://discord.com/developers/applications
2. Add Bot to server
3. Configure Chronos integration

### Configuration

```bash
chronos integrations add discord \
  --token BOT_TOKEN \
  --guild-id GUILD_ID
```

### Usage

```python
from chronos.integrations import Discord

discord = DiscordIntegration(token="BOT_TOKEN")

# Create bot
bot = discord.bots.create(
    name="Game Assistant",
    guild_id="123456789"
)

# Handle commands
@bot.command("ask", description="Ask the AI")
async def ask(ctx, *, question):
    response = agent.chat(question)
    await ctx.reply(response)

# Handle messages
@bot.event("message_create")
async def handle_message(message):
    if bot.mentioned(message):
        response = agent.chat(message.content)
        await message.reply(response)
```

## Microsoft Teams Integration

### Setup

1. Register Azure AD Application
2. Configure Teams permissions
3. Add bot to Teams

### Configuration

```bash
chronos integrations add teams \
  --tenant-id TENANT_ID \
  --app-id APP_ID \
  --app-secret APP_SECRET
```

### Usage

```python
from chronos.integrations import Teams

teams = TeamsIntegration(
    tenant_id="...",
    app_id="...",
    app_secret="..."
)

# Create bot
bot = teams.bots.create(
    name="Corporate Assistant"
)

@bot.command("search")
async def search(ctx, query):
    results = agent.chat(f"Search: {query}")
    await bot.reply(ctx, results)
```

## WhatsApp Integration

### Setup

1. Create Meta Developer Account
2. Set up WhatsApp Business API
3. Configure webhook

### Configuration

```bash
chronos integrations add whatsapp \
  --phone-number-id PHONE_NUMBER_ID \
  --access-token ACCESS_TOKEN \
  --verify-token VERIFY_TOKEN
```

### Usage

```python
from chronos.integrations import WhatsApp

whatsapp = WhatsAppIntegration(
    phone_number_id="...",
    access_token="..."
)

# Handle incoming messages
@whatsapp.on_message
def handle_message(message):
    response = agent.chat(message.text)
    whatsapp.send_message(
        to=message.from_,
        text=response
    )

# Send templates
whatsapp.send_template(
    to="+1234567890",
    template="order_confirmation",
    params={"order_id": "12345"}
)
```

## Telegram Integration

### Setup

1. Create bot via @BotFather
2. Get bot token
3. Configure webhook

### Configuration

```bash
chronos integrations add telegram \
  --token BOT_TOKEN
```

### Usage

```python
from chronos.integrations import Telegram

telegram = TelegramIntegration(token="BOT_TOKEN")

@telegram.message_handler()
def handle_message(update):
    response = agent.chat(update.message.text)
    telegram.send_message(
        chat_id=update.message.chat.id,
        text=response
    )

# Handle commands
@telegram.command_handler("help")
def handle_help(update):
    telegram.send_message(
        chat_id=update.message.chat.id,
        text="I'm here to help!"
    )
```

## Web Chat Widget

### Installation

```html
<!-- Add to your website -->
<script>
  window.ChronosChat = {
    agent: 'agent_abc123',
    position: 'bottom-right',
    theme: {
      primary: '#0066FF',
      secondary: '#00CC66'
    }
  };
</script>
<script src="https://cdn.chronos.studio/widget.js"></script>
```

### Customization

```javascript
window.ChronosChat = {
  agent: 'agent_abc123',
  
  // Custom launcher
  launcher: {
    text: 'Chat with us',
    image: '/chat-icon.png'
  },
  
  // Custom messages
  greeting: 'Hi! How can we help?',
  offline: 'We\'re currently offline. Leave a message!',
  
  // Appearance
  colors: {
    primary: '#0066FF',
    background: '#FFFFFF',
    text: '#333333'
  },
  
  // Behavior
  powered_by: false, // Hide Chronos branding
  file_attachments: true,
  emojis: true
};
```

## Platform Comparison

| Platform | Best For | Limitations |
|----------|----------|-------------|
| Slack | Internal tools | Requires Slack workspace |
| Discord | Community | Gaming-focused |
| Teams | Enterprise | Complex setup |
| WhatsApp | Customer support | Business API required |
| Telegram | Global reach | Limited business features |

## Best Practices

1. **Consistent personality** - Same agent across platforms
2. **Platform optimization** - Adapt responses to platform
3. **Rich content** - Use platform-specific features
4. **Handoff planning** - Route to humans when needed
5. **Analytics** - Track per-platform performance
