import React from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2, MessageSquare, PlayCircle, TerminalSquare } from 'lucide-react'
import { Reveal } from '../Reveal'

const suiteFlows = [
  {
    icon: MessageSquare,
    title: 'Chat with created or marketplace agents',
    detail: 'Open any agent in Suite and interact through a unified chat surface with full context visibility.',
  },
  {
    icon: TerminalSquare,
    title: 'Watch real-time action logs',
    detail: 'Track executions including tool calls and virtual-computer activity directly while the task runs.',
  },
  {
    icon: PlayCircle,
    title: 'Continue tasks across channels',
    detail: 'Pull the latest conversation history into web chat to continue tasks started on external channels.',
  },
  {
    icon: CheckCircle2,
    title: 'Manage context and summaries',
    detail: 'Use context meters and summary condensation to keep long-running conversations operational.',
  },
]

export const AgentSuiteDeepDiveSection: React.FC = () => {
  return (
    <section id="suite" className="mx-auto w-full max-w-7xl px-6 py-16">
      <Reveal>
        <h2 className="text-3xl font-semibold text-white md:text-4xl">Agent Suite: where operations happen</h2>
      </Reveal>
      <Reveal delay={80}>
        <p className="mt-4 max-w-3xl text-white/70">
          Build in Studio, operate in Suite. Chronos Suite centralizes conversations, action traces, and task continuity for ongoing agent work.
        </p>
      </Reveal>
      <div className="mt-8 grid gap-4 md:grid-cols-2">
        {suiteFlows.map((flow, index) => (
          <Reveal key={flow.title} delay={index * 70}>
            <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
              <div className="flex items-center gap-3">
                <flow.icon className="h-5 w-5 text-cyan-200" />
                <h3 className="text-lg font-semibold text-white">{flow.title}</h3>
              </div>
              <p className="mt-3 text-sm text-white/75">{flow.detail}</p>
            </article>
          </Reveal>
        ))}
      </div>
      <Reveal delay={180}>
        <div className="mt-6">
          <Link to="/app/agents" className="rounded-full border border-white/20 px-5 py-2.5 text-sm font-semibold text-white hover:border-white/40">
            Open Agent Suite
          </Link>
        </div>
      </Reveal>
    </section>
  )
}
