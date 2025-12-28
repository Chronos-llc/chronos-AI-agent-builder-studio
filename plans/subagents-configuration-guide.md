# Subagents Configuration Guide

## Overview

Subagents are specialized AI components that can be enabled within a main agent to provide specific functionality. Each subagent operates independently but can communicate and collaborate with the main agent and other subagents.

## Subagent Architecture

### Subagent Communication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main Agent                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Vision    │  │  Knowledge  │  │ Translator  │             │
│  │   Agent     │  │    Agent    │  │    Agent    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                │                │                    │
│         └────────────────┼────────────────┘                    │
│                          │                                   │
│              ┌─────────────┐  ┌─────────────┐                │
│              │ Personality │  │   Policy    │                │
│              │    Agent    │  │    Agent    │                │
│              └─────────────┘  └─────────────┘                │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Image Gen   │  │   Video     │  │  Summary    │             │
│  │   Agent     │  │   Agent     │  │    Agent    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## Individual Subagent Specifications

### 1. Summary Agent

**Purpose**: Generate conversation summaries and manage transcript data

**Configuration Interface**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Summary Agent                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ☑ Enable Agent                                             │ │
│  │                                                             │ │
│  │ Enabling the agent allows it to actively participate in    │ │
│  │ conversations. When enabled, the agent will process user   │ │
│  │ input, generate responses, and take actions as configured. │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Configuration                                               │ │
│  │                                                             │ │
│  │ Summary Max Tokens                                         │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ [====●====] 100 tokens                                 │ │ │ ← Slider
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ Transcript Max Lines                                       │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ [====●====] 10 lines                                   │ │ │ ← Slider
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ Model                                                       │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ OpenAI GPT-4        ▼                                 │ │ │ ← Model picker
│  │ │ • OpenAI GPT-4                                             │ │
│  │ │ • Anthropic Claude-3                                     │ │
│  │ │ • Local Llama 2                                         │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ 🔄 Reset to Default Values                             │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Exposed Variables                                           │ │
│  │                                                             │ │
│  │ • {{conversation.summaryagent.summary}}                     │ │
│  │   Generated summary of the conversation so far             │ │
│  │                                                             │ │
│  │ • {{conversation.SummaryAgent.transcript}}                 │ │
│  │   Full conversation transcript, formatted and truncated    │ │
│  │   to include only the last X lines                         │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Technical Implementation**:

- **Trigger**: After each conversation turn
- **Processing**: Async summarization of accumulated conversation
- **Caching**: Cache summaries to avoid redundant processing
- **Fallback**: If summarization fails, continue without summary

### 2. Translator Agent

**Purpose**: Real-time language detection and translation

**Configuration Interface**:

```
┌─────────────────────────────────────────────────────────────────┐
│                       Translator Agent                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ☑ Enable Agent                                             │ │
│  │                                                             │ │
│  │ Enabling the agent allows it to actively participate in    │ │
│  │ conversations. When enabled, the agent will process user   │ │
│  │ input, generate responses, and take actions as configured. │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Configuration                                               │ │
│  │                                                             │ │
│  │ Detect Initial User Language                               │ │
│  │ ☑ Enable                                                   │ │
│  │                                                             │ │
│  │ Automatically detect user's language. If language          │ │
│  │ detection is enabled, the agent will attempt to extract    │ │
│  │ the language if the message is at least 3 tokens. This     │ │
│  │ automatically overwrites the {{User.TranslatorAgent.       │ │
│  │ Language}} variable.                                       │ │
│  │                                                             │ │
│  │ Detect Language Change                                     │ │
│  │ ☐ Enable                                                   │ │
│  │                                                             │ │
│  │ When enabled, the agent will attempt to detect the user's  │ │
│  │ language on every conversation turn (adds latency). This   │ │
│  │ is useful if the user's language may change during the     │ │
│  │ conversation. If disabled, the agent will only detect      │ │
│  │ the user's language when language is 'null'.               │ │
│  │                                                             │ │
│  │ Model                                                       │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ Google Translate API    ▼                               │ │ │ ← Model picker
│  │ │ • Google Translate API                                   │ │
│  │ │ • DeepL API                                             │ │
│  │ │ • OpenAI Translation                                    │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ 🔄 Reset to Default Values                             │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Exposed Variables                                           │ │
│  │                                                             │ │
│  │ • {{User.TranslatorAgent.Language}}                        │ │
│  │   Detected language of the user. Set to null to reset      │ │
│  │   detection or force a language by setting to any valid    │ │
│  │   ISO code (e.g., 'en').                                   │ │
│  │                                                             │ │
│  │ • {{turn.TranslatorAgent.originalMessages}}                │ │
│  │   Original messages before translation                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Language Support**:

- ISO 639-1 language codes (e.g., 'en', 'es', 'fr', 'de', 'zh')
- Automatic detection for 100+ languages
- Fallback to 'en' if detection fails

### 3. Knowledge Agent

**Purpose**: Intelligent knowledge base querying and retrieval

**Configuration Interface**:

```
┌─────────────────────────────────────────────────────────────────┐
│                       Knowledge Agent                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ☑ Enable Agent                                             │ │
│  │                                                             │ │
│  │ Enabling the agent allows it to actively participate in    │ │
│  │ conversations. When enabled, the agent will process user   │ │
│  │ input, generate responses, and take actions as configured. │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Configuration                                               │ │
│  │                                                             │ │
│  │ Answer Manually (Advanced)                                  │ │
│  │ ☐ Enable                                                   │ │
│  │                                                             │ │
│  │ Your chatbot will not answer automatically. When this      │ │
│  │ option is enabled, you need to manually reply to the user  │ │
│  │ with {{turn.knowledgeAgent.answer}}. This can be done      │ │
│  │ with a Say Node, on a capture card or with a hook         │ │
│  │ (advanced).                                                │ │
│  │                                                             │ │
│  │ Additional Context                                          │ │
│  │ ☑ Enable                                                  │ │
│  │                                                             │ │
│  │ Providing context helps knowledge bases give better        │ │
│  │ answers. We recommend including the transcript of the      │ │
│  │ conversation and/or the summary of the summary agent.      │ │
│  │                                                             │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ Additional Context Description:                        │ │ │
│  │ │                                                         │ │ │
│  │ │ Summary of the conversation:                           │ │ │
│  │ │ """                                                     │ │ │
│  │ │ {{conversation.SummaryAgent.summary}}                   │ │ │
│  │ │ """                                                     │ │ │
│  │ │                                                         │ │ │
│  │ │ Transcript:                                             │ │ │
│  │ │ """                                                     │ │ │
│  │ │ {{conversation.SummaryAgent.transcript}}                │ │ │
│  │ │ """                                                     │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ Model Strategy                                              │ │
│  │ ○ Fastest    (Use fastest model only)                      │ │
│  │ ● Hybrid     (Fast fallback to best)                       │ │
│  │ ○ Best       (Use most accurate model)                     │ │
│  │                                                             │ │
│  │ Models Configuration                                        │ │
│  │ Fastest Model:                                              │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ OpenAI GPT-3.5 Turbo      ▼                            │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ Best Model:                                                 │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ OpenAI GPT-4            ▼                              │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ Question Extractor:                                         │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ OpenAI GPT-3.5 Turbo      ▼                            │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ Chunk Count                                                │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ [====●====] 20.00 chunks                              │ │ │ ← Slider
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ 🔄 Reset to Default Values                             │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Exposed Variables                                           │ │
│  │                                                             │ │
│  │ • {{turn.KnowledgeAgent.answer}}                            │ │
│  │   Generated answer from the knowledge base                  │ │
│  │                                                             │ │
│  │ • {{turn.KnowledgeAgent.citations}}                         │ │
│  │   Source citations for the generated answer                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Technical Implementation**:

- **Vector Database**: Embedding-based similarity search
- **Chunking**: Configurable chunk size and overlap
- **Reranking**: Optional reranking of retrieved chunks
- **Caching**: Cache query results for performance

### 4. Vision Agent

**Purpose**: Image analysis and text extraction from visual content

**Configuration Interface**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Vision Agent                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ☑ Enable Agent                                             │ │
│  │                                                             │ │
│  │ Enabling the agent allows it to actively participate in    │ │
│  │ conversations. When enabled, the agent will process user   │ │
│  │ input, generate responses, and take actions as configured. │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Configuration                                               │ │
│  │                                                             │ │
│  │ Extract from Incoming Images                               │ │
│  │ ☑ Enable                                                  │ │
│  │                                                             │ │
│  │ When enabled, the agent will attempt to extract text       │ │
│  │ content and description from incoming messages. This       │ │
│  │ settings can be overridden at the node level.              │ │
│  │                                                             │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ 🔄 Reset to Default Values                             │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Exposed Variables                                           │ │
│  │                                                             │ │
│  │ • {{turn.VisionAgent.content}}                              │ │
│  │   Extracted content and analysis from images               │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Supported Image Formats**: JPEG, PNG, GIF, BMP, WebP  
**Analysis Types**:

- OCR (Optical Character Recognition)
- Object detection
- Scene description
- Text extraction
- Image categorization

### 5. Image Generation Agent

**Purpose**: AI-powered image creation and editing

**Configuration Interface**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Image Generation Agent                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ☑ Enable Agent                                             │ │
│  │                                                             │ │
│  │ Enabling the agent allows it to actively participate in    │ │
│  │ conversations. When enabled, the agent will process user   │ │
│  │ input, generate responses, and take actions as configured. │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Configuration                                               │ │
│  │                                                             │ │
│  │ Generate Image                                              │ │
│  │ ☑ Enable                                                  │ │
│  │                                                             │ │
│  │ When enabled, the agent will attempt to detect user's      │ │
│  │ image generation requests and generate an image from       │ │
│  │ both image and text prompt.                                │ │
│  │                                                             │ │
│  │ Edit Images                                                 │ │
│  │ ☑ Enable                                                  │ │
│  │                                                             │ │
│  │ When enabled, the agent can edit images for users based    │ │
│  │ on image input and image edit prompt.                      │ │
│  │                                                             │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ 🔄 Reset to Default Values                             │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Exposed Variables                                           │ │
│  │                                                             │ │
│  │ • {{turn.ImageGenerationAgent.content}}                     │ │
│  │   Generated images and related metadata                    │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Image Generation Capabilities**:

- Text-to-image generation
- Image-to-image translation
- Inpainting and outpainting
- Style transfer
- Image upscaling

### 6. Video Agent

**Purpose**: Video generation and analysis

**Configuration Interface**:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Video Agent                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ☑ Enable Agent                                             │ │
│  │                                                             │ │
│  │ Enabling the agent allows it to actively participate in    │ │
│  │ conversations. When enabled, the agent will process user   │ │
│  │ input, generate responses, and take actions as configured. │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Configuration                                               │ │
│  │                                                             │ │
│  │ Generate Video                                              │ │
│  │ ☑ Enable                                                  │ │
│  │                                                             │ │
│  │ When enabled, the agent will attempt to detect user's      │ │
│  │ video generation requests and generate videos from         │ │
│  │ both image frame and text prompts.                         │ │
│  │                                                             │ │
│  │ Analyze Incoming Videos                                     │ │
│  │ ☑ Enable                                                  │ │
│  │                                                             │ │
│  │ When enabled, the agent will attempt to analyze/generate   │ │
│  │ analysis from videos in incoming messages. This settings   │ │
│  │ can be overridden at the node level.                       │ │
│  │                                                             │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ 🔄 Reset to Default Values                             │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Exposed Variables                                           │ │
│  │                                                             │ │
│  │ • {{turn.VideoAgent.content}}                               │ │
│  │   Generated videos and video analysis content              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Video Processing Capabilities**:

- Text-to-video generation
- Image-to-video animation
- Video analysis and description
- Scene extraction
- Video summarization

### 7. Personality Agent

**Purpose**: Character and personality management

**Configuration Interface** (Based on reference images):

```
┌─────────────────────────────────────────────────────────────────┐
│                      Personality Agent                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ☑ Enable Agent                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Configuration                                               │ │
│  │                                                             │ │
│  │ Personality Traits:                                         │ │
│  │ ○ Professional      ○ Friendly      ○ Humorous            │ │
│  │ ○ Analytical        ○ Creative      ○ Empathetic          │ │
│  │                                                             │ │
│  │ Communication Style:                                        │ │
│  │ ○ Formal           ○ Casual        ○ Technical           │ │
│  │ ○ Conversational   ○ Direct        ○ Detailed            │ │
│  │                                                             │ │
│  │ Response Preferences:                                       │ │
│  │ • Tone: [Professional and helpful     ]                   │ │
│  │ • Length: [Medium responses (2-3 sentences)]             │ │
│  │ • Formality: [Semi-formal            ]                   │ │
│  │                                                             │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ 🔄 Reset to Default Values                             │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 8. Policy Agent

**Purpose**: Compliance and rule enforcement

**Configuration Interface** (Based on reference images):

```
┌─────────────────────────────────────────────────────────────────┐
│                         Policy Agent                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ☑ Enable Agent                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Configuration                                               │ │
│  │                                                             │ │
│  │ Safety Rules:                                               │ │
│  │ ☑ Block harmful content                                    │ │
│  │ ☑ Prevent personal information disclosure                  │ │
│  │ ☑ Enforce brand guidelines                                 │ │
│  │ ☐ Require human approval for sensitive topics              │ │
│  │                                                             │ │
│  │ Content Filters:                                            │ │
│  │ • Blocked topics: [政治, 宗教, 医疗建议]                 │ │
│  │ • Approved sources: [官方文档, FAQ, 帮助中心]             │ │
│  │                                                             │ │
│  │ Escalation Rules:                                           │ │
│  │ ○ Auto-block and inform user                               │ │
│  │ ● Redirect to human support                                │ │
│  │ ○ Allow with warning                                       │ │
│  │                                                             │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │ 🔄 Reset to Default Values                             │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Subagent Interaction Patterns

### Sequential Processing

```
User Input → Main Agent → Vision → Translator → Knowledge → Summary → Response
```

### Parallel Processing

```
User Input → Main Agent → [Vision Agent] ─┐
                    → [Knowledge Agent] ─┼→ Main Agent → Response
                    → [Translator Agent] ─┘
```

### Conditional Activation

```
User Input → Main Agent 
   ↓
Contains Image? → Activate Vision Agent
   ↓
Foreign Language? → Activate Translator Agent
   ↓
Complex Query? → Activate Knowledge Agent
   ↓
Generate Response
```

## Performance Considerations

### Resource Management

- **Memory Usage**: Limit concurrent subagent processing
- **API Calls**: Batch similar requests where possible
- **Caching**: Cache expensive operations (summarization, translation)
- **Timeouts**: Implement reasonable timeouts for each subagent

### Error Handling

- **Graceful Degradation**: Continue without failed subagents
- **Retry Logic**: Implement exponential backoff for API calls
- **Fallback Modes**: Use simpler models if primary models fail
- **Error Reporting**: Log errors for debugging and improvement

### Configuration Validation

- **Model Availability**: Verify selected models are installed
- **API Key Validation**: Check API keys before saving configuration
- **Resource Limits**: Validate against user's plan limitations
- **Dependency Checking**: Ensure required dependencies are met

This comprehensive subagent configuration system provides powerful customization options while maintaining ease of use and performance optimization.
