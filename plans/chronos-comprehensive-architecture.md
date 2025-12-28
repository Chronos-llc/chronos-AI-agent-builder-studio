# Chronos AI Agent Builder Studio - Comprehensive Architecture Plan

## Project Overview

**Platform Name**: Chronos AI Agent Builder Studio  
**Core Concept**: "Building the machine that builds the machines"  
**Meta-Agent**: Special agent with full studio manipulation capabilities  
**Target**: Desktop-only platform for creating sophisticated AI agents

## System Architecture Overview

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    Chronos AI Agent Builder Studio              │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript)                                  │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │  User Workspace │ │   Studio IDE    │ │  Chronos Hub    │    │
│  │                 │ │                 │ │                 │    │
│  │ • Dashboard     │ │ • Meta-Agent    │ │ • Integrations  │    │
│  │ • Agent Panel   │ │ • Subagents     │ │ • Workflows     │    │
│  │ • Activity      │ │ • Tester        │ │ • Plugins       │    │
│  │ • Analytics     │ │ • Knowledge     │ │ • MCP Servers   │    │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  Backend (Python + FastAPI)                                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │  Agent Engine   │ │  Learning System│ │  Integration    │    │
│  │                 │ │                 │ │    Manager      │    │
│  │ • Meta-Agent    │ │ • Training UI   │ │ • MCP Protocol  │    │
│  │ • Subagents     │ │ • Real-time     │ │ • Channels      │    │
│  │ • Workflow Exec │ │ • Iterations    │ │ • AI Providers  │    │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                      │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │   PostgreSQL    │ │     Redis       │ │   File Storage  │    │
│  │                 │ │                 │ │                 │    │
│  │ • Users/Agents  │ │ • Sessions      │ │ • Knowledge     │    │
│  │ • Configs       │ │ • Real-time     │ │ • Media Files   │    │
│  │ • Learning Data │ │ • Cache         │ │ • Agent Assets  │    │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Core Platform Components

### 1. User Workspace Page

**Purpose**: Central hub for user agent activities and overview

**Features**:

- Agent activity dashboard
- Performance metrics and analytics
- Recent interactions summary
- Quick access to active agents
- Usage statistics and billing info

**Components**:

- Activity feed with real-time updates
- Agent status indicators
- Performance charts and graphs
- Quick action buttons

### 2. Sidebar Navigation System

**Primary Navigation Items**:

- **Build with "FUZZY"** (Meta-Agent - Top position)
- **Voice Agent** (Future implementation)
- **Dashboard** (User workspace)
- **Agents** (Panel view)
- **Studio** (Main development environment)
- **Tables** (Memory and record management)
- **Actions** (Custom action management)
- **Hooks** (Pre/post/during operation hooks)
- **Versions** (Agent version control)
- **Installed Integrations** (User's installed integrations)
- **Settings** (Bot configuration)

**Subagents Section** (in Studio sidebar):

- Vision Agent
- Policy Agent
- Knowledge Agent
- Personality Agent
- Image Generation Agent
- Video Agent
- Summary Agent
- Translator Agent

### 3. Agent Panel View

**Features**:

- Agent information cards
- Deployment status (which communication channels)
- "Edit in Studio" button
- Real-time status indicators
- Quick configuration access

### 4. Studio Interface (Main Development Environment)

#### Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                        Studio Header                            │
│  [Agent Name] [Save] [Test] [Deploy] [Settings]                 │
├───────────────┬─────────────────────────────────────────────────┤
│               │                                                 │
│   Sidebar     │              Main Content Area                  │
│               │                                                 │
│ • Subagents   │  ┌─────────────────────────────────────────────┐ │
│ • Tables      │  │            Right Panel                      │ │
│ • Actions     │  │            (Tester/Emulator)                │ │
│ • Hooks       │  │                                             │ │
│ • Versions    │  │  ┌─────────────────────────────────────────┐ │ │
│ • Settings    │  │  │         Chat Interface                  │ │ │
│               │  │  │                                         │ │ │
│               │  │  └─────────────────────────────────────────┘ │ │
│               │  │                                             │ │
│               │  │  [Test Agent] [Switch to Emulator]          │ │
│               │  └─────────────────────────────────────────────┘ │
├───────────────┴─────────────────────────────────────────────────┤
│                    Central Workspace                             │
│                                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │ System          │ │ Knowledge       │ │ Tools           │    │
│  │ Instructions    │ │ Base            │ │ Configuration   │    │
│  │                 │ │                 │ │                 │    │
│  │ [Text Editor]   │ │ [File Upload]   │ │ [MCP Tools]     │    │
│  │                 │ │ [Multi-media]   │ │ [Install/Config]│    │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Communication Channels                         │ │
│  │  [WebChat] [Telegram] [Slack] [WhatsApp] [Custom]          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Training/Learning Interface                    │ │
│  │  [Real-time Testing] [Inspect] [View Logs] [Training]      │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### Studio Components Detail

**Right Panel - Tester/Emulator**:

- Real-time chat interface for testing
- Emulator mode for node-based automation
- Live agent response viewing
- Debug information display

**System Instructions Box**:

- Rich text editor for agent behavior definition
- Tool usage guidelines
- Response formatting rules
- Personality and role definition

**Knowledge Base**:

- Multi-media support:
  - Text documents (.txt, .md, .pdf)
  - Files and documents
  - Images (.jpg, .png, .gif, .bmp)
  - Video files (.mp4, .avi, .mov)
- Drag-and-drop upload interface
- Automatic content extraction and indexing
- Search and retrieval system

**Tools Configuration**:

- MCP server integration
- Tool installation and configuration
- Custom tool creation interface
- Tool dependency management

**Communication Channels**:

- **WebChat Configuration** (4 styles):
  1. Chat bubble (corner widget)
  2. Embed (iframe integration)
  3. Standalone (mobile-friendly)
  4. React (library component)
- **External Channels**:
  - Telegram bot integration
  - Slack app integration
  - WhatsApp Business API
  - Custom channel support

### 5. Meta-Agent System ("FUZZY")

**Purpose**: Empowered agent with studio manipulation capabilities

**Capabilities**:

- Full studio interface control
- Agent creation and modification
- Configuration management
- System-level operations
- Automated workflows

**Interface**:

- Special sidebar placement (top)
- Voice/text command interface
- Visual programming capabilities
- Real-time studio manipulation

### 6. Subagents Architecture

#### 6.1 Summary Agent

**Purpose**: Conversation summarization and transcript management

**Configuration**:

- Enable/Disable toggle
- Summary max tokens (slider, default: 100)
- Transcript max lines (slider, default: 10)
- Model picker (from installed AI providers)
- Reset to defaults button

**Exposed Variables**:

- `{{conversation.summaryagent.summary}}` - Generated summary
- `{{conversation.SummaryAgent.transcript}}` - Full transcript

#### 6.2 Translator Agent

**Purpose**: Real-time language detection and translation

**Configuration**:

- Enable/Disable toggle
- Detect Initial User Language toggle
- Detect Language Change toggle
- Model picker for translation
- Reset to defaults button

**Exposed Variables**:

- `{{User.TranslatorAgent.Language}}` - Detected language
- `{{turn.TranslatorAgent.originalMessages}}` - Original messages

#### 6.3 Knowledge Agent

**Purpose**: Intelligent knowledge base querying and retrieval

**Configuration**:

- Enable/Disable toggle
- Answer Manually toggle (advanced)
- Additional Context toggle
- Custom context text area with variables:

  ```
  Summary of the conversation:
  {{conversation.SummaryAgent.summary}}
  
  Transcript:
  {{conversation.SummaryAgent.transcript}}
  ```

- Model Strategy:
  - Fastest (fastest model only)
  - Hybrid (fast fallback to best)
  - Best (most accurate model)
- Model pickers for:
  - Fastest model
  - Best model
  - Question extractor model
- Chunk count slider (0-50, default: 20)

**Exposed Variables**:

- `{{turn.KnowledgeAgent.answer}}` - Generated answer
- `{{turn.KnowledgeAgent.citations}}` - Source citations

#### 6.4 Vision Agent

**Purpose**: Image analysis and text extraction

**Configuration**:

- Enable/Disable toggle
- Extract from incoming images toggle
- Reset to defaults button

**Exposed Variables**:

- `{{turn.VisionAgent.content}}` - Extracted content and analysis

#### 6.5 Image Generation Agent

**Purpose**: AI image creation and editing

**Configuration**:

- Enable/Disable toggle
- Generate image toggle
- Edit images toggle
- Reset to defaults button

**Exposed Variables**:

- `{{Turn.ImageGenerationAgent.content}}` - Generated/edited images

#### 6.6 Video Agent

**Purpose**: Video generation and analysis

**Configuration**:

- Enable/Disable toggle
- Generate video toggle
- Analyze incoming videos toggle
- Reset to defaults button

**Exposed Variables**:

- `{{turn.VideoAgent.content}}` - Generated/analyzed video content

#### 6.7 Personality Agent

**Purpose**: Character and personality management
*Configuration details based on reference images*

#### 6.8 Policy Agent

**Purpose**: Compliance and rule enforcement
*Configuration details based on reference images*

### 7. Chronos Hub

**Purpose**: Central marketplace for integrations, workflows, and plugins

#### 7.1 Integration Categories

- **MCP Servers**: Model Context Protocol servers
- **AI Model Providers**: OpenAI, Anthropic, local models
- **Communication Channels**: Telegram, Slack, Discord, WhatsApp
- **External Apps**: Third-party service integrations
- **Workflows**: User-created automation workflows
- **Plugins**: Custom functionality extensions

#### 7.2 Installation Process

1. Browse available items
2. Click "Install"
3. Configuration wizard
4. API key setup (if required)
5. Connection testing
6. Success confirmation

### 8. Training/Learning System

**Real-time Testing Interface**:

- "Test Your Agent" button (sends "hi")
- Real-time action visualization
- Response inspection capability
- Code review and correction interface
- Learning injection system
- Iterative improvement tracking

**Learning Process**:

1. Agent responds to test input
2. User clicks "Inspect" to see response code
3. User provides corrections or training
4. System incorporates learning
5. Agent improves for future interactions

### 9. Tables & Memory System

**Purpose**: Agent memory and record keeping

**Features**:

- Create custom tables
- Define table schemas
- Use tables as agent memory
- Record keeping for agent actions
- Real-time table access during conversations

### 10. Free Plan Limitations

**Restrictions**:

- Maximum 1 agent per user (voice or action)
- Limited storage space
- Reduced API call limits
- Basic feature set only
- No advanced subagents

**Upgrade Incentives**:

- Multiple agents
- Advanced subagents
- Extended storage
- Higher API limits
- Priority support

## Technical Implementation Details

### Database Schema Extensions

```sql
-- Users table (extended)
users (
  id: UUID PRIMARY KEY,
  email: VARCHAR UNIQUE NOT NULL,
  username: VARCHAR UNIQUE NOT NULL,
  password_hash: VARCHAR NOT NULL,
  plan_type: VARCHAR DEFAULT 'free', -- 'free', 'pro', 'enterprise'
  agent_limit: INTEGER DEFAULT 1,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP,
  is_active: BOOLEAN DEFAULT true
)

-- Agents table (extended)
agents (
  id: UUID PRIMARY KEY,
  user_id: UUID REFERENCES users(id),
  name: VARCHAR NOT NULL,
  type: VARCHAR NOT NULL, -- 'action', 'voice'
  status: VARCHAR DEFAULT 'draft', -- 'draft', 'active', 'paused'
  configuration: JSONB,
  meta_agent_enabled: BOOLEAN DEFAULT false,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP,
  is_active: BOOLEAN DEFAULT true
)

-- Subagents configuration
subagents_config (
  id: UUID PRIMARY KEY,
  agent_id: UUID REFERENCES agents(id),
  subagent_type: VARCHAR NOT NULL,
  is_enabled: BOOLEAN DEFAULT false,
  configuration: JSONB,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP
)

-- Knowledge base
knowledge_base (
  id: UUID PRIMARY KEY,
  agent_id: UUID REFERENCES agents(id),
  name: VARCHAR NOT NULL,
  content_type: VARCHAR NOT NULL, -- 'text', 'file', 'image', 'video'
  file_path: VARCHAR,
  content_text: TEXT,
  metadata: JSONB,
  processed: BOOLEAN DEFAULT false,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP
)

-- Tables for agents
agent_tables (
  id: UUID PRIMARY KEY,
  agent_id: UUID REFERENCES agents(id),
  name: VARCHAR NOT NULL,
  schema: JSONB NOT NULL,
  data: JSONB,
  is_memory: BOOLEAN DEFAULT false,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP
)

-- Training data
training_data (
  id: UUID PRIMARY KEY,
  agent_id: UUID REFERENCES agents(id),
  input_text: TEXT NOT NULL,
  agent_response: TEXT,
  user_correction: TEXT,
  improvement_notes: TEXT,
  created_at: TIMESTAMP
)

-- Communication channels
communication_channels (
  id: UUID PRIMARY KEY,
  agent_id: UUID REFERENCES agents(id),
  channel_type: VARCHAR NOT NULL, -- 'webchat', 'telegram', 'slack', 'whatsapp'
  configuration: JSONB,
  is_active: BOOLEAN DEFAULT false,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP
)

-- Chronos Hub items
chronos_hub_items (
  id: UUID PRIMARY KEY,
  name: VARCHAR NOT NULL,
  type: VARCHAR NOT NULL, -- 'integration', 'workflow', 'plugin'
  category: VARCHAR NOT NULL,
  description: TEXT,
  configuration_schema: JSONB,
  is_free: BOOLEAN DEFAULT true,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP
)

-- User installations
user_installations (
  id: UUID PRIMARY KEY,
  user_id: UUID REFERENCES users(id),
  hub_item_id: UUID REFERENCES chronos_hub_items(id),
  configuration: JSONB,
  api_key: TEXT, -- encrypted
  is_active: BOOLEAN DEFAULT true,
  installed_at: TIMESTAMP,
  configured_at: TIMESTAMP
)
```

### API Endpoints (Extended)

```
# Authentication & User Management
POST /auth/register
POST /auth/login
POST /auth/refresh
GET /auth/profile
PUT /auth/profile
GET /user/usage-stats

# Agent Management
GET /agents
POST /agents
GET /agents/{id}
PUT /agents/{id}
DELETE /agents/{id}
POST /agents/{id}/deploy
POST /agents/{id}/test

# Meta-Agent
POST /agents/{id}/meta-agent/enable
POST /agents/{id}/meta-agent/command
GET /agents/{id}/meta-agent/status

# Subagents
GET /agents/{id}/subagents
PUT /agents/{id}/subagents/{subagent_type}
GET /agents/{id}/subagents/{subagent_type}/config

# Knowledge Base
GET /agents/{id}/knowledge
POST /agents/{id}/knowledge/upload
DELETE /agents/{id}/knowledge/{kb_id}
POST /agents/{id}/knowledge/{kb_id}/reindex

# Tables
GET /agents/{id}/tables
POST /agents/{id}/tables
PUT /agents/{id}/tables/{table_id}
DELETE /agents/{id}/tables/{table_id}
GET /agents/{id}/tables/{table_id}/data
POST /agents/{id}/tables/{table_id}/data

# Communication Channels
GET /agents/{id}/channels
POST /agents/{id}/channels
PUT /agents/{id}/channels/{channel_id}
DELETE /agents/{id}/channels/{channel_id}
POST /channels/{channel_id}/test

# Training & Learning
POST /agents/{id}/train
GET /agents/{id}/training-data
POST /agents/{id}/training-data/{training_id}/correct
GET /agents/{id}/logs
POST /agents/{id}/logs/{log_id}/inspect

# Chronos Hub
GET /hub/items
GET /hub/items/{item_id}
POST /hub/items/{item_id}/install
GET /hub/installed
PUT /hub/installations/{installation_id}
POST /hub/installations/{installation_id}/test

# Actions, Hooks, Versions (as previously defined)
# Bot Settings (as previously defined)
```

### Real-time Features

- WebSocket connections for real-time testing
- Live agent response streaming
- Real-time collaboration in studio
- Instant notification system
- Live usage monitoring

### Security Considerations

- API key encryption and secure storage
- User data isolation and multi-tenancy
- Sandboxed agent execution
- Input validation and sanitization
- Rate limiting and abuse prevention
- Audit logging for all operations

This comprehensive architecture provides a solid foundation for building the Chronos AI Agent Builder Studio with all the specified features and capabilities.
