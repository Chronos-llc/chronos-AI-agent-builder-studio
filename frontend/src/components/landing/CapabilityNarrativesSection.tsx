import React from 'react'
import { Link } from 'react-router-dom'
import { BarChart3, Bot, ClipboardCheck, Compass, LineChart, MessageCircle, Mic2, ShieldCheck, ShoppingBag, Wrench, Workflow } from 'lucide-react'
import { Reveal } from '../Reveal'

const capabilityNarratives = [
  {
    title: 'Agent Builder + Fuzzy assistant',
    detail: 'Design prompts, sub-agent behavior, model choices, and execution paths with guided assistance from Fuzzy.',
    href: '/app/agents/new',
    icon: Bot,
  },
  {
    title: 'Workflow Generator + Virtual Computer',
    detail: 'Chain task steps and run code execution paths with controlled runtime and traceable outputs.',
    href: '/app/agents/new',
    icon: Workflow,
  },
  {
    title: 'MCP Hub + Integrations',
    detail: 'Install and configure servers/connectors, then expose operations inside agents and workflows.',
    href: '/app/integrations',
    icon: Wrench,
  },
  {
    title: 'Marketplace',
    detail: 'Discover, install, and operationalize reusable agents from marketplace-ready distributions.',
    href: '/app/agents',
    icon: ShoppingBag,
  },
  {
    title: 'Voice Studio + Communication Channels',
    detail: 'Configure voice pipelines and deploy to webchat, Telegram, Slack, WhatsApp, and other channels.',
    href: '/app/channels',
    icon: Mic2,
  },
  {
    title: 'Agent Suite',
    detail: 'Chat with agents, continue tasks across channels, and inspect action timelines in one place.',
    href: '/app/agents',
    icon: MessageCircle,
  },
  {
    title: 'Testing Suites',
    detail: 'Validate behaviors and outcomes before live deployment with repeatable test scenarios.',
    href: '/app/agents/new',
    icon: ClipboardCheck,
  },
  {
    title: 'Call Logs + Reports/Boards',
    detail: 'Audit execution history and visualize operational metrics for optimization and governance.',
    href: '/app',
    icon: BarChart3,
  },
  {
    title: 'Compliance + Analytics',
    detail: 'Apply policy controls and monitor performance telemetry for production readiness.',
    href: '/app/settings',
    icon: ShieldCheck,
  },
  {
    title: 'Operational observability',
    detail: 'Track context usage, conversation summaries, and action traces across runtime surfaces.',
    href: '/app/agents',
    icon: LineChart,
  },
]

export const CapabilityNarrativesSection: React.FC = () => {
  return (
    <section className="mx-auto w-full max-w-7xl px-6 py-16">
      <Reveal>
        <h2 className="text-3xl font-semibold text-white md:text-4xl">Platform capabilities explained</h2>
      </Reveal>
      <Reveal delay={80}>
        <p className="mt-4 max-w-3xl text-white/70">
          Chronos capabilities are designed to work as one system: build, route, execute, observe, and improve without context loss.
        </p>
      </Reveal>
      <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {capabilityNarratives.map((item, index) => (
          <Reveal key={item.title} delay={index * 50}>
            <Link
              to={item.href}
              className="group block rounded-2xl border border-white/10 bg-white/[0.03] p-5 transition hover:border-cyan-300/40 hover:bg-white/[0.06]"
            >
              <div className="flex items-center gap-3">
                <item.icon className="h-5 w-5 text-cyan-200" />
                <h3 className="text-base font-semibold text-white">{item.title}</h3>
              </div>
              <p className="mt-3 text-sm text-white/75">{item.detail}</p>
            </Link>
          </Reveal>
        ))}
      </div>
    </section>
  )
}
