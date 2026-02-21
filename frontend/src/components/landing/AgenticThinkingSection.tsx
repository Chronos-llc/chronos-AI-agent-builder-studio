import React from 'react'
import { Reveal } from '../Reveal'

const stages = [
  'Orchestrator receives user objective and enters internal planning mode.',
  'Dialogue sub-agents are created with role-specific reasoning personalities.',
  'Dialogue loop runs tool-less reasoning rounds to challenge and refine strategy.',
  'Orchestrator synthesizes the plan, executes selected steps, then removes dialogue sub-agents.',
]

export const AgenticThinkingSection: React.FC = () => {
  return (
    <section className="landing-section">
      <div className="landing-container">
        <Reveal>
          <div className="landing-surface border-[#ff8ea6]/35 bg-gradient-to-br from-[#ff6f89]/14 via-transparent to-cyan-400/10 p-6">
            <p className="inline-flex rounded-full border border-[#ff9fb3]/55 bg-[#ff7a96]/10 px-2 py-1 text-[11px] uppercase tracking-[0.12em] text-[#ffafbf]">
              Beta / Experimental
            </p>
            <h2 className="mt-4 text-3xl font-semibold text-white md:text-4xl">
              Agentic Thinking: internal dialogue planning framework
            </h2>
            <p className="mt-3 max-w-4xl text-sm text-amber-50/90">
              Chronos introduces an experimental framework where orchestrator agents open internal dialogue sessions using temporary
              sub-dialogue agents before execution. This internal planning loop is separate from normal tool orchestration and is
              designed to deepen reasoning quality for complex tasks.
            </p>
          </div>
        </Reveal>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {stages.map((stage, index) => (
            <Reveal key={stage} delay={index * 80}>
              <article className="landing-card p-5">
                <p className="text-xs uppercase tracking-[0.12em] text-white/55">Stage {index + 1}</p>
                <p className="mt-2 text-sm text-white/80">{stage}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
