import React from 'react'
import { Reveal } from '../Reveal'

const steps = [
  {
    title: 'Design',
    description: 'Define objectives, prompts, and behavior with Fuzzy guidance.',
  },
  {
    title: 'Connect',
    description: 'Install integrations, model providers, channels, and MCP tools.',
  },
  {
    title: 'Automate',
    description: 'Compose workflows and sub-agent orchestration with execution traces.',
  },
  {
    title: 'Operate',
    description: 'Deploy to suite/chat/voice channels and monitor in real time.',
  },
]

export const HowItWorksSection: React.FC = () => {
  return (
    <section className="mx-auto w-full max-w-7xl px-6 py-16">
      <Reveal>
        <h2 className="text-3xl font-semibold text-white">How it works</h2>
      </Reveal>
      <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {steps.map((step, index) => (
          <Reveal key={step.title} delay={index * 90}>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
              <div className="inline-flex rounded-full border border-cyan-200/40 bg-cyan-300/10 px-2 py-1 text-xs text-cyan-100">
                Step {index + 1}
              </div>
              <h3 className="mt-3 text-lg font-semibold text-white">{step.title}</h3>
              <p className="mt-2 text-sm text-white/70">{step.description}</p>
            </div>
          </Reveal>
        ))}
      </div>

      <Reveal delay={220}>
        <div className="mt-8 grid gap-3 sm:grid-cols-3">
          {[
            { label: 'Integrated providers', value: '40+' },
            { label: 'Automation capabilities', value: '100+' },
            { label: 'Studio control surfaces', value: '15+' },
          ].map(item => (
            <div key={item.label} className="rounded-xl border border-white/10 bg-black/20 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.15em] text-white/55">{item.label}</p>
              <p className="mt-1 text-2xl font-semibold text-cyan-100">{item.value}</p>
            </div>
          ))}
        </div>
      </Reveal>
    </section>
  )
}
