---
sidebar_position: 2
title: Authentication
---

# Authentication

Chronos Studio supports multiple authentication methods to secure API access. This guide covers API keys and OAuth 2.0 for authenticating your requests.

## API Keys

### Overview
API keys are the simplest way to authenticate. Include your key in the `Authorization` header.

### Creating API Keys
1. Navigate to Settings → API Keys
2. Click "Create New Key"
3. Set a name and select permissions
4. Copy the key (shown only once)

### Using API Keys
```bash
curl -X GET https://api.chronos.studio/v1/agents \
  -H "Authorization: Bearer sk_live_abc123..."
```

### Key Types

| Type | Prefix | Use Case |
|------|--------|----------|
| Live | `sk_live_` | Production environment |
| Test | `sk_test_` | Testing and development |
| Read-only | `sk_read_` | Limited read access |

### Key Permissions
When creating a key, specify permissions:
- `agents:read` - Read agent information
- `agents:write` - Create and modify agents
- `tools:manage` - Configure tools
- `voice:manage` - Voice agent operations
- `webhooks:manage` - Webhook configuration

## OAuth 2.0

### Overview
OAuth 2.0 provides secure delegated access, ideal for applications that act on behalf of users.

### Authorization Code Flow

**Step 1: Redirect to Authorization**
```
https://auth.chronos.studio/authorize?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=https://yourapp.com/callback&
  response_type=code&
  scope=agents:read agents:write&
  state=random_state_string
```

**Step 2: User Authorizes**
User logs in and grants permission.

**Step 3: Receive Authorization Code**
Your redirect URI receives:
```
https://yourapp.com/callback?code=AUTHORIZATION_CODE&state=random_state_string
```

**Step 4: Exchange Code for Token**
```bash
curl -X POST https://auth.chronos.studio/token \
  -d "grant_type=authorization_code" \
  -d "code=AUTHORIZATION_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=https://yourapp.com/callback"
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token",
  "scope": "agents:read agents:write"
}
```

**Step 5: Use Access Token**
```bash
curl -X GET https://api.chronos.studio/v1/agents \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Refresh Tokens
```bash
curl -X POST https://auth.chronos.studio/token \
  -d "grant_type=refresh_token" \
  -d "refresh_token=REFRESH_TOKEN" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

## Organization Headers

When authenticated, specify the organization:

```bash
-H "X-Organization-ID: org_abc123"
```

## Security Best Practices

### API Keys
1. **Never commit keys** to version control
2. **Rotate keys** regularly
3. **Use environment variables** to store keys
4. **Set appropriate permissions** - avoid overly broad access
5. **Revoke compromised keys** immediately

```bash
# Good: Environment variable
export CHRONOS_API_KEY="sk_live_..."
curl -H "Authorization: Bearer $CHRONOS_API_KEY"

# Bad: Hardcoded key
curl -H "Authorization: Bearer sk_live_abc123"
```

### OAuth
1. **Validate redirect URIs** - only allow pre-registered URIs
2. **Use state parameter** to prevent CSRF
3. **Store tokens securely** - encrypt at rest
4. **Implement token refresh** before expiration
5. **Handle revocation** gracefully

## Token Scopes

| Scope | Description |
|-------|-------------|
| `agents:read` | Read agent data |
| `agents:write` | Create and modify agents |
| `tools:manage` | Manage tools and integrations |
| `voice:manage` | Voice agent operations |
| `webhooks:manage` | Webhook configuration |
| `billing:read` | View billing information |
| `admin` | Full administrative access |

## Troubleshooting

### 401 Unauthorized
- Check API key is valid and not expired
- Verify key has required permissions
- Ensure correct Authorization header format

### 403 Forbidden
- Key lacks required scope
- Organization ID is incorrect or missing

### Token Expiration
- Implement refresh token flow
- Handle 401 responses with retry logic
