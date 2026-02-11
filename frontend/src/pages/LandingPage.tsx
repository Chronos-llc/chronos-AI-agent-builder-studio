import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles, ShieldCheck, Workflow, Cpu, Mic2, Globe2, Building2 } from 'lucide-react'
import { ChronosLogo } from '../components/brand/ChronosLogo'
import { Reveal } from '../components/Reveal'
import { cn } from '../lib/utils'

const providerBadges = [
  'OpenAI',
  'Fireworks',
  'xAI',
  'Google',
  'OpenRouter',
  'ElevenLabs',
  'Cartesia',
  'Deepgram',
  'Azure',
  'AWS',
]

const featureCards = [
  {
    title: 'From Idea to Agent in Minutes',
    description:
      'Start with a prompt, connect your data, and launch multi-agent workflows without wiring the plumbing.',
    icon: Sparkles,
  },
  {
    title: 'Build Your Own Chatbot with Real Tools',
    description:
      'Equip agents with actions, APIs, and automations so they can do actual work for you.',
    icon: Workflow,
  },
  {
    title: 'Create a Digital Sidekick',
    description:
      'Let assistants reason over your private knowledge, workflows, and operational playbooks.',
    icon: Cpu,
  },
  {
    title: 'Voice-first Experiences',
    description:
      'Deploy speaking agents with STT, TTS, and multilingual voice orchestration.',
    icon: Mic2,
  },
  {
    title: 'Global-ready & Multilingual',
    description:
      'Translate, transcribe, and respond across languages with the right model mix.',
    icon: Globe2,
  },
  {
    title: 'Enterprise Controls',
    description:
      'Security, auditability, and compliance controls are first-class citizens.',
    icon: ShieldCheck,
  },
]

const orchestrationSteps = [
  {
    title: 'Design',
    description: 'Outline goals, prompts, and guardrails for every agent.',
  },
  {
    title: 'Connect',
    description: 'Plug in tools, data sources, and integrations from the hub.',
  },
  {
    title: 'Compose',
    description: 'Chain sub-agents and build decision flows.',
  },
  {
    title: 'Ship',
    description: 'Deploy to chat, voice, and web channels in one click.',
  },
]

const ProviderBadge: React.FC<{ name: string }> = ({ name }) => {
  const initials = name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map(part => part[0])
    .join('')
    .toUpperCase()

  return (
    <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/90 shadow-lg shadow-black/10 backdrop-blur">
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-xs font-semibold">
        {initials}
      </div>
      <span>{name}</span>
    </div>
  )
}

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#0B1016] text-white">
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.25),_transparent_60%)]" />
        <div className="absolute -right-20 -top-20 h-72 w-72 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute -left-24 top-40 h-80 w-80 rounded-full bg-sky-500/20 blur-3xl" />

        <header className="relative z-10">
          <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
            <ChronosLogo textClassName="text-white" markClassName="text-white" />
            <nav className="hidden items-center gap-6 text-sm text-white/70 md:flex">
              <a href="#platform" className="hover:text-white">Platform</a>
              <a href="#orchestration" className="hover:text-white">Orchestration</a>
              <a href="#enterprise" className="hover:text-white">Enterprise</a>
            </nav>
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="rounded-full border border-white/20 px-4 py-2 text-sm text-white/80 transition hover:border-white/40 hover:text-white"
              >
                Sign in
              </Link>
              <Link
                to="/app"
                className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-[#0B1016] transition hover:bg-white/90"
              >
                Launch Studio
              </Link>
            </div>
          </div>
        </header>

        <section className="relative z-10 mx-auto flex w-full max-w-6xl flex-col gap-12 px-6 pb-24 pt-12 md:flex-row md:items-center">
          <div className="flex-1 space-y-6">
            <Reveal>
              <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.2em] text-white/70">
                Chronos AI Agent Builder Studio
              </div>
            </Reveal>
            <Reveal delay={100}>
              <h1 className="text-4xl font-semibold leading-tight md:text-5xl">
                From Idea to Agent in Minutes
              </h1>
            </Reveal>
            <Reveal delay={200}>
              <p className="text-lg text-white/70">
                Build your own chatbot and give it tools to do actual work for you. Create your own digital sidekick
                that works with your data, speaks in real-time, and orchestrates sub-agents with precision.
              </p>
            </Reveal>
            <Reveal delay={300}>
              <div className="flex flex-wrap gap-4">
                <Link
                  to="/app"
                  className="inline-flex items-center gap-2 rounded-full bg-cyan-400 px-6 py-3 text-sm font-semibold text-[#0B1016] transition hover:bg-cyan-300"
                >
                  Start building
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 rounded-full border border-white/20 px-6 py-3 text-sm font-semibold text-white transition hover:border-white/50"
                >
                  Book a demo
                </Link>
              </div>
            </Reveal>
          </div>
          <Reveal delay={300} direction="left" className="flex-1">
            <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-white/10 via-white/5 to-transparent p-6 shadow-2xl shadow-black/30">
              <div className="space-y-4">
                <div className="flex items-center justify-between text-xs text-white/60">
                  <span>Agent Orchestration</span>
                  <span>Live preview</span>
                </div>
                <div className="rounded-2xl bg-[#101720] p-4 text-sm text-white/80">
                  <div className="flex items-center justify-between">
                    <span>Primary LLM</span>
                    <span className="rounded-full bg-cyan-400/10 px-2 py-1 text-xs text-cyan-200">GPT-5.2</span>
                  </div>
                  <div className="mt-3 flex items-center justify-between">
                    <span>Voice Stack</span>
                    <span className="rounded-full bg-white/10 px-2 py-1 text-xs">Cartesia · Sonic 2</span>
                  </div>
                  <div className="mt-3 flex items-center justify-between">
                    <span>Translation</span>
                    <span className="rounded-full bg-white/10 px-2 py-1 text-xs">Gemini 3.1</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs text-white/60">
                  {['Secure by design', 'Tool-ready', 'Multi-modal', 'Live monitoring'].map(item => (
                    <div key={item} className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-center">
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Reveal>
        </section>
      </div>

      <section id="platform" className="mx-auto w-full max-w-6xl px-6 py-20">
        <Reveal>
          <h2 className="text-3xl font-semibold">Build, orchestrate, and scale.</h2>
        </Reveal>
        <Reveal delay={120}>
          <p className="mt-3 max-w-2xl text-white/70">
            Chronos AI Studio brings together model catalogs, tool orchestration, and agent governance into a single,
            cohesive platform for teams and builders.
          </p>
        </Reveal>
        <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {featureCards.map((feature, index) => (
            <Reveal key={feature.title} delay={index * 80}>
              <div className="group rounded-2xl border border-white/10 bg-white/5 p-6 transition hover:-translate-y-1 hover:border-cyan-300/40 hover:bg-white/10">
                <feature.icon className="h-6 w-6 text-cyan-300" />
                <h3 className="mt-4 text-lg font-semibold">{feature.title}</h3>
                <p className="mt-2 text-sm text-white/70">{feature.description}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      <section id="orchestration" className="bg-[#0F1520] py-20">
        <div className="mx-auto w-full max-w-6xl px-6">
          <Reveal>
            <div className="flex items-center gap-3 text-sm uppercase tracking-[0.2em] text-white/50">
              <Building2 className="h-4 w-4" />
              Agent Orchestration Flow
            </div>
          </Reveal>
          <Reveal delay={120}>
            <h2 className="mt-4 text-3xl font-semibold">A workflow that scales with you.</h2>
          </Reveal>
          <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {orchestrationSteps.map((step, index) => (
              <Reveal key={step.title} delay={index * 80}>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                  <div className="text-xs text-cyan-200">Step {index + 1}</div>
                  <h3 className="mt-2 text-lg font-semibold">{step.title}</h3>
                  <p className="mt-2 text-sm text-white/70">{step.description}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto w-full max-w-6xl px-6 py-20">
        <Reveal>
          <h2 className="text-3xl font-semibold">Provider-ready catalog.</h2>
        </Reveal>
        <Reveal delay={120}>
          <p className="mt-3 text-white/70">
            Install providers from the integration hub, use the studio default keys, or bring your own credentials.
          </p>
        </Reveal>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {providerBadges.map((provider, index) => (
            <Reveal key={provider} delay={index * 60}>
              <ProviderBadge name={provider} />
            </Reveal>
          ))}
        </div>
      </section>

      <section id="enterprise" className="relative overflow-hidden bg-[#0F1520] py-20">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom,_rgba(14,165,233,0.2),_transparent_60%)]" />
        <div className="relative mx-auto w-full max-w-6xl px-6">
          <Reveal>
            <h2 className="text-3xl font-semibold">Enterprise-ready from day one.</h2>
          </Reveal>
          <Reveal delay={120}>
            <p className="mt-3 max-w-2xl text-white/70">
              Governance, compliance, observability, and multi-tenant controls built into the platform to keep your
              teams aligned.
            </p>
          </Reveal>
          <Reveal delay={240}>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                to="/login"
                className={cn(
                  'inline-flex items-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-semibold text-[#0F1520] transition hover:bg-white/90'
                )}
              >
                Talk to enterprise
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/app"
                className="inline-flex items-center gap-2 rounded-full border border-white/20 px-6 py-3 text-sm font-semibold text-white transition hover:border-white/50"
              >
                Explore Studio
              </Link>
            </div>
          </Reveal>
        </div>
      </section>

      <footer className="border-t border-white/10 py-10">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 md:flex-row md:items-center md:justify-between">
          <ChronosLogo textClassName="text-white" markClassName="text-white" />
          <div className="text-sm text-white/60">
            © {new Date().getFullYear()} Chronos AI. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage

