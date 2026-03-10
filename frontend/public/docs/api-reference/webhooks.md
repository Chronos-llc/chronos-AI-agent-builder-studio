---
sidebar_position: 6
title: Webhooks
---

# Webhooks API

Webhooks allow Chronos Studio to send real-time events to your application. Instead of polling for updates, your server receives HTTP POST requests when events occur.

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /webhooks | List webhooks |
| POST | /webhooks | Create webhook |
| GET | /webhooks/{id} | Get webhook details |
| PUT | /webhooks/{id} | Update webhook |
| DELETE | /webhooks/{id} | Delete webhook |
| POST | /webhooks/{id}/test | Send test event |

## Webhooks

### List Webhooks
```bash
GET /webhooks
```

### Response
```json
{
  "data": [
    {
      "id": "webhook_abc123",
      "url": "https://yourapp.com/webhooks/chronos",
      "events": ["agent.message.completed", "voice.call.ended"],
      "secret": "whsec_***",
      "active": true,
      "created_at": "2024-01-10T08:00:00Z"
    }
  ]
}
```

## Create Webhook

```bash
POST /webhooks
```

### Request Body
```json
{
  "url": "https://yourapp.com/webhooks/chronos",
  "events": [
    "agent.message.completed",
    "voice.call.ended",
    "agent.tool_called"
  ],
  "name": "Production Webhook",
  "active": true,
  "retry_policy": {
    "enabled": true,
    "max_attempts": 3,
    "backoff": "exponential"
  }
}
```

### Response
```json
{
  "id": "webhook_abc123",
  "url": "https://yourapp.com/webhooks/chronos",
  "events": ["agent.message.completed", "voice.call.ended"],
  "secret": "whsec_abc123def456",
  "active": true,
  "created_at": "2024-01-15T14:00:00Z"
}
```

**Important**: Save the `secret` securely - it's only shown once!

## Webhook Events

### Agent Events

| Event | Description |
|-------|-------------|
| `agent.message.received` | New message from user |
| `agent.message.completed` | Agent response complete |
| `agent.tool_called` | Agent invoked a tool |
| `agent.tool.completed` | Tool execution finished |
| `agent.error` | Error occurred |
| `agent.created` | New agent created |
| `agent.updated` | Agent configuration changed |
| `agent.deleted` | Agent deleted |

### Voice Events

| Event | Description |
|-------|-------------|
| `voice.call.initiated` | Call started |
| `voice.call.answered` | Call answered |
| `voice.call.in_progress` | Conversation active |
| `voice.call.transferring` | Call being transferred |
| `voice.call.ended` | Call completed |
| `voice.call.failed` | Call failed |
| `voice.transcript` | Real-time transcript segment |
| `voice.dtmf` | DTMF tone received |

### Conversation Events

| Event | Description |
|-------|-------------|
| `conversation.started` | New conversation started |
| `conversation.ended` | Conversation ended |
| `conversation.rating` | User provided rating |

## Webhook Payload

### Example: Message Completed
```json
{
  "id": "evt_xyz789",
  "type": "agent.message.completed",
  "timestamp": "2024-01-15T14:05:00Z",
  "data": {
    "agent_id": "agent_abc123",
    "session_id": "session_def456",
    "message_id": "msg_ghi789",
    "user_message": "What's my order status?",
    "agent_response": "Let me check that for you...",
    "tool_calls": [
      {
        "tool": "get_order_status",
        "parameters": {},
        "result": {"status": "shipped"}
      }
    ],
    "metadata": {
      "tokens_used": 250,
      "model": "gpt-4",
      "latency_ms": 1200
    }
  }
}
```

## Verifying Webhooks

All webhooks include a signature header for verification:

### Node.js
```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}

// Express middleware
app.post('/webhooks/chronos', (req, res) => {
  const signature = req.headers['x-chronos-signature'];
  
  if (!verifyWebhook(JSON.stringify(req.body), signature, webhookSecret)) {
    return res.status(401).send('Invalid signature');
  }
  
  // Process webhook
  console.log('Received event:', req.body.type);
  res.status(200).send('OK');
});
```

### Python
```python
import hmac
import hashlib
import json

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, f"sha256={expected}")

# Flask example
@app.route('/webhooks/chronos', methods=['POST'])
def handle_webhook():
    payload = request.get_data()
    signature = request.headers.get('X-Chronos-Signature')
    
    if not verify_webhook(payload, signature, webhook_secret):
        return 'Invalid signature', 401
    
    event = json.loads(payload)
    print(f"Received event: {event['type']}")
    return 'OK', 200
```

## Retry Policy

Configure automatic retries for failed deliveries:

```json
{
  "retry_policy": {
    "enabled": true,
    "max_attempts": 3,
    "backoff": "exponential",
    "initial_delay": 60,
    "max_delay": 3600
  }
}
```

Retry schedule (exponential):
- Attempt 1: Immediate
- Attempt 2: 60 seconds
- Attempt 3: 120 seconds

## Webhook Best Practices

### Security
1. **Always verify signatures** - Don't process unverified webhooks
2. **Use HTTPS** - Protect data in transit
3. **Keep secrets secure** - Never log or expose webhook secrets

### Reliability
1. **Respond quickly** - Return 200 within 5 seconds
2. **Process asynchronously** - Queue events for processing
3. **Implement idempotency** - Handle duplicate deliveries

### Debugging
1. **Use test events** - Verify configuration before going live
2. **Log all events** - Keep audit trail
3. **Monitor delivery** - Track success/failure rates
