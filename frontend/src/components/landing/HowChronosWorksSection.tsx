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
    <section className="landing-section">
      <div className="landing-container">
        <Reveal>
          <h2 className="landing-heading">How Chronos Studio works</h2>
        </Reveal>
        <Reveal delay={90}>
          <p className="landing-lead">
            Chronos combines planning, execution, and operations so teams can move from idea to production agent systems without
            switching platforms.
          </p>
        </Reveal>
        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {phases.map((phase, index) => (
            <Reveal key={phase.title} delay={index * 80}>
              <article className="landing-card p-5">
                <p className="inline-flex rounded-full border border-[#ff8ea6]/35 bg-[#ff7a96]/12 px-2 py-1 text-xs text-[#ff9fb3]">Step {index + 1}</p>
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
