# Messaging API Integration

## Overview

The Messaging API Integration allows external bot backend systems to send messages to Chronos AI agents using Personal Access Tokens for secure authentication. This integration enables seamless communication between your existing bot infrastructure and Chronos agents.

## Features

- ✅ **Personal Access Token Management**: Secure token generation and management in user settings
- ✅ **Messaging API Endpoints**: RESTful API for sending messages to agents
- ✅ **Webhook Support**: Receive bot responses via configured webhook URLs
- ✅ **Integration Hub**: Easy installation and configuration through the Chronos Hub Marketplace
- ✅ **Conversation Tracking**: Track conversations with unique IDs
- ✅ **Multiple Message Types**: Support for text, images, and custom payloads

## Architecture

### Backend Components

1. **Personal Access Token Model** (`backend/app/models/personal_access_token.py`)
   - Secure token storage with SHA-256 hashing
   - Token prefix for identification
   - Usage tracking and expiration support
   - Revocation capabilities

2. **Token Management API** (`backend/app/api/personal_access_tokens.py`)
   - Create new tokens
   - List user tokens
   - Revoke tokens
   - Delete tokens

3. **Messaging API** (`backend/app/api/messaging_api.py`)
   - Send messages to agents
   - Webhook URL management
   - Token-based authentication
   - Message validation

### Frontend Components

1. **Personal Access Tokens Component** (`frontend/src/components/PersonalAccessTokens.tsx`)
   - Token creation interface
   - Token list with usage statistics
   - Copy token functionality
   - Revoke/delete actions

2. **Settings Page** (`frontend/src/pages/SettingsPage.tsx`)
   - Tabbed interface with Access Tokens section
   - User-friendly token management

3. **Messaging API Integration Details** (`frontend/src/components/MessagingAPIIntegrationDetails.tsx`)
   - Integration information
   - Setup instructions
   - Configuration interface
   - API documentation

## Setup Instructions

### 1. Database Migration

The Personal Access Token model will be automatically created when you start the backend server. The database tables are created via SQLAlchemy's `create_all()` method.

### 2. Seed the Messaging API Integration

Run the seeding script to add the Messaging API integration to the marketplace:

```bash
cd backend
python scripts/seed_messaging_api_integration.py
```

### 3. Start the Services

```bash
# Start backend
cd ..
python -m uvicorn app.main:app --app-dir backend --reload-dir backend --reload

# Start frontend
cd frontend
npm run dev
```

## Usage Guide

### For Chronos Users

#### Step 1: Create a Personal Access Token

1. Navigate to **Settings** → **Access Tokens**
2. Click **Create New Token**
3. Enter a descriptive name (e.g., "Production Bot Integration")
4. Click **Create Token**
5. **Important**: Copy the token immediately - it won't be shown again!

#### Step 2: Install the Messaging API Integration

1. Go to **Integrations** in the Chronos Hub Marketplace
2. Search for "Messaging API"
3. Click **Install Integration**
4. Select your agent
5. Configure the **Response Endpoint URL** (where you want to receive bot responses)
6. Save the configuration

#### Step 3: Get Your Webhook URL

The webhook URL for sending messages will be displayed after installation:
```
https://api.chronos.ai/api/v1/messaging/messages/send
```

### For External Bot Systems

#### Sending Messages to Chronos

**Endpoint**: `POST /api/v1/messaging/messages/send`

**Headers**:
```
Authorization: Bearer chronos_YOUR_PERSONAL_ACCESS_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "userId": "user123",
  "messageId": "msg_unique_id_123",
  "conversationId": "conv_abc123",
  "type": "text",
  "text": "Hello, Chronos agent!",
  "payload": {
    "metadata": "optional additional data"
  }
}
```

**Response**:
```json
{
  "type": "text",
  "payload": {
    "text": "Message received: Hello, Chronos agent!",
    "status": "processing"
  },
  "conversationId": "conv_abc123",
  "chronosUserId": "1",
  "chronosMessageId": "msg_1704931200.123",
  "chronosConversationId": "conv_abc123"
}
```

#### Receiving Bot Responses

Chronos will send bot responses to your configured webhook URL:

**Method**: `POST`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "type": "text",
  "payload": {
    "text": "This is the bot's response"
  },
  "conversationId": "conv_abc123",
  "chronosUserId": "1",
  "chronosMessageId": "msg_1704931200.456",
  "chronosConversationId": "conv_abc123"
}
```

**Your webhook should return**: `HTTP 200 OK`

## API Reference

### Personal Access Tokens API

#### Create Token
```
POST /api/v1/personal-access-tokens/tokens/
```

#### List Tokens
```
GET /api/v1/personal-access-tokens/tokens/
```

#### Get Token
```
GET /api/v1/personal-access-tokens/tokens/{token_id}
```

#### Update Token
```
PUT /api/v1/personal-access-tokens/tokens/{token_id}
```

#### Revoke Token
```
POST /api/v1/personal-access-tokens/tokens/{token_id}/revoke
```

#### Delete Token
```
DELETE /api/v1/personal-access-tokens/tokens/{token_id}
```

### Messaging API

#### Send Message
```
POST /api/v1/messaging/messages/send
```

#### Get Webhook URL
```
GET /api/v1/messaging/messages/webhook
```

#### Test Webhook
```
POST /api/v1/messaging/messages/webhook/test
```

## Security Considerations

1. **Token Storage**: Tokens are hashed using SHA-256 before storage
2. **Token Prefix**: Only the first 8 characters are stored for identification
3. **HTTPS Only**: Always use HTTPS in production
4. **Token Expiration**: Tokens can have expiration dates
5. **Revocation**: Tokens can be revoked immediately
6. **Usage Tracking**: Monitor token usage for suspicious activity

## Example Integration

### Python Example

```python
import requests

# Configuration
CHRONOS_API_URL = "https://api.chronos.ai/api/v1/messaging/messages/send"
PERSONAL_ACCESS_TOKEN = "chronos_your_token_here"

# Send a message
def send_message_to_chronos(user_id, message_text, conversation_id):
    headers = {
        "Authorization": f"Bearer {PERSONAL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "userId": user_id,
        "messageId": f"msg_{int(time.time())}",
        "conversationId": conversation_id,
        "type": "text",
        "text": message_text,
        "payload": {}
    }
    
    response = requests.post(CHRONOS_API_URL, json=payload, headers=headers)
    return response.json()

# Webhook handler (Flask example)
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_chronos_response():
    data = request.json
    conversation_id = data['conversationId']
    response_text = data['payload']['text']
    
    # Process the response
    print(f"Received response for {conversation_id}: {response_text}")
    
    return jsonify({"status": "ok"}), 200
```

### Node.js Example

```javascript
const axios = require('axios');
const express = require('express');

// Configuration
const CHRONOS_API_URL = 'https://api.chronos.ai/api/v1/messaging/messages/send';
const PERSONAL_ACCESS_TOKEN = 'chronos_your_token_here';

// Send a message
async function sendMessageToChronos(userId, messageText, conversationId) {
  const response = await axios.post(CHRONOS_API_URL, {
    userId,
    messageId: `msg_${Date.now()}`,
    conversationId,
    type: 'text',
    text: messageText,
    payload: {}
  }, {
    headers: {
      'Authorization': `Bearer ${PERSONAL_ACCESS_TOKEN}`,
      'Content-Type': 'application/json'
    }
  });
  
  return response.data;
}

// Webhook handler
const app = express();
app.use(express.json());

app.post('/webhook', (req, res) => {
  const { conversationId, payload } = req.body;
  const responseText = payload.text;
  
  // Process the response
  console.log(`Received response for ${conversationId}: ${responseText}`);
  
  res.status(200).json({ status: 'ok' });
});

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

## Troubleshooting

### Token Issues

**Problem**: "Invalid or revoked token"
- **Solution**: Verify the token is active and not revoked in Settings → Access Tokens
- **Solution**: Ensure you're using the full token including the `chronos_` prefix

**Problem**: "Token has expired"
- **Solution**: Create a new token or update the expiration date

### Webhook Issues

**Problem**: Not receiving bot responses
- **Solution**: Verify your webhook URL is publicly accessible
- **Solution**: Ensure your webhook returns HTTP 200
- **Solution**: Check webhook URL configuration in the integration settings

**Problem**: "Connection test failed"
- **Solution**: Test your webhook URL with a tool like Request Bin
- **Solution**: Check firewall and network settings

## Files Created/Modified

### Backend
- ✅ `backend/app/models/personal_access_token.py` - Token model
- ✅ `backend/app/schemas/personal_access_token.py` - Token schemas
- ✅ `backend/app/api/personal_access_tokens.py` - Token management API
- ✅ `backend/app/api/messaging_api.py` - Messaging API endpoints
- ✅ `backend/app/models/user.py` - Added token relationship
- ✅ `backend/app/main.py` - Added new routers
- ✅ `backend/scripts/seed_messaging_api_integration.py` - Seeding script

### Frontend
- ✅ `frontend/src/components/PersonalAccessTokens.tsx` - Token management UI
- ✅ `frontend/src/components/MessagingAPIIntegrationDetails.tsx` - Integration details
- ✅ `frontend/src/pages/SettingsPage.tsx` - Updated with token management

## Next Steps

1. **Run the seeding script** to add the Messaging API integration to the marketplace
2. **Test token creation** in the Settings page
3. **Install the integration** from the marketplace
4. **Test the API** with your bot backend system
5. **Monitor usage** and token activity

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the API reference
- Contact support at support@chronos.ai

---

**Version**: 0.2.3  
**Last Updated**: 2026-01-10  
**Author**: Chronos AI Team
