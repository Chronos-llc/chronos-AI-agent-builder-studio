# Studio Interface Design & Layout Specifications

## Studio Layout Overview

The Studio is the heart of the Chronos AI Agent Builder Studio - a comprehensive development environment where users create, configure, and test their AI agents. This document provides detailed specifications for the Studio interface.

## Studio Layout Structure

### Main Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                        Studio Header                            │
│  Chronos Studio - [Agent Name] [Save] [Test] [Deploy] [⚙️]      │
├───────────────┬─────────────────────────────────────────────────┤
│               │                                                 │
│   Sidebar     │              Main Content Area                  │
│               │                                                 │
│  ┌─────────┐  │  ┌─────────────────────────────────────────────┐ │
│  │FUZZY    │  │  │            Right Panel                      │ │
│  │(Meta)   │  │  │            (90% width)                      │ │
│  └─────────┘  │  │                                             │ │
│               │  │  ┌─────────────────────────────────────────┐ │ │
│  ┌─────────┐  │  │  │         Chat Tester                     │ │ │
│  │Subagents│  │  │  │                                         │ │ │
│  │         │  │  │  │  🤖 Agent: Hello! How can I help?      │ │ │
│  │• Vision │  │  │  │  👤 User: Hi                           │ │ │
│  │• Policy │  │  │  │                                         │ │ │
│  │• Know.  │  │  │  │  [Type your message...]                │ │ │
│  │• Pers.  │  │  │  │                                         │ │ │
│  │• Image  │  │  │  └─────────────────────────────────────────┘ │ │
│  │• Video  │  │  │                                             │ │
│  │• Summ.  │  │  │  [Test Agent] [🔧 Emulator Mode]           │ │
│  │• Trans. │  │  └─────────────────────────────────────────────┘ │
│  └─────────┘  │                                                 │
│               │  ┌─────────────────────────────────────────────┐ │
│  ┌─────────┐  │  │             Footer Panel                   │ │
│  │Tables   │  │  │            (Auto-expand)                   │ │
│  │Actions  │  │  │                                             │ │
│  │Hooks    │  │  │  📊 Real-time Logs & Training              │ │
│  │Versions │  │  │  [Execution Flow] [Training Data] [Debug]  │ │
│  │Integr.  │  │  └─────────────────────────────────────────────┘ │
│  │Settings │  │                                                 │
│  └─────────┘  └─────────────────────────────────────────────────┘ │
├───────────────┴─────────────────────────────────────────────────┤
│                    Central Workspace                             │
│                                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │ System          │ │ Knowledge       │ │ Tools           │    │
│  │ Instructions    │ │ Base            │ │ Configuration   │    │
│  │                 │ │                 │ │                 │    │
│  │ 📝 Define your  │ │ 📚 Add files,   │ │ 🔧 Install MCP  │    │
│  │ agent's behavior│ │ text, images,   │ │ tools and       │    │
│  │ and personality │ │ videos to       │ │ configure AI    │    │
│  │                 │ │ train your      │ │ providers       │    │
│  │ [Edit Content]  │ │ agent           │ │                 │    │
│  │                 │ │                 │ │ [Browse Hub]    │    │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Communication Channels                         │ │
│  │                                                             │ │
│  │  🌐 WebChat    📱 Telegram    💬 Slack    📞 WhatsApp     │ │
│  │     [Config]     [Config]       [Config]     [Config]      │ │
│  │                                                             │ │
│  │  🔗 Custom Channels  [+ Add Channel]                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Component Specifications

### 1. Studio Header

**Location**: Top of screen, fixed position  
**Height**: 60px  
**Components**:

- Logo and "Chronos Studio" title
- Current agent name (editable)
- Primary action buttons:
  - **Save** (Ctrl+S): Save current changes
  - **Test**: Send test message to agent
  - **Deploy**: Deploy agent to production
  - **Settings** (⚙️): Agent configuration panel

**Styling**:

```css
.studio-header {
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}
```

### 2. Sidebar Navigation

**Location**: Left side of screen  
**Width**: 280px (collapsible to 60px)  
**Scrollable**: Yes  

#### Sidebar Sections

**Meta-Agent Section (Top)**:

```
┌─────────┐
│ 🤖 FUZZY │ ← Special highlighted section
│  Meta   │
│  Agent  │
└─────────┘
```

**Subagents Section**:

```
┌─────────────────┐
│ 🔧 Subagents    │
├─────────────────┤
│ 👁️  Vision      │
│ 🛡️  Policy      │
│ 🧠  Knowledge   │
│ 🎭  Personality │
│ 🎨  Image Gen   │
│ 🎬  Video       │
│ 📝  Summary     │
│ 🌐  Translator  │
└─────────────────┘
```

**Management Section**:

```
┌─────────────────┐
│ 📊 Tables       │
│ ⚡ Actions      │
│ 🪝 Hooks        │
│ 📋 Versions     │
│ 🔌 Integrations │
│ ⚙️  Settings    │
└─────────────────┘
```

### 3. Right Panel - Chat Tester

**Location**: Right side of main content area  
**Width**: 400px (responsive)  
**Components**:

- Chat interface with message bubbles
- Input field with send button
- Test control buttons
- Real-time response display

**Chat Interface Design**:

```
┌─────────────────────────────────────────┐
│ 🤖 Agent: Hello! How can I help you?    │ ← Agent message (left-aligned)
│                                         │
│                    👤 User: Hi there!   │ ← User message (right-aligned)
│                                         │
│ 🤖 Agent: I'm doing great! How can I    │ ← Agent response
│    assist you today?                    │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Type your message...                │ │ ← Input field
│ └─────────────────────────────────────┘ │
│                                         │
│ [Send] [Test Agent] [🔧 Emulator]      │ ← Action buttons
└─────────────────────────────────────────┘
```

**Message Bubble Styling**:

```css
.message-agent {
  background: #f3f4f6;
  color: #111827;
  border-radius: 18px 18px 18px 4px;
  padding: 12px 16px;
  margin: 8px 0;
  max-width: 80%;
  align-self: flex-start;
}

.message-user {
  background: #3b82f6;
  color: white;
  border-radius: 18px 18px 4px 18px;
  padding: 12px 16px;
  margin: 8px 0;
  max-width: 80%;
  align-self: flex-end;
}
```

### 4. Central Workspace - Three Panel Layout

#### Panel 1: System Instructions

**Purpose**: Define agent behavior and personality  
**Features**:

- Rich text editor with formatting
- Syntax highlighting for instructions
- Preview mode
- Template library
- Character/word count

**Content Structure**:

```
System Instructions:
┌─────────────────────────────────────────┐
│ Define your agent's behavior,           │
│ personality, and how it should          │
│ interact with users. Include:           │
│                                         │
│ • Core personality traits               │
│ • Response style and tone              │
│ • Tool usage guidelines                │
│ • Ethical boundaries                   │
│ • Special instructions                 │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ You are a helpful AI assistant      │ │ ← Text editor
│ │ with expertise in technology and    │ │
│ │ customer service. Always be         │ │
│ │ friendly, professional, and         │ │
│ │ concise in your responses.          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Save] [Preview] [Templates] [Reset]   │
└─────────────────────────────────────────┘
```

#### Panel 2: Knowledge Base

**Purpose**: Upload and manage training materials  
**Features**:

- Drag-and-drop file upload
- Multi-media support (text, images, videos)
- Content preview
- Search functionality
- Chunking and indexing status

**Upload Interface**:

```
Knowledge Base:
┌─────────────────────────────────────────┐
│ 📚 Upload Training Materials            │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │                                     │ │
│ │  📁 Drag files here or click       │ │ ← Upload area
│ │                                     │ │
│ │  Supported: .txt, .md, .pdf,       │ │
│ │  .jpg, .png, .mp4, .avi            │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📄 uploaded-doc.pdf      [✓ Indexed]   │ ← Uploaded files
│ 🖼️  product-image.jpg    [⏳ Processing] │
│ 🎬 tutorial-video.mp4    [⚠️ Failed]    │
│                                         │
│ [Search Knowledge] [Reindex All]       │
└─────────────────────────────────────────┘
```

#### Panel 3: Tools Configuration

**Purpose**: Install and configure MCP tools  
**Features**:

- Browse available tools from Chronos Hub
- Install/uninstall tools
- Configure tool parameters
- Test tool functionality
- Tool dependency management

**Tools Interface**:

```
Tools Configuration:
┌─────────────────────────────────────────┐
│ 🔧 Installed MCP Tools                  │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 🗃️ File System Tools               │ │ ← Tool card
│ │ [Config] [Test] [Remove]            │ │
│ │ Status: ✅ Active                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 🌐 Web Search API                   │ │
│ │ [Config] [Test] [Remove]            │ │
│ │ Status: ⚠️ Needs Configuration      │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Browse Chronos Hub] [Update All]      │
└─────────────────────────────────────────┘
```

### 5. Communication Channels Panel

**Purpose**: Configure deployment channels  
**Features**:

- Channel selection and configuration
- Real-time conversation monitoring
- Channel-specific settings
- WebChat embedding options

**Channel Configuration**:

```
Communication Channels:
┌─────────────────────────────────────────┐
│ 🌐 WebChat                              │
│ ┌─────────────────────────────────────┐ │
│ │ Style: Chat Bubble ▼               │ │ ← Style selector
│ │ Theme: Light ▼                     │ │
│ │ Position: Bottom Right ▼           │ │
│ │                                     │ │
│ │ [Preview] [Get Embed Code]         │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📱 Telegram Bot                        │
│ ┌─────────────────────────────────────┐ │
│ │ Bot Token: •••••••••••••••••••••••• │ │ ← Token input
│ │ Status: ⚠️ Not Configured           │ │
│ │                                     │ │
│ │ [Configure] [Test] [Disable]        │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [+ Add Channel]                        │
└─────────────────────────────────────────┘
```

### 6. Footer Panel - Real-time Logs

**Purpose**: Monitor agent execution and training  
**Features**:

- Real-time execution logs
- Training data interface
- Debug information
- Performance metrics

**Logs Interface**:

```
┌─────────────────────────────────────────┐
│ 📊 Real-time Agent Activity             │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 14:23:45 - Tool: FileSearch         │ │ ← Log entries
│ │    Query: "product specifications"   │ │
│ │    Result: 3 files found            │ │
│ │                                     │ │
│ │ 14:23:46 - Knowledge: Query         │ │
│ │    Context: User looking for specs  │ │
│ │    Response: Found relevant docs    │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Execution Flow] [Training] [Debug]    │ ← Tab buttons
└─────────────────────────────────────────┘
```

## Responsive Design

### Desktop (1200px+)

- Full three-panel layout
- Expanded sidebar (280px)
- Wide chat tester (400px)

### Laptop (768px - 1199px)

- Collapsible sidebar (60px when collapsed)
- Two-panel layout (instructions + knowledge/tools)
- Reduced chat tester (300px)

### Tablet (768px - 1023px)

- Hidden sidebar (accessible via hamburger)
- Stacked panels (instructions, knowledge, tools)
- Full-width chat tester

### Mobile (320px - 767px)

- Single-panel view with tabs
- Hidden chat tester (accessible via button)
- Simplified navigation

## Interactive Features

### Real-time Collaboration

- Multiple users can edit simultaneously
- Live cursor positions
- Change tracking and conflict resolution
- User presence indicators

### Auto-save and Versioning

- Automatic saving every 30 seconds
- Manual save points
- Version history with diff viewer
- Rollback functionality

### Keyboard Shortcuts

- `Ctrl+S`: Save
- `Ctrl+Enter`: Send test message
- `Ctrl+T`: Open emulator mode
- `Ctrl+/`: Show help overlay
- `F11`: Toggle fullscreen

### Drag and Drop

- File uploads to knowledge base
- Reorder panels and sections
- Drag components in emulator mode
- Drop configuration snippets

## Performance Optimization

### Lazy Loading

- Load subagent configurations on demand
- Lazy load knowledge base content
- Progressive chat history loading
- On-demand tool initialization

### Caching Strategy

- Cache agent configurations
- Store recent conversations
- Cache knowledge base searches
- Local storage for user preferences

### WebSocket Integration

- Real-time chat testing
- Live collaboration updates
- Real-time deployment status
- Instant notification system

This comprehensive Studio interface design provides a powerful, intuitive environment for building sophisticated AI agents while maintaining usability and performance.
