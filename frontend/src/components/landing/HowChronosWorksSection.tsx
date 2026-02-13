import React from 'react'
import { Reveal } from '../Reveal'

const phases = [
  {
    title: 'Design',
    detail:
      'Define goals, system prompts, model preferences, and agent behavior patterns with Fuzzy assistance.',
  },
  {
    title: 'Connect',
    detail:
      'Attach model providers, communication channels, tool connectors, and MCP servers from the Integration Hub.',
  },
  {
    title: 'Deploy',
    detail:
      'Publish to voice and chat surfaces, then route traffic through your selected communication channels.',
  },
  {
    title: 'Operate',
    detail:
      'Track actions, monitor context usage, continue tasks from any channel, and iterate in Agent Suite.',
  },
]

export const HowChronosWorksSection: React.FC = () => {
  return (
    <section className="bg-[#0B111A] py-16">
      <div className="mx-auto w-full max-w-7xl px-6">
        <Reveal>
          <h2 className="text-3xl font-semibold text-white md:text-4xl">How Chronos Studio works</h2>
        </Reveal>
        <Reveal delay={90}>
          <p className="mt-4 max-w-3xl text-white/70">
            Chronos combines planning, execution, and operations so teams can move from idea to production agent systems without
            switching platforms.
          </p>
        </Reveal>
        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {phases.map((phase, index) => (
            <Reveal key={phase.title} delay={index * 80}>
              <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
                <p className="inline-flex rounded-full border border-white/20 px-2 py-1 text-xs text-white/60">Step {index + 1}</p>
                <h3 className="mt-3 text-lg font-semibold text-white">{phase.title}</h3>
                <p className="mt-2 text-sm text-white/75">{phase.detail}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
