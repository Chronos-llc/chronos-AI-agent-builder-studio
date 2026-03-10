---
sidebar_position: 2
title: Authentication
---

# Authentication

## API Keys

The simplest authentication method. Best for server-to-server communication.

### Generate a Key

1. Go to [Dashboard → Settings → API Keys](https://app.chronos.studio/settings/api-keys)
2. Click **Create New Key**
3. Name it (e.g., "production-backend")
4. Set permissions (read, write, admin)
5. Copy the key — it's only shown once

### Usage

```bash
curl https://api.chronos.studio/v1/agents \
  -H "Authorization: Bearer sk_live_abc123..."
```

### Key Types

| Prefix | Type | Use Case |
|--------|------|----------|
| `sk_live_` | Live key | Production requests |
| `sk_test_` | Test key | Development/staging |
| `sk_pub_` | Public key | Client-side (limited permissions) |

## OAuth 2.0

For applications that act on behalf of users.

### Authorization Flow

```
1. Redirect user to:
   https://auth.chronos.studio/oauth/authorize?
     client_id=YOUR_CLIENT_ID&
     redirect_uri=YOUR_CALLBACK&
     response_type=code&
     scope=agents:read agents:write

2. User authorizes your app

3. Exchange code for token:
   POST https://auth.chronos.studio/oauth/token
   {
     "grant_type": "authorization_code",
     "code": "AUTH_CODE",
     "client_id": "YOUR_CLIENT_ID",
     "client_secret": "YOUR_CLIENT_SECRET"
   }

4. Use the access token:
   Authorization: Bearer ACCESS_TOKEN
```

### Scopes

| Scope | Permission |
|-------|-----------|
| `agents:read` | List and view agents |
| `agents:write` | Create, update, delete agents |
| `agents:chat` | Send messages to agents |
| `voice:read` | View voice configurations |
| `voice:write` | Manage voice settings and numbers |
| `tools:manage` | Manage tools and integrations |
| `admin` | Full account access |

## Token Refresh

```bash
POST https://auth.chronos.studio/oauth/token
{
  "grant_type": "refresh_token",
  "refresh_token": "YOUR_REFRESH_TOKEN",
  "client_id": "YOUR_CLIENT_ID"
}
```

## Security Best Practices

1. **Never expose live keys client-side** — use public keys (`sk_pub_`) for browsers
2. **Rotate keys regularly** — update every 90 days
3. **Use minimal scopes** — only request what you need
4. **Set IP allowlists** — restrict keys to known IPs in production
5. **Monitor usage** — review API logs for anomalies

---

## Next Steps

- [Agents API](./agents) — Manage agents via API
