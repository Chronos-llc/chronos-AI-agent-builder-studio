import { useState, useEffect } from 'react'

export interface DocumentationSection {
  id: string
  title: string
  description: string
  icon?: string
  pages: DocumentationPage[]
}

export interface DocumentationPage {
  id: string
  title: string
  description: string
  content?: string
  category?: string
}

// Sample documentation structure (will be replaced with actual content)
export const DOCUMENTATION_SECTIONS: DocumentationSection[] = [
  {
    id: 'overview',
    title: 'Overview',
    description: 'Learn about Chronos Studio features and architecture',
    pages: [
      {
        id: 'introduction',
        title: 'Introduction',
        description: 'What is Chronos Studio and how it works'
      },
      {
        id: 'architecture',
        title: 'Architecture',
        description: 'Technical architecture and system components'
      },
      {
        id: 'quick-start',
        title: 'Quick Start',
        description: 'Getting started guide'
      }
    ]
  },
  {
    id: 'agent-builder',
    title: 'Agent Builder',
    description: 'Building and configuring AI agents',
    pages: [
      {
        id: 'creating-agents',
        title: 'Creating Agents',
        description: 'Step-by-step guide to creating agents'
      },
      {
        id: 'agent-config',
        title: 'Agent Configuration',
        description: 'Configuration options for agents'
      },
      {
        id: 'agent-types',
        title: 'Agent Types',
        description: 'Different types of agents available'
      },
      {
        id: 'version-control',
        title: 'Version Control',
        description: 'Managing agent versions'
      }
    ]
  },
  {
    id: 'agent-suite',
    title: 'Agent Suite',
    description: 'Running and monitoring agents',
    pages: [
      {
        id: 'running-agents',
        title: 'Running Agents',
        description: 'How to run and manage agents'
      },
      {
        id: 'agent-monitoring',
        title: 'Agent Monitoring',
        description: 'Monitoring agent performance'
      },
      {
        id: 'agent-analytics',
        title: 'Agent Analytics',
        description: 'Analyzing agent behavior'
      }
    ]
  },
  {
    id: 'integrations',
    title: 'Integrations',
    description: 'Connecting external services',
    pages: [
      {
        id: 'mcp-servers',
        title: 'MCP Servers',
        description: 'Using MCP servers'
      },
      {
        id: 'ai-providers',
        title: 'AI Providers',
        description: 'Integrating AI providers'
      },
      {
        id: 'external-services',
        title: 'External Services',
        description: 'Connecting to external APIs'
      }
    ]
  },
  {
    id: 'workflow',
    title: 'Workflow & Automation',
    description: 'Building automated workflows',
    pages: [
      {
        id: 'workflow-generator',
        title: 'Workflow Generator',
        description: 'Creating workflows'
      },
      {
        id: 'virtual-computer',
        title: 'Virtual Computer',
        description: 'Using the virtual computer'
      },
      {
        id: 'task-execution',
        title: 'Task Execution',
        description: 'Executing tasks'
      }
    ]
  },
  {
    id: 'voice',
    title: 'Voice Studio',
    description: 'Voice agent configuration',
    pages: [
      {
        id: 'voice-configuration',
        title: 'Voice Configuration',
        description: 'Configuring voice agents'
      },
      {
        id: 'communication-channels',
        title: 'Communication Channels',
        description: 'Setting up communication channels'
      },
      {
        id: 'phone-numbers',
        title: 'Phone Numbers',
        description: 'Managing phone numbers'
      }
    ]
  },
  {
    id: 'api',
    title: 'API Documentation',
    description: 'API reference and examples',
    pages: [
      {
        id: 'api-overview',
        title: 'API Overview',
        description: 'API introduction'
      },
      {
        id: 'api-endpoints',
        title: 'API Endpoints',
        description: 'API endpoint reference'
      },
      {
        id: 'api-examples',
        title: 'API Examples',
        description: 'API usage examples'
      }
    ]
  },
  {
    id: 'advanced',
    title: 'Advanced Topics',
    description: 'Advanced features and customization',
    pages: [
      {
        id: 'agentic-thinking',
        title: 'Agentic Thinking',
        description: 'Advanced agent behavior'
      },
      {
        id: 'custom-integrations',
        title: 'Custom Integrations',
        description: 'Building custom integrations'
      },
      {
        id: 'deployment',
        title: 'Deployment',
        description: 'Deployment options'
      },
      {
        id: 'security',
        title: 'Security',
        description: 'Security best practices'
      }
    ]
  }
]

// Function to load documentation content from markdown files
export const loadDocumentationContent = async (pageId: string): Promise<string> => {
  try {
    // First check if there's an existing markdown file
    const existingFiles = {
      'agentic-thinking': 'agentic-thinking.md',
      'api-guide': 'api-guide.md',
      'playwright-deployment': 'playwright-deployment.md',
      'user-guide': 'user-guide.md'
    }

    if (existingFiles[pageId as keyof typeof existingFiles]) {
      const response = await fetch(`/docs/${existingFiles[pageId as keyof typeof existingFiles]}`)
      if (response.ok) {
        return await response.text()
      }
    }

    // Fallback content
    return `# ${pageId.replace('-', ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
    
This documentation page is currently being developed. Check back soon for more information.

## Features

- Comprehensive documentation coming soon
- Detailed examples and tutorials
- API references
- Best practices and guidelines

## Getting Help

If you need immediate assistance, please:

1. Check the [Chronos Studio Documentation](/)
2. Create a [support ticket](/app/support)
3. Join our [community forum](https://chronos.ai/community)

`
  } catch (error) {
    console.error('Error loading documentation content:', error)
    return `# Documentation Unavailable
    
We're sorry, but we couldn't load the documentation for this page. Please try again later.

If this issue persists, please contact our support team.`
  }
}

export const useDocumentationContent = (pageId: string) => {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadContent = async () => {
      try {
        setLoading(true)
        const docContent = await loadDocumentationContent(pageId)
        setContent(docContent)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load content')
        setContent('')
      } finally {
        setLoading(false)
      }
    }

    loadContent()
  }, [pageId])

  return { content, loading, error }
}