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
    <section className="bg-[#0C121C] py-16">
      <div className="mx-auto w-full max-w-7xl px-6">
        <Reveal>
          <div className="rounded-3xl border border-amber-300/40 bg-amber-300/10 p-6">
            <p className="inline-flex rounded-full border border-amber-200/60 px-2 py-1 text-[11px] uppercase tracking-[0.12em] text-amber-100">
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
              <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
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
