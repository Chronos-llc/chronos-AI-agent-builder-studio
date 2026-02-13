import React from 'react'
import { Link } from 'react-router-dom'
import { Bot, Mic2, Workflow, Cable } from 'lucide-react'
import { Reveal } from '../Reveal'

const blocks = [
  {
    icon: Bot,
    title: 'Build chat and work agents',
    description:
      'Create work-focused agents with tool execution, task logic, memory, and suite interactions in one pipeline.',
  },
  {
    icon: Mic2,
    title: 'Build voice agents',
    description:
      'Configure speech stack, phone routing, and real-time call behavior from Voice Studio without leaving Chronos.',
  },
  {
    icon: Workflow,
    title: 'Run operational workflows',
    description:
      'Use workflow generation and orchestration to standardize repeated tasks, fallback paths, and automation outcomes.',
  },
  {
    icon: Cable,
    title: 'Connect tools and providers',
    description:
      'Install models, MCP servers, and connectors in the Integration Hub and bind them to agents and workflows.',
  },
]

export const UnifiedStackSection: React.FC = () => {
  return (
    <section id="unified-stack" className="mx-auto w-full max-w-7xl px-6 py-16">
      <Reveal>
        <h2 className="text-3xl font-semibold text-white md:text-4xl">
          Chronos is a unified stack for voice and work-based chat agents.
        </h2>
      </Reveal>
      <Reveal delay={80}>
        <p className="mt-4 max-w-4xl text-white/70">
          Instead of separate tools for build, orchestration, deployment, and operations, Chronos gives one control plane for model
          routing, communication channels, workflows, and agent execution history.
        </p>
      </Reveal>
      <div className="mt-8 grid gap-4 md:grid-cols-2">
        {blocks.map((block, index) => (
          <Reveal key={block.title} delay={index * 70}>
            <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
              <div className="flex items-center gap-3">
                <block.icon className="h-5 w-5 text-cyan-200" />
                <h3 className="text-lg font-semibold text-white">{block.title}</h3>
              </div>
              <p className="mt-3 text-sm text-white/75">{block.description}</p>
            </article>
          </Reveal>
        ))}
      </div>
      <Reveal delay={180}>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link to="/app/agents/new" className="rounded-full bg-cyan-300 px-5 py-2.5 text-sm font-semibold text-[#081018] hover:bg-cyan-200">
            Build an agent
          </Link>
          <Link to="/app/agents" className="rounded-full border border-white/20 px-5 py-2.5 text-sm font-semibold text-white hover:border-white/40">
            Open existing agents
          </Link>
        </div>
      </Reveal>
    </section>
  )
}
