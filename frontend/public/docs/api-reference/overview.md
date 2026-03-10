---
sidebar_position: 1
title: API Overview
---

# API Reference Overview

The Chronos Studio API provides programmatic access to all platform features, enabling you to build custom integrations, automate workflows, and manage agents at scale.

## Base URL

All API requests should be made to:

```
https://api.chronos.studio/v1
```

## Authentication

All API requests require authentication using API keys or OAuth 2.0. See [Authentication Guide](/docs/api-reference/authentication) for details.

## Request Format

### Headers
```bash
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
X-Organization-ID: org_abc123
```

### Request Body
Most POST and PUT requests require JSON bodies:

```json
{
  "name": "My Agent",
  "type": "conversational",
  "config": {
    "temperature": 0.7
  }
}
```

## Response Format

All responses follow a consistent structure:

### Success Response
```json
{
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {"field": "name", "message": "Name is required"}
    ]
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

## Pagination

List endpoints support pagination:

```bash
GET /agents?page=2&limit=20
```

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

## Rate Limits

| Plan | Requests/Minute | Requests/Day |
|------|-----------------|--------------|
| Free | 60 | 1,000 |
| Pro | 300 | 50,000 |
| Enterprise | 1,000 | Unlimited |

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 295
X-RateLimit-Reset: 1705317600
```

## API Sections

### Agents API
Create and manage AI agents, configure behavior, and handle interactions.

- [Agents API](/docs/api-reference/agents)
- Create, read, update, delete agents
- Manage agent configurations
- Handle conversations

### Tools API
Configure and manage tools available to agents.

- [Tools API](/docs/api-reference/tools)
- Register custom tools
- Configure tool parameters
- Manage tool permissions

### Voice API
Programmatic access to voice agent features.

- [Voice API](/docs/api-reference/voice)
- Initiate voice calls
- Manage voice configurations
- Handle voice events

### Webhooks
Receive real-time events from your agents.

- [Webhooks API](/docs/api-reference/webhooks)
- Configure webhook endpoints
- Manage webhook events
- Handle webhook payloads

## SDKs

### Official SDKs
- **Python**: `pip install chronos-sdk`
- **Node.js**: `npm install chronos-sdk`
- **Go**: `go get github.com/chronos/studio-go`

### Community SDKs
- Ruby, PHP, and other community-maintained libraries

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid request parameters |
| AUTHENTICATION_ERROR | 401 | Invalid or missing credentials |
| PERMISSION_DENIED | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

## Versioning

The API uses URL versioning. Current version is `v1`.

```bash
https://api.chronos.studio/v1/agents
```

## Support

- **Documentation**: You're here!
- **Status Page**: status.chronos.studio
- **Support Email**: support@chronos.studio
