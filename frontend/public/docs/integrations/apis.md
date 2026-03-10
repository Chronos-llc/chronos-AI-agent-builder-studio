---
sidebar_position: 2
title: API Integrations
---

# API Integrations

Connect your agents to external APIs to extend their capabilities.

## Supported APIs

### CRM Systems

| Provider | Status | Features |
|----------|--------|----------|
| Salesforce | Supported | Leads, contacts, opportunities |
| HubSpot | Supported | Contacts, deals, tickets |
| Pipedrive | Supported | Deals, contacts |
| Zoho CRM | Supported | Full CRM operations |

### Helpdesk

| Provider | Status | Features |
|----------|--------|----------|
| Zendesk | Supported | Tickets, users |
| Freshdesk | Supported | Tickets, contacts |
| Intercom | Supported | Conversations, users |
| HelpScout | Supported | Conversations |

### E-commerce

| Provider | Status | Features |
|----------|--------|----------|
| Shopify | Supported | Orders, products, customers |
| Stripe | Supported | Payments, customers |
| WooCommerce | Supported | Orders, products |

### Communication

| Provider | Status | Features |
|----------|--------|----------|
| Twilio | Supported | SMS, voice, WhatsApp |
| SendGrid | Supported | Email sending |
| Mailgun | Supported | Email sending |

## Creating API Integrations

### Via Dashboard

1. Navigate to **Integrations**
2. Click **Add Integration**
3. Select service type
4. Configure credentials
5. Test connection

### Via API

```bash
curl -X POST https://api.chronos.studio/v1/integrations \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "salesforce",
    "name": "Production Salesforce",
    "credentials": {
      "client_id": "YOUR_CLIENT_ID",
      "client_secret": "YOUR_CLIENT_SECRET",
      "instance_url": "https://yourcompany.salesforce.com"
    }
  }'
```

## Using Integrations in Agents

### Automatic Tool Generation

```python
# Integration automatically creates tools
integration = client.integrations.get("salesforce")

# Tools available to agents
agent = client.agents.create(
    name="Sales Agent",
    config={
        "tools": integration.available_tools
    }
)
```

### Direct API Calls

```python
# Query Salesforce
result = integration.query(
    "SELECT Id, Name FROM Account WHERE Type = 'Customer'"
)

# Create record
account = integration.create("Account", {
    "Name": "New Customer",
    "Type": "Prospect"
})
```

## Authentication Methods

### OAuth 2.0
```json
{
  "auth": {
    "type": "oauth2",
    "authorization_url": "https://service.com/oauth/authorize",
    "token_url": "https://service.com/oauth/token",
    "scopes": ["read", "write"]
  }
}
```

### API Key
```json
{
  "auth": {
    "type": "api_key",
    "header": "X-API-Key",
    "key": "your_api_key"
  }
}
```

### Basic Auth
```json
{
  "auth": {
    "type": "basic",
    "username": "user",
    "password": "pass"
  }
}
```

## Rate Limiting

Each integration handles rate limiting:

```python
# Automatic retry on rate limit
integration.set_rate_limit(
    requests_per_minute=60,
    retry_on_limit=True,
    backoff_strategy="exponential"
)
```

## Error Handling

```python
try:
    result = integration.get("Contact", "contact_id")
except IntegrationError as e:
    if e.code == "RATE_LIMIT":
        wait_and_retry(e.retry_after)
    elif e.code == "AUTH_EXPIRED":
        refresh_credentials()
    else:
        log_error(e)
```

## Webhooks for Integration Events

```bash
chronos webhooks create \
  --url https://yourapp.com/webhooks/integration \
  --events "integration.synced", "integration.error"
```

## Custom API Integration

### HTTP Integration

```python
class CustomAPI(Integration):
    name = "custom_api"
    base_url = "https://api.yourservice.com"
    
    @property
    def auth(self):
        return {"Bearer": self.secrets["api_key"]}
    
    def get_customer(self, customer_id):
        return self.get(f"/customers/{customer_id}")
    
    def create_order(self, data):
        return self.post("/orders", data)
```

### Register Custom Integration

```bash
chronos integrations register custom_api.py
```
