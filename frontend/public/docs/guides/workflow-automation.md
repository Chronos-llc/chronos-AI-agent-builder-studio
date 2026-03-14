---
sidebar_position: 3
title: "Guide: Workflow Automation"
---

# Guide: Workflow Automation

Automate recurring business processes with scheduled agents, event triggers, and multi-step workflows.

## Types of Automation

### Scheduled Agents
Run agents on a cron schedule:

```yaml
name: daily-digest
schedule:
  cron: "0 8 * * 1-5"          # 8 AM, Monday-Friday
  timezone: America/New_York

system_prompt: |
  Compile a daily briefing:
  1. Summarize unread emails
  2. List today's meetings
  3. Check project status
  4. Create a prioritized task list
  Send the briefing to Slack.

tools:
  - name: read_emails
    builtin: true
  - name: get_calendar
    builtin: true
  - name: check_projects
    path: ./tools/projects.py
  - name: send_slack_message
    builtin: true
```

### Event-Triggered Agents
Run agents when events happen:

```yaml
name: new-lead-processor
trigger:
  type: webhook
  event: new_lead_created
  source: hubspot

system_prompt: |
  A new lead has arrived. Research them and prepare a briefing:
  1. Look up their company
  2. Check their LinkedIn profile
  3. Identify relevant case studies
  4. Draft a personalized outreach email
  5. Notify the sales team

tools:
  - name: web_search
    builtin: true
  - name: get_lead_details
    path: ./tools/lead_details.py
  - name: draft_email
    builtin: true
  - name: notify_sales
    path: ./tools/notify.py
```

### Multi-Step Workflows
Chain multiple agents in sequence:

```yaml
name: content-pipeline
type: workflow

steps:
  - name: research
    agent: web-researcher
    input: "Research {{topic}} with current data and statistics"
    output: research_data

  - name: write
    agent: blog-writer
    input: "Write a blog post about {{topic}} using this research: {{research_data}}"
    output: draft

  - name: edit
    agent: editor
    input: "Edit this draft for clarity and SEO: {{draft}}"
    output: final_post

  - name: publish
    agent: publisher
    input: "Publish to WordPress and share on social media: {{final_post}}"
    output: result

trigger:
  schedule:
    cron: "0 9 * * 1"            # Every Monday at 9 AM
  input:
    topic: "AI agents industry update"
```

## Common Automations

### Email Monitoring
```yaml
trigger:
  type: email
  filter: "to:support@company.com"
action:
  agent: email-responder
  task: "Categorize email, draft response, flag urgent items"
```

### Social Media Monitoring
```yaml
trigger:
  type: schedule
  cron: "0 */4 * * *"          # Every 4 hours
action:
  agent: social-monitor
  task: "Check Twitter/LinkedIn mentions, summarize sentiment"
```

### Report Generation
```yaml
trigger:
  type: schedule
  cron: "0 17 * * 5"           # Friday at 5 PM
action:
  agent: report-generator
  task: "Generate weekly KPI report from analytics + CRM data"
  output:
    - send_email: ["team@company.com"]
    - post_slack: "#reports"
```

---

## Next Steps

- [White-Label Solutions](./white-label) — Deploy agents for your clients
- [Multi-Agent Systems](../agents/multi-agent) — Complex orchestration
