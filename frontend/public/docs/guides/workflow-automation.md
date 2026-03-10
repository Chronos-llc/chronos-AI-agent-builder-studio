---
sidebar_position: 4
title: Workflow Automation
---

# Workflow Automation

Learn how to automate complex business processes using Chronos Studio agents and workflows.

## Overview

Workflow automation allows you to:
- Connect agents to business processes
- Trigger actions based on events
- Orchestrate multi-step tasks
- Handle approvals and exceptions

## Workflow Components

### Triggers
Events that start a workflow:

| Trigger | Description |
|---------|-------------|
| Webhook | HTTP request received |
| Schedule | Time-based execution |
| Event | Agent/voice event |
| Manual | User-initiated |

### Actions
Operations performed in a workflow:

- API calls
- Database operations
- Send notifications
- Create/update records
- Wait for conditions

### Conditions
Logic for branching:

- If/else branches
- Data validation
- Threshold checks

## Creating Workflows

### Dashboard

1. Navigate to **Workflows**
2. Click **Create Workflow**
3. Choose trigger type
4. Add actions and conditions
5. Save and activate

### YAML Configuration

```yaml
name: Order Processing
trigger:
  type: webhook
  path: /webhooks/order-created

steps:
  - name: validate_order
    action: http_request
    config:
      url: https://api.orders.com/validate
      method: POST
      body: "{{ trigger.body }}"
    on_failure: notify_admin

  - name: check_inventory
    action: database_query
    config:
      query: "SELECT stock FROM products WHERE id = {{ trigger.body.product_id }}"
    conditions:
      - if: "{{ steps.check_inventory.stock > 0 }}"
        continue: true
      - else:
          action: notify_out_of_stock
          stop: true

  - name: process_payment
    action: http_request
    config:
      url: https://api.payments.com/charge
      method: POST
      body:
        amount: "{{ trigger.body.amount }}"
        customer: "{{ trigger.body.customer_id }}"

  - name: create_shipment
    action: http_request
    config:
      url: https://api.shipping.com/labels
      method: POST

  - name: send_confirmation
    action: send_email
    config:
      to: "{{ trigger.body.customer_email }}"
      template: order_confirmation
```

## Agent Workflows

### Agent as Workflow Step

```python
from chronos.workflows import Workflow

workflow = Workflow(
    name="Customer Onboarding",
    trigger={"type": "user.created"}
)

# Step 1: AI classification
workflow.add_step(
    name="classify_customer",
    agent="agent_classifier",
    input="{{ trigger.user_data }}",
    output_var="classification"
)

# Step 2: Route based on classification
workflow.add_condition(
    if="{{ steps.classification.tier }} == 'enterprise'",
    then="setup_enterprise_account",
    else="setup_standard_account"
)

# Step 3: Execute appropriate setup
workflow.add_step(
    name="setup_enterprise_account",
    actions=[
        create_account(type="enterprise"),
        assign_dedicated_manager(),
        send_welcome_package()
    ]
)
```

### Complete Automation Example

```python
from chronos import WorkflowBuilder

builder = WorkflowBuilder()

# Create customer onboarding workflow
onboarding = (
    builder.workflow("Customer Onboarding")
    .trigger(
        type="webhook",
        path="/webhooks/new-customer"
    )
    
    # Step 1: Analyze customer data
    .agent_step(
        name="analyze_customer",
        agent="classifier_agent",
        input={"customer": "{{trigger.data}}"},
        output="customer_profile"
    )
    
    # Step 2: Create account
    .action(
        name="create_account",
        operation="create_record",
        table="accounts",
        data={
            "name": "{{trigger.data.company}}",
            "tier": "{{steps.analyze_customer.tier}}",
            "owner": "{{trigger.data.owner}}"
        }
    )
    
    # Step 3: Configure environment
    .agent_step(
        name="provision_resources",
        agent="provisioning_agent",
        input={
            "tier": "{{steps.analyze_customer.tier}}",
            "account_id": "{{steps.create_account.id}}"
        }
    )
    
    # Step 4: Send welcome email
    .action(
        name="send_welcome",
        operation="send_email",
        template="welcome",
        to="{{trigger.data.email}}"
    )
    
    # Error handling
    .on_error(
        notify="alerts@example.com",
        retry_count=3
    )
    
    .build()
)

# Activate workflow
onboarding.activate()
```

## Scheduled Workflows

### Cron Expressions

```yaml
name: Daily Report Generation
trigger:
  type: schedule
  cron: "0 8 * * *"  # Daily at 8 AM

steps:
  - name: fetch_data
    action: database_query
    query: "SELECT * FROM activities WHERE date = yesterday"
    output: daily_activities

  - name: analyze
    agent: "reporting_agent"
    input:
      data: "{{ steps.fetch_data }}"
      type: "daily_summary"
    output: report

  - name: send_report
    action: send_email
    to: "team@example.com"
    subject: "Daily Report - {{ now }}"
    body: "{{ steps.analyze.report }}"
```

### Built-in Schedules

```yaml
trigger:
  type: schedule
  frequency: hourly  # Options: minutely, hourly, daily, weekly, monthly
```

## Approval Workflows

### Human-in-the-Loop

```yaml
name: Expense Approval
trigger:
  type: webhook
  path: /webhooks/expense-submitted

steps:
  - name: validate_expense
    action: validate
    schema: expense_schema

  - name: check_amount
    conditions:
      - if: "{{ trigger.body.amount }} > 1000"
        action: request_approval
      - else:
          auto_approve: true

  - name: request_approval
    action: create_approval_task
    config:
      approver: "{{ trigger.body.manager }}"
      task: "Review expense of ${{ trigger.body.amount }}"
      due_in: 24 hours
      actions:
        - approve: process_payment
        - reject: notify_rejection
```

## Webhook Integration

### Receiving Webhooks

```python
from chronos.webhooks import WebhookServer

server = WebhookServer()

@server.route("/webhooks/crm")
def handle_crm_webhook(data):
    workflow = Workflow.get("sync-crm")
    workflow.trigger(data)
    
    return {"status": "accepted"}

# Start server
server.run(port=3000)
```

### Sending Webhooks

```yaml
steps:
  - name: notify_external
    action: http_request
    url: https://external-api.com/webhook
    method: POST
    headers:
      Authorization: "Bearer {{ secrets.WEBHOOK_KEY }}"
    body: "{{ workflow.output }}"
```

## Error Handling

### Retry Policies

```yaml
steps:
  - name: unreliable_api
    action: http_request
    url: https://api.example.com/data
    retry:
      max_attempts: 3
      backoff: exponential
      initial_delay: 5  # seconds
      max_delay: 60

  - name: fallback
    action: notify_admins
    conditions:
      - if: "{{ steps.unreliable_api.failed }}"
```

### Dead Letter Queue

```yaml
workflow:
  name: Process Orders
  dlq: /webhooks/orders-failed
  
  steps:
    - name: process
      action: process_order
      on_failure: move_to_dlq
```

## Monitoring

### Workflow Logs

```bash
# View workflow execution logs
chronos workflows logs order-processing --limit 50

# View specific execution
chronos workflows executions view exec_abc123
```

### Metrics

Track:
- Execution count
- Success rate
- Average duration
- Failed steps
- Queue depth

## Best Practices

1. **Idempotency** - Handle duplicate triggers gracefully
2. **Timeouts** - Set reasonable timeouts for each step
3. **Error handling** - Always plan for failures
4. **Testing** - Test workflows thoroughly before production
5. **Monitoring** - Set up alerts for failures
6. **Documentation** - Document complex workflows
