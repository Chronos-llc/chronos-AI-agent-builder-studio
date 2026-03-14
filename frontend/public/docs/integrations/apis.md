---
sidebar_position: 3
title: External APIs
---

# External API Integrations

Connect your agents to any REST API — internal services, third-party platforms, or custom backends.

## API Tool Definition

```python
# tools/stripe_api.py
from chronos.tools import tool
from chronos.config import env
import httpx

@tool(
    name="get_customer_billing",
    description="Look up a customer's billing information in Stripe"
)
async def get_customer_billing(customer_email: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.stripe.com/v1/customers/search",
            params={"query": f"email:'{customer_email}'"},
            headers={"Authorization": f"Bearer {env('STRIPE_SECRET_KEY')}"}
        )
        data = response.json()

        if data["data"]:
            customer = data["data"][0]
            return {
                "name": customer["name"],
                "email": customer["email"],
                "plan": customer.get("subscriptions", {}).get("data", [{}])[0].get("plan", {}).get("nickname", "None"),
                "status": customer.get("subscriptions", {}).get("data", [{}])[0].get("status", "inactive")
            }
        return {"error": "Customer not found"}
```

## OpenAPI / Swagger Import

Automatically generate tools from an OpenAPI spec:

```bash
chronos tools import-openapi https://api.example.com/openapi.json \
  --name example-api \
  --auth-header "Authorization: Bearer ${API_KEY}"
```

This generates tool definitions for every endpoint in the spec.

## Authentication Methods

### API Key
```yaml
tools:
  - name: external_api
    path: ./tools/api.py
    auth:
      type: api_key
      header: X-API-Key
      key: ${EXTERNAL_API_KEY}
```

### OAuth 2.0
```yaml
tools:
  - name: google_sheets
    path: ./tools/sheets.py
    auth:
      type: oauth2
      provider: google
      scopes:
        - https://www.googleapis.com/auth/spreadsheets
```

### Bearer Token
```yaml
tools:
  - name: internal_api
    path: ./tools/internal.py
    auth:
      type: bearer
      token: ${INTERNAL_TOKEN}
```

## Webhooks

Receive events from external services:

```yaml
webhooks:
  - name: stripe_events
    path: /webhooks/stripe
    secret: ${STRIPE_WEBHOOK_SECRET}
    events:
      - payment_intent.succeeded
      - customer.subscription.updated
    agent: billing-agent
```

When a webhook fires, the specified agent processes the event.

## Rate Limiting & Retries

```yaml
tools:
  - name: external_api
    path: ./tools/api.py
    rate_limit: 100/min
    retry:
      max_attempts: 3
      backoff: exponential
      initial_delay: 1s
```

---

## Next Steps

- [Messaging Platforms](./messaging) — Connect chat channels
- [Databases](./databases) — Connect data stores
