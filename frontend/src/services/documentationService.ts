import { useState, useEffect } from 'react'

export interface DocumentationPage {
  id: string
  title: string
  description: string
  filePath: string
  content?: string
  category?: string
}

export interface DocumentationSection {
  id: string
  title: string
  description: string
  icon?: string
  pages: DocumentationPage[]
}

/**
 * Real 8-section information architecture matching the drafted docs spec.
 * Each page's `filePath` points to an actual markdown file under /docs/.
 */
export const DOCUMENTATION_SECTIONS: DocumentationSection[] = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    description: 'Set up Chronos Studio and build your first agent in minutes',
    pages: [
      {
        id: 'quickstart',
        title: 'Quick Start',
        description: 'Get up and running in 5 minutes',
        filePath: 'getting-started/quickstart.md',
      },
      {
        id: 'installation',
        title: 'Installation',
        description: 'Install and configure Chronos Studio',
        filePath: 'getting-started/installation.md',
      },
      {
        id: 'first-agent',
        title: 'Your First Agent',
        description: 'Build and deploy your first AI agent',
        filePath: 'getting-started/first-agent.md',
      },
      {
        id: 'concepts',
        title: 'Core Concepts',
        description: 'Understand the fundamentals of Chronos Studio',
        filePath: 'getting-started/concepts.md',
      },
    ],
  },
  {
    id: 'platform',
    title: 'Platform',
    description: 'Explore the Chronos Studio platform, dashboard, Spark, and Jestha',
    pages: [
      {
        id: 'overview',
        title: 'Platform Overview',
        description: 'Architecture and core components',
        filePath: 'platform/overview.md',
      },
      {
        id: 'dashboard',
        title: 'Dashboard',
        description: 'Navigate and manage your workspace',
        filePath: 'platform/dashboard.md',
      },
      {
        id: 'spark',
        title: 'Spark',
        description: 'Meta-agent for building agents via natural language',
        filePath: 'platform/spark.md',
      },
      {
        id: 'jestha',
        title: 'Jestha',
        description: 'Your copilot agentic workspace app',
        filePath: 'platform/jestha.md',
      },
    ],
  },
  {
    id: 'agents',
    title: 'Agents',
    description: 'Create, configure, and orchestrate AI agents',
    pages: [
      {
        id: 'overview',
        title: 'Agents Overview',
        description: 'How agents work in Chronos Studio',
        filePath: 'agents/overview.md',
      },
      {
        id: 'creating-agents',
        title: 'Creating Agents',
        description: 'Step-by-step agent creation guide',
        filePath: 'agents/creating-agents.md',
      },
      {
        id: 'tools',
        title: 'Tools',
        description: 'Equip agents with tools and capabilities',
        filePath: 'agents/tools.md',
      },
      {
        id: 'memory',
        title: 'Memory',
        description: 'Agent memory and context management',
        filePath: 'agents/memory.md',
      },
      {
        id: 'blueprints',
        title: 'Blueprints',
        description: 'Reusable agent templates and blueprints',
        filePath: 'agents/blueprints.md',
      },
      {
        id: 'multi-agent',
        title: 'Multi-Agent',
        description: 'Orchestrate multiple agents together',
        filePath: 'agents/multi-agent.md',
      },
    ],
  },
  {
    id: 'voice-ai',
    title: 'Voice AI',
    description: 'Build real-time voice agents with sub-second latency',
    pages: [
      {
        id: 'overview',
        title: 'Voice AI Overview',
        description: 'Introduction to voice agent capabilities',
        filePath: 'voice-ai/overview.md',
      },
      {
        id: 'getting-started',
        title: 'Getting Started with Voice',
        description: 'Set up your first voice agent',
        filePath: 'voice-ai/getting-started.md',
      },
      {
        id: 'voice-models',
        title: 'Voice Models',
        description: 'Available voice models and providers',
        filePath: 'voice-ai/voice-models.md',
      },
      {
        id: 'telephony',
        title: 'Telephony',
        description: 'Phone and SIP integration',
        filePath: 'voice-ai/telephony.md',
      },
      {
        id: 'emotion-detection',
        title: 'Emotion Detection',
        description: 'Real-time sentiment and emotion analysis',
        filePath: 'voice-ai/emotion-detection.md',
      },
    ],
  },
  {
    id: 'integrations',
    title: 'Integrations',
    description: 'Connect MCP servers, APIs, messaging, and databases',
    pages: [
      {
        id: 'overview',
        title: 'Integrations Overview',
        description: 'Available integrations and how to connect',
        filePath: 'integrations/overview.md',
      },
      {
        id: 'mcp',
        title: 'MCP Servers',
        description: 'Model Context Protocol integration',
        filePath: 'integrations/mcp.md',
      },
      {
        id: 'apis',
        title: 'APIs',
        description: 'REST API and custom API integrations',
        filePath: 'integrations/apis.md',
      },
      {
        id: 'messaging',
        title: 'Messaging',
        description: 'Slack, Discord, Twilio, and more',
        filePath: 'integrations/messaging.md',
      },
      {
        id: 'databases',
        title: 'Databases',
        description: 'Database connections and storage',
        filePath: 'integrations/databases.md',
      },
    ],
  },
  {
    id: 'api-reference',
    title: 'API Reference',
    description: 'Complete API documentation with examples',
    pages: [
      {
        id: 'overview',
        title: 'API Overview',
        description: 'API introduction and base URLs',
        filePath: 'api-reference/overview.md',
      },
      {
        id: 'authentication',
        title: 'Authentication',
        description: 'API keys, JWT tokens, and OAuth',
        filePath: 'api-reference/authentication.md',
      },
      {
        id: 'agents',
        title: 'Agents API',
        description: 'CRUD operations for agents',
        filePath: 'api-reference/agents.md',
      },
      {
        id: 'voice',
        title: 'Voice API',
        description: 'Voice agent endpoints',
        filePath: 'api-reference/voice.md',
      },
      {
        id: 'tools',
        title: 'Tools API',
        description: 'Tool management endpoints',
        filePath: 'api-reference/tools.md',
      },
      {
        id: 'webhooks',
        title: 'Webhooks',
        description: 'Event webhooks and callbacks',
        filePath: 'api-reference/webhooks.md',
      },
    ],
  },
  {
    id: 'guides',
    title: 'Guides',
    description: 'End-to-end tutorials for common use cases',
    pages: [
      {
        id: 'customer-support-bot',
        title: 'Customer Support Bot',
        description: 'Build an AI-powered support agent',
        filePath: 'guides/customer-support-bot.md',
      },
      {
        id: 'sales-voice-agent',
        title: 'Sales Voice Agent',
        description: 'Create an outbound sales voice agent',
        filePath: 'guides/sales-voice-agent.md',
      },
      {
        id: 'workflow-automation',
        title: 'Workflow Automation',
        description: 'Automate complex multi-step workflows',
        filePath: 'guides/workflow-automation.md',
      },
      {
        id: 'white-label',
        title: 'White Label',
        description: 'Deploy white-label agent solutions',
        filePath: 'guides/white-label.md',
      },
    ],
  },
  {
    id: 'resources',
    title: 'Resources',
    description: 'FAQ, changelog, roadmap, and support',
    pages: [
      {
        id: 'faq',
        title: 'FAQ',
        description: 'Frequently asked questions',
        filePath: 'resources/faq.md',
      },
      {
        id: 'changelog',
        title: 'Changelog',
        description: 'Release notes and version history',
        filePath: 'resources/changelog.md',
      },
      {
        id: 'roadmap',
        title: 'Roadmap',
        description: 'Upcoming features and milestones',
        filePath: 'resources/roadmap.md',
      },
      {
        id: 'support',
        title: 'Support',
        description: 'Get help and contact the team',
        filePath: 'resources/support.md',
      },
    ],
  },
]

/**
 * Strip YAML frontmatter (---...---) from markdown content.
 */
function stripFrontmatter(content: string): string {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n/)
  if (match) {
    return content.slice(match[0].length)
  }
  return content
}

/**
 * Clean MDX/JSX-style content for plain react-markdown rendering.
 * Converts className="" to class="" and removes style={{...}} attributes
 * so the markdown renderer doesn't choke on JSX syntax.
 */
function cleanMdxContent(content: string): string {
  // Replace className="..." with class="..."
  let cleaned = content.replace(/className="([^"]*)"/g, 'class="$1"')
  // Remove style={{...}} inline JSX style objects (they break react-markdown)
  cleaned = cleaned.replace(/\s*style=\{\{[^}]*\}\}/g, '')
  return cleaned
}

/**
 * Load documentation content from a markdown file by its filePath.
 */
export const loadDocumentationContent = async (
  sectionId: string,
  pageId: string
): Promise<string> => {
  try {
    // Find the page in sections
    const section = DOCUMENTATION_SECTIONS.find((s) => s.id === sectionId)
    const page = section?.pages.find((p) => p.id === pageId)

    if (page?.filePath) {
      const response = await fetch(`/docs/${page.filePath}`)
      if (response.ok) {
        let text = await response.text()
        text = stripFrontmatter(text)
        text = cleanMdxContent(text)
        return text
      }
    }

    // Try loading intro.md for the root welcome page
    if (pageId === 'intro' || pageId === 'welcome') {
      const response = await fetch('/docs/intro.md')
      if (response.ok) {
        let text = await response.text()
        text = stripFrontmatter(text)
        text = cleanMdxContent(text)
        return text
      }
    }

    return `# Page Not Found\n\nThe documentation page "${pageId}" could not be loaded. Please navigate back to the [Docs Hub](/docs).`
  } catch (error) {
    console.error('Error loading documentation content:', error)
    return `# Documentation Unavailable\n\nWe couldn't load this page. Please try again or return to the [Docs Hub](/docs).`
  }
}

export const useDocumentationContent = (sectionId: string, pageId: string) => {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadContent = async () => {
      try {
        setLoading(true)
        const docContent = await loadDocumentationContent(sectionId, pageId)
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
  }, [sectionId, pageId])

  return { content, loading, error }
}
