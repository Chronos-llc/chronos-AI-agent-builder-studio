# Chronos AI Agent Builder Studio - Architecture Plan

## Project Overview

A comprehensive AI agent builder studio with React + TypeScript frontend and Python + FastAPI backend, featuring agent creation, customization, versioning, and integrations management.

## Technology Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: Python + FastAPI + SQLAlchemy
- **Database**: PostgreSQL (primary) + Redis (caching/sessions)
- **Authentication**: JWT-based authentication
- **State Management**: Zustand/Redux Toolkit
- **UI Framework**: Material-UI/Ant Design or custom component library
- **File Storage**: Local storage with cloud storage abstraction
- **AI Integration**: OpenAI, Anthropic, local models support

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Client  │◄──►│   FastAPI       │◄──►│   PostgreSQL    │
│   (Frontend)    │    │   (Backend)     │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   Redis Cache   │◄─────────────┘
                        │   (Sessions)    │
                        └─────────────────┘
```

### Backend Architecture

#### Core Modules

1. **Authentication Module**
   - JWT token management
   - User registration/login
   - Role-based access control

2. **Agent Management Module**
   - CRUD operations for agents
   - Version control system
   - Agent templates

3. **Actions Module**
   - Custom action execution
   - AI code generation
   - Action validation

4. **Hooks System**
   - Pre/Post/During operation hooks
   - Hook registration and execution
   - Hook chaining and ordering

5. **Integrations Module**
   - MCP servers management
   - External app integrations
   - Communication channels

6. **AI Models Module**
   - Model provider management
   - API key management
   - Usage tracking and billing

#### Database Schema

```sql
-- Users table
users (
  id: UUID PRIMARY KEY,
  email: VARCHAR UNIQUE NOT NULL,
  username: VARCHAR UNIQUE NOT NULL,
  password_hash: VARCHAR NOT NULL,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP,
  is_active: BOOLEAN DEFAULT true
)

-- Agents table
agents (
  id: UUID PRIMARY KEY,
  user_id: UUID REFERENCES users(id),
  name: VARCHAR NOT NULL,
  description: TEXT,
  configuration: JSONB,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP,
  is_active: BOOLEAN DEFAULT true
)

-- Agent versions table
agent_versions (
  id: UUID PRIMARY KEY,
  agent_id: UUID REFERENCES agents(id),
  version_number: INTEGER,
  configuration: JSONB,
  changelog: TEXT,
  created_at: TIMESTAMP,
  created_by: UUID REFERENCES users(id)
)

-- Actions table
actions (
  id: UUID PRIMARY KEY,
  agent_id: UUID REFERENCES agents(id),
  name: VARCHAR NOT NULL,
  type: VARCHAR NOT NULL, -- 'custom', 'generated', 'template'
  code: TEXT,
  configuration: JSONB,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP
)

-- Hooks table
hooks (
  id: UUID PRIMARY KEY,
  agent_id: UUID REFERENCES agents(id),
  name: VARCHAR NOT NULL,
  trigger_type: VARCHAR NOT NULL, -- 'before', 'after', 'during'
  trigger_event: VARCHAR NOT NULL,
  code: TEXT,
  configuration: JSONB,
  execution_order: INTEGER,
  is_active: BOOLEAN DEFAULT true,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP
)

-- Integrations table
integrations (
  id: UUID PRIMARY KEY,
  name: VARCHAR NOT NULL,
  type: VARCHAR NOT NULL, -- 'mcp', 'communication', 'ai_provider'
  provider: VARCHAR NOT NULL,
  configuration: JSONB,
  is_installed: BOOLEAN DEFAULT false,
  is_configured: BOOLEAN DEFAULT false,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP
)

-- User integrations table (installed by users)
user_integrations (
  id: UUID PRIMARY KEY,
  user_id: UUID REFERENCES users(id),
  integration_id: UUID REFERENCES integrations(id),
  configuration: JSONB,
  api_key: TEXT, -- encrypted
  is_active: BOOLEAN DEFAULT true,
  installed_at: TIMESTAMP,
  configured_at: TIMESTAMP
)

-- Bot settings table
bot_settings (
  id: UUID PRIMARY KEY,
  agent_id: UUID REFERENCES agents(id),
  inactivity_timeout: INTEGER DEFAULT 30, -- seconds
  node_repetition_limit: INTEGER DEFAULT 3, -- minutes
  chronos_client_enabled: BOOLEAN DEFAULT false,
  configuration_variables: JSONB,
  llm_options: JSONB,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP
)
```

### Frontend Architecture

#### Component Structure

```
src/
├── components/
│   ├── common/           # Reusable UI components
│   ├── navigation/       # Navigation components
│   ├── agents/          # Agent-specific components
│   ├── actions/         # Actions management
│   ├── hooks/           # Hooks management
│   ├── integrations/    # Integrations hub
│   ├── settings/        # Bot settings
│   └── versions/        # Version management
├── pages/               # Page components
├── hooks/               # Custom React hooks
├── services/            # API service layer
├── store/               # State management
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
└── styles/              # Global styles and themes
```

#### Key Components

1. **Main Layout**
   - Sidebar navigation
   - Top header with user menu
   - Main content area

2. **Agent Builder Interface**
   - Visual workflow editor
   - Code editor for custom actions
   - Preview and testing interface

3. **Actions Management**
   - Custom action editor
   - AI code generation interface
   - Action library/templates

4. **Hooks System**
   - Hook creation/editing interface
   - Trigger configuration
   - Execution flow visualization

5. **Integrations Hub**
   - Available integrations catalog
   - Installation wizard
   - Configuration dashboard
   - Update management

6. **Bot Settings**
   - Basic settings form
   - Workflow configuration
   - LLM options panel
   - Environment variables management

## Feature Specifications

### 1. Actions Module

- **Custom Actions**: Code editor with syntax highlighting
- **AI Generation**: Natural language to code conversion
- **Templates**: Pre-built action templates
- **Validation**: Code syntax and security checks
- **Execution**: Sandboxed action execution environment

### 2. Hooks System

- **Trigger Types**: Before, After, During operations
- **Event Types**: Action execution, agent startup/shutdown, error handling
- **Hook Chaining**: Ordered execution with dependency management
- **Debugging**: Hook execution logs and debugging tools

### 3. Version Management

- **Version Control**: Git-like versioning for agent configurations
- **Branching**: Support for agent configuration branches
- **Rollback**: Easy rollback to previous versions
- **Diff Viewer**: Visual comparison between versions

### 4. Integrations Hub

#### Available Integrations

1. **Communication Channels**
   - Telegram Bot
   - Discord Bot
   - Slack App
   - WhatsApp Business API

2. **MCP Servers**
   - File system operations
   - Database connectors
   - Web scraping tools
   - API connectors

3. **AI Model Providers**
   - OpenAI GPT models
   - Anthropic Claude
   - Local models (Ollama, etc.)
   - Custom model endpoints

#### Installation Process

1. Browse available integrations
2. Click "Install" on desired integration
3. Complete installation wizard
4. Configure integration (API keys, settings)
5. Test connection
6. Activate for agents

### 5. Bot Settings

- **Basic Settings**: Name, description, avatar
- **Workflow Options**:
  - Inactivity timeout (default: 30 seconds)
  - Node repetition limit (default: 3 minutes)
- **Chronos Client**: Enable/disable client integration
- **Configuration Variables**: Environment variable management
- **LLM Options**:
  - Default Fast LLM
  - Default Best LLM
  - Autonomous Language Model
  - RAG Language Model
  - Fallback LLM

### 6. Voice Agent (Future)

- Voice-to-text integration
- Text-to-speech capabilities
- Real-time conversation handling
- Voice command processing

## API Endpoints

### Authentication

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Token refresh
- `GET /auth/profile` - Get user profile

### Agents

- `GET /agents` - List user agents
- `POST /agents` - Create new agent
- `GET /agents/{id}` - Get agent details
- `PUT /agents/{id}` - Update agent
- `DELETE /agents/{id}` - Delete agent

### Actions

- `GET /agents/{id}/actions` - List agent actions
- `POST /agents/{id}/actions` - Create action
- `PUT /agents/{id}/actions/{action_id}` - Update action
- `DELETE /agents/{id}/actions/{action_id}` - Delete action
- `POST /actions/generate` - AI code generation

### Hooks

- `GET /agents/{id}/hooks` - List agent hooks
- `POST /agents/{id}/hooks` - Create hook
- `PUT /agents/{id}/hooks/{hook_id}` - Update hook
- `DELETE /agents/{id}/hooks/{hook_id}` - Delete hook

### Integrations

- `GET /integrations` - List available integrations
- `POST /integrations/{id}/install` - Install integration
- `GET /user-integrations` - List user installations
- `PUT /user-integrations/{id}` - Update integration config
- `POST /integrations/{id}/test` - Test integration

### Versions

- `GET /agents/{id}/versions` - List agent versions
- `POST /agents/{id}/versions` - Create new version
- `GET /agents/{id}/versions/{version_id}` - Get version details
- `POST /agents/{id}/versions/{version_id}/rollback` - Rollback to version

### Settings

- `GET /agents/{id}/settings` - Get bot settings
- `PUT /agents/{id}/settings` - Update bot settings

## Security Considerations

- API key encryption and secure storage
- Input validation and sanitization
- Rate limiting and abuse prevention
- Sandboxed action execution
- User data isolation
- HTTPS-only communication
- CSRF protection
- SQL injection prevention

## Performance Optimization

- Database query optimization
- Caching strategy with Redis
- Code splitting and lazy loading
- Image optimization and CDN
- API response compression
- Background job processing
- Connection pooling

## Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │◄──►│   React App     │    │   FastAPI App   │
│   (Nginx)       │    │   (Static)      │    │   (Docker)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐              │
                       │   PostgreSQL    │◄─────────────┘
                       │   (Database)    │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │   (Sessions)    │
                       └─────────────────┘
```

This architecture provides a scalable, maintainable foundation for the Chronos AI Agent Builder Studio with clear separation of concerns and extensibility for future features.
