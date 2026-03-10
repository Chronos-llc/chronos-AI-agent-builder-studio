# Chronos AI Agent Builder Studio - API Guide

## Overview

This guide provides documentation for the Chronos AI Agent Builder Studio API. The API is built with FastAPI and provides endpoints for:
- Marketplace management
- Skills system
- Platform updates
- Support system
- Payment methods
- Admin operations

## Authentication

All API endpoints require authentication. The following authentication methods are supported:

### Bearer Token
```http
Authorization: Bearer <token>
```

### API Key
```http
X-API-Key: <api-key>
```

### Admin Authentication
Admin-only endpoints require additional permissions. Use the admin authentication endpoints to obtain an admin token.

## Base URL

```
http://localhost:8000/api
```

## Marketplace Endpoints

### Get Marketplace Listings

Returns a list of all published agents in the marketplace.

```http
GET /marketplace/agents
```

**Parameters:**
- `category`: Filter agents by category (optional)
- `tags`: Filter agents by tags (optional)
- `search`: Search agents by name or description (optional)
- `page`: Page number (optional, default: 1)
- `limit`: Number of results per page (optional, default: 20)

**Response:**
```json
{
  "data": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "category": "string",
      "tags": ["string"],
      "version": "string",
      "publisher_id": "string",
      "price": 0,
      "rating": 0,
      "reviews_count": 0,
      "installations_count": 0,
      "created_at": "2024-01-19T22:49:03.596Z",
      "updated_at": "2024-01-19T22:49:03.596Z"
    }
  ],
  "total": 0,
  "page": 1,
  "limit": 20
}
```

### Get Agent Details

Returns detailed information about a specific agent.

```http
GET /marketplace/agents/{agent_id}
```

**Parameters:**
- `agent_id`: Agent ID (required)

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "category": "string",
  "tags": ["string"],
  "version": "string",
  "publisher_id": "string",
  "price": 0,
  "rating": 0,
  "reviews_count": 0,
  "installations_count": 0,
  "created_at": "2024-01-19T22:49:03.596Z",
  "updated_at": "2024-01-19T22:49:03.596Z",
  "screenshots": ["string"],
  "videos": ["string"],
  "features": ["string"],
  "requirements": ["string"]
}
```

### Install Agent

Installs an agent from the marketplace.

```http
POST /marketplace/agents/{agent_id}/install
```

**Parameters:**
- `agent_id`: Agent ID (required)

**Response:**
```json
{
  "success": true,
  "message": "Agent installed successfully",
  "data": {
    "id": "string",
    "name": "string",
    "version": "string"
  }
}
```

### Publish Agent

Publishes an agent to the marketplace.

```http
POST /marketplace/agents/publish
```

**Request Body:**
```json
{
  "agent_id": "string",
  "name": "string",
  "description": "string",
  "category": "string",
  "tags": ["string"],
  "price": 0,
  "screenshots": ["string"],
  "videos": ["string"],
  "features": ["string"],
  "requirements": ["string"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Agent published successfully",
  "data": {
    "id": "string",
    "name": "string",
    "version": "string"
  }
}
```

## Skills System Endpoints

### Get Skills List

Returns a list of all available skills.

```http
GET /skills
```

**Parameters:**
- `category`: Filter skills by category (optional)
- `search`: Search skills by name or description (optional)
- `page`: Page number (optional, default: 1)
- `limit`: Number of results per page (optional, default: 20)

**Response:**
```json
{
  "data": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "category": "string",
      "version": "string",
      "rating": 0,
      "reviews_count": 0,
      "installations_count": 0,
      "created_at": "2024-01-19T22:49:03.596Z",
      "updated_at": "2024-01-19T22:49:03.596Z"
    }
  ],
  "total": 0,
  "page": 1,
  "limit": 20
}
```

### Get Skill Details

Returns detailed information about a specific skill.

```http
GET /skills/{skill_id}
```

**Parameters:**
- `skill_id`: Skill ID (required)

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "category": "string",
  "version": "string",
  "rating": 0,
  "reviews_count": 0,
  "installations_count": 0,
  "created_at": "2024-01-19T22:49:03.596Z",
  "updated_at": "2024-01-19T22:49:03.596Z",
  "content": "string"
}
```

### Install Skill

Installs a skill to an agent.

```http
POST /skills/{skill_id}/install
```

**Parameters:**
- `skill_id`: Skill ID (required)

**Request Body:**
```json
{
  "agent_id": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Skill installed successfully",
  "data": {
    "id": "string",
    "name": "string",
    "version": "string"
  }
}
```

## Platform Updates Endpoints

### Get Platform Updates

Returns a list of all platform updates.

```http
GET /platform-updates
```

**Parameters:**
- `page`: Page number (optional, default: 1)
- `limit`: Number of results per page (optional, default: 10)

**Response:**
```json
{
  "data": [
    {
      "id": "string",
      "title": "string",
      "content": "string",
      "type": "string",
      "priority": "string",
      "media": ["string"],
      "is_viewed": false,
      "created_at": "2024-01-19T22:49:03.596Z"
    }
  ],
  "total": 0,
  "page": 1,
  "limit": 10
}
```

### Mark Update as Viewed

Marks a platform update as viewed.

```http
PUT /platform-updates/{update_id}/view
```

**Parameters:**
- `update_id`: Update ID (required)

**Response:**
```json
{
  "success": true,
  "message": "Update marked as viewed"
}
```

## Support System Endpoints

### Create Support Ticket

Creates a new support ticket.

```http
POST /support/tickets
```

**Request Body:**
```json
{
  "subject": "string",
  "content": "string",
  "category": "string",
  "priority": "string",
  "attachments": ["string"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Ticket created successfully",
  "data": {
    "id": "string",
    "subject": "string",
    "content": "string",
    "status": "string",
    "created_at": "2024-01-19T22:49:03.596Z"
  }
}
```

### Get Support Tickets

Returns a list of support tickets for the user.

```http
GET /support/tickets
```

**Parameters:**
- `status`: Filter tickets by status (optional)
- `priority`: Filter tickets by priority (optional)
- `page`: Page number (optional, default: 1)
- `limit`: Number of results per page (optional, default: 10)

**Response:**
```json
{
  "data": [
    {
      "id": "string",
      "subject": "string",
      "content": "string",
      "status": "string",
      "priority": "string",
      "created_at": "2024-01-19T22:49:03.596Z",
      "updated_at": "2024-01-19T22:49:03.596Z"
    }
  ],
  "total": 0,
  "page": 1,
  "limit": 10
}
```

## Payment Methods Endpoints

### Get Payment Methods

Returns a list of saved payment methods for the user.

```http
GET /payment-methods
```

**Response:**
```json
{
  "data": [
    {
      "id": "string",
      "type": "string",
      "last4": "string",
      "exp_month": 0,
      "exp_year": 0,
      "is_default": false,
      "created_at": "2024-01-19T22:49:03.596Z"
    }
  ]
}
```

### Add Payment Method

Adds a new payment method.

```http
POST /payment-methods
```

**Request Body:**
```json
{
  "type": "string",
  "card_number": "string",
  "exp_month": 0,
  "exp_year": 0,
  "cvv": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Payment method added successfully",
  "data": {
    "id": "string",
    "type": "string",
    "last4": "string",
    "exp_month": 0,
    "exp_year": 0,
    "is_default": false
  }
}
```

## Admin Endpoints

### Get Admin Dashboard Stats

Returns dashboard statistics for admins.

```http
GET /admin/stats
```

**Response:**
```json
{
  "total_agents": 0,
  "total_users": 0,
  "total_installations": 0,
  "total_reviews": 0,
  "total_support_tickets": 0,
  "new_agents_today": 0,
  "new_users_today": 0,
  "pending_support_tickets": 0
}
```

### Moderate Agent

Approves or rejects an agent for publishing.

```http
PUT /admin/agents/{agent_id}/moderate
```

**Parameters:**
- `agent_id`: Agent ID (required)

**Request Body:**
```json
{
  "status": "approved" or "rejected",
  "reason": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Agent moderation status updated"
}
```

## Error Handling

All endpoints follow a consistent error response format:

```json
{
  "detail": "Error message",
  "status": 400
}
```

Common error status codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

All endpoints have rate limits. If you exceed the limit, you'll receive a 429 Too Many Requests response.

## WebSocket Endpoints

### Real-time Updates

```
ws://localhost:8000/ws
```

Used for real-time communication between client and server. Supports events for:
- New updates
- Support ticket status changes
- Agent installation progress
- Payment status updates

## Conclusion

This API guide provides documentation for all public endpoints of the Chronos AI Agent Builder Studio. For more detailed information or to report issues, please contact our support team.
