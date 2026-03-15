---
sidebar_position: 1
title: "Guide: Customer Support Bot"
---

# Guide: Build a Customer Support Bot

Build a production-ready customer support agent with ticket management, knowledge base search, and human escalation.

## What We'll Build

A support agent that:
- Answers FAQs from a knowledge base
- Looks up customer accounts and order status
- Creates support tickets
- Escalates to humans when needed
- Works on Telegram, WhatsApp, and your website

## Architecture

```
Customer → Channel (Telegram/WA/Web) → Support Agent
                                          │
                                          ├── Knowledge Base (FAQ)
                                          ├── CRM (Account Lookup)
                                          ├── Order System (Status)
                                          ├── Ticketing (Create/Update)
                                          └── Escalation (Human Handoff)
```

## Step 1: Agent Configuration

```yaml
name: support-bot
model: gemini-2.0-flash
temperature: 0.3                  # Lower = more consistent for support

system_prompt: |
  You are a customer support agent for {{company_name}}.

  Guidelines:
  - Always greet the customer warmly
  - Search the knowledge base before saying "I don't know"
  - Look up their account when they mention orders or billing
  - Create a ticket for any issue you can't resolve immediately
  - Escalate to a human if the customer is very frustrated or
    the issue requires account changes you can't make
  - Never share other customers' information
  - Keep responses concise and helpful

  Escalation triggers:
  - Customer explicitly asks for a human
  - Issue involves refunds over $100
  - Technical issues you can't diagnose
  - Customer has been frustrated for 3+ messages

memory:
  type: persistent
  per_user: true
  ttl: 90d

tools:
  - name: search_faq
    path: ./tools/faq_search.py
  - name: lookup_customer
    path: ./tools/customer_lookup.py
  - name: check_order_status
    path: ./tools/order_status.py
  - name: create_ticket
    path: ./tools/create_ticket.py
  - name: escalate_to_human
    path: ./tools/escalate.py

channels:
  - type: api
  - type: telegram
    config:
      bot_token: ${TELEGRAM_BOT_TOKEN}
  - type: whatsapp
    config:
      phone_number_id: ${WA_PHONE_ID}
      access_token: ${WA_ACCESS_TOKEN}

guardrails:
  pii_detection: true
  max_tool_calls: 8
```

## Step 2: Build the Tools

### FAQ Search

```python
# tools/faq_search.py
from chronos.tools import tool
from chronos.memory import vector

@tool(
    name="search_faq",
    description="Search the FAQ knowledge base for answers"
)
async def search_faq(question: str) -> list[dict]:
    results = await vector.search(
        collection="faq",
        query=question,
        limit=3,
        threshold=0.7
    )
    return [{"question": r.metadata["question"],
             "answer": r.metadata["answer"]}
            for r in results]
```

### Customer Lookup

```python
# tools/customer_lookup.py
from chronos.tools import tool
import httpx

@tool(
    name="lookup_customer",
    description="Look up a customer by email or phone number"
)
async def lookup_customer(
    email: str = None,
    phone: str = None
) -> dict:
    async with httpx.AsyncClient() as client:
        params = {}
        if email: params["email"] = email
        if phone: params["phone"] = phone

        response = await client.get(
            f"{env('CRM_URL')}/customers/search",
            params=params,
            headers={"Authorization": f"Bearer {env('CRM_TOKEN')}"}
        )
        customer = response.json()

    if customer.get("data"):
        c = customer["data"][0]
        return {
            "name": c["name"],
            "email": c["email"],
            "plan": c["subscription"]["plan"],
            "status": c["subscription"]["status"],
            "member_since": c["created_at"]
        }
    return {"error": "Customer not found"}
```

### Escalation

```python
# tools/escalate.py
from chronos.tools import tool

@tool(
    name="escalate_to_human",
    description="Transfer the conversation to a human support agent",
    requires_confirmation=False
)
async def escalate_to_human(
    reason: str,
    priority: str = "normal"
) -> str:
    # Creates a ticket and notifies the support team
    ticket = await ticketing.create(
        type="escalation",
        reason=reason,
        priority=priority,
        conversation_history=current_conversation()
    )

    await notify_team(
        channel="support-queue",
        message=f"Escalation: {reason} (Priority: {priority})"
    )

    return f"Transferred to human support (Ticket #{ticket.id}). A team member will respond shortly."
```

## Step 3: Load FAQ Data

```bash
# Import FAQ from a CSV file
chronos memory import faq \
  --collection faq \
  --file faq_data.csv \
  --question-column "question" \
  --answer-column "answer"
```

## Step 4: Test

```bash
chronos dev
```

```
You: "Hi, I ordered something last week and haven't received it"
Agent: "Hi there! I'd be happy to help you track down your order.
        Could you share your email address or order number so I
        can look it up?"

You: "jesse@example.com"
Agent: [tool:lookup_customer] Looking up account...
       [tool:check_order_status] Checking orders...

       "I found your account, Jesse! Your most recent order
        (#ORD-4521) shipped on March 5 and is currently in transit.
        The estimated delivery is March 11. Would you like me to
        send you the tracking link?"
```

## Step 5: Deploy

```bash
chronos deploy --env production
```

---

## Metrics to Track

- **Resolution Rate** — % of issues resolved without escalation
- **Average Handling Time** — Time from first message to resolution
- **Customer Satisfaction** — Post-conversation ratings
- **Escalation Rate** — % of conversations requiring humans
- **FAQ Hit Rate** — % of questions answered from knowledge base

## Next Steps

- [Sales Voice Agent](./sales-voice-agent) — Build a voice-based sales agent
- [Workflow Automation](./workflow-automation) — Automate business processes
