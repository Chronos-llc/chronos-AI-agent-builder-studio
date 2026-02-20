import React from 'react'
import { Brain, Mic2, Users, Building2, Zap, Globe } from 'lucide-react'
import { Reveal } from '../Reveal'

export const AboutUsSection: React.FC = () => {
  return (
    <section id="about-us" className="landing-section relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(104,186,255,0.09),_transparent_62%)]" />
      <div className="pointer-events-none absolute -right-24 top-14 h-80 w-80 rounded-full bg-cyan-400/10 blur-3xl" />
      <div className="pointer-events-none absolute -left-24 bottom-10 h-80 w-80 rounded-full bg-pink-500/10 blur-3xl" />

      <div className="landing-container relative">
        {/* Header */}
        <Reveal>
          <div className="mb-4 inline-flex rounded-full border border-[#ff8ea6]/30 bg-[#ff7a96]/10 px-4 py-2 text-xs uppercase tracking-[0.2em] text-[#ff9fb3]">
            About Us
          </div>
        </Reveal>
        <Reveal delay={50}>
          <h2 className="landing-heading md:text-5xl">
            About Chronos Studio
          </h2>
        </Reveal>
        <Reveal delay={100}>
          <p className="mt-4 text-xl font-light text-white/75">
            The Execution Layer for Next-Generation AI Agents
          </p>
        </Reveal>

        {/* Introduction */}
        <Reveal delay={150}>
          <div className="mt-10 max-w-4xl">
            <p className="text-lg leading-relaxed text-white/76">
              At Chronos Studio, we architect the infrastructure where intelligent systems transition from concept to deployment. We are a full-stack AI agent platform, a unified foundation purpose-built for constructing both general-purpose AI agents and voice-enabled autonomous systems within a single, cohesive stack.
            </p>
          </div>
        </Reveal>

        {/* Our Philosophy */}
        <Reveal delay={200}>
          <div className="mt-16">
            <h3 className="text-2xl font-semibold text-white">Our Philosophy</h3>
            <div className="landing-card mt-4 max-w-4xl p-6">
              <p className="text-white/75 leading-relaxed">
                The AI landscape has fragmented. Developers navigate disjointed tools for text-based agents, separate platforms for voice synthesis, and disconnected pipelines for deployment. Chronos Studio resolves this systemic inefficiency. We consolidate the entire agent creation lifecycle from initial design through tool integration, voice model selection, and production deployment into one orchestrated environment.
              </p>
            </div>
          </div>
        </Reveal>

        {/* What We Build */}
        <Reveal delay={250}>
          <div className="mt-16">
            <h3 className="text-2xl font-semibold text-white">What We Build</h3>
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              {/* General AI Agents */}
              <div className="landing-card p-6">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#ff84a0]/15">
                    <Brain className="h-5 w-5 text-[#ff9bb0]" />
                  </div>
                  <h4 className="text-lg font-semibold text-white">General AI Agents</h4>
                </div>
                <p className="mt-4 text-sm text-white/75 leading-relaxed">
                  Construct intelligent agents equipped with custom tools, memory systems, and autonomous decision-making capabilities. Connect your agents to external APIs, databases, and your preferred social media ecosystems, transforming them from static scripts into adaptive digital sidekicks that extend your cognitive reach.
                </p>
              </div>

              {/* Voice AI Agents */}
              <div className="landing-card p-6">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-300/20">
                    <Mic2 className="h-5 w-5 text-cyan-100" />
                  </div>
                  <h4 className="text-lg font-semibold text-white">Voice AI Agents</h4>
                </div>
                <p className="mt-4 text-sm text-white/75 leading-relaxed">
                  Deploy real-time voice agents engineered for human-grade conversation. Through our integrated access to premier AI voice model providers, you build agents with:
                </p>
                <ul className="mt-3 space-y-2 text-sm text-white/70">
                  <li className="flex items-start gap-2">
                    <Zap className="mt-0.5 h-4 w-4 shrink-0 text-[#ff96ae]" />
                    <span>Sub-second latency for natural conversation flow</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Globe className="mt-0.5 h-4 w-4 shrink-0 text-[#ff96ae]" />
                    <span>Emotional awareness that detects and responds to user sentiment</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Mic2 className="mt-0.5 h-4 w-4 shrink-0 text-[#ff96ae]" />
                    <span>Human-like vocal fidelity that transcends robotic interaction</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </Reveal>

        {/* Who We Serve */}
        <Reveal delay={300}>
          <div className="mt-16">
            <h3 className="text-2xl font-semibold text-white">Who We Serve</h3>
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              {/* Individuals & Creators */}
              <div className="landing-card p-6">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-300/20">
                    <Users className="h-5 w-5 text-cyan-100" />
                  </div>
                  <h4 className="text-lg font-semibold text-white">Individuals & Creators</h4>
                </div>
                <ul className="mt-4 space-y-2 text-sm text-white/75">
                  <li className="flex items-start gap-2">
                    <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#ff96ae]" />
                    <span>Build personal AI sidekicks that automate workflows and amplify productivity</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#ff96ae]" />
                    <span>Connect agents to the messaging App you use daily</span>
                  </li>
                </ul>
              </div>

              {/* Developers & Enterprises */}
              <div className="landing-card p-6">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-300/20">
                    <Building2 className="h-5 w-5 text-cyan-100" />
                  </div>
                  <h4 className="text-lg font-semibold text-white">Developers & Enterprises</h4>
                </div>
                <ul className="mt-4 space-y-2 text-sm text-white/75">
                  <li className="flex items-start gap-2">
                    <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#ff96ae]" />
                    <span>Construct scalable voice agents for customer support, sales, and engagement</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#ff96ae]" />
                    <span>Connect agents to the messaging App your customers are on</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#ff96ae]" />
                    <span>Access enterprise-grade telephony with 99.9% SLA guarantees</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#ff96ae]" />
                    <span>No-code to pro-code flexibility for any skill level</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#ff96ae]" />
                    <span>Full API access for custom integrations and white-label solutions</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </Reveal>

        {/* Why Chronos */}
        <Reveal delay={350}>
          <div className="mt-16">
            <h3 className="text-2xl font-semibold text-white">Why Chronos?</h3>
            <div className="landing-surface mt-4 max-w-4xl p-6">
              <p className="text-white/75 leading-relaxed">
                The market is moving toward agentic systems. By 2026, the majority of businesses will have integrated AI-driven voice technology into their operations. Chronos Studio positions you ahead of this inflection point.
              </p>
              <p className="mt-4 text-white/75 leading-relaxed">
                We do not offer fragmented tools. We provide the ground, a systematic foundation where both general and voice agents are conceived, trained, and launched. Whether you are an individual seeking a cognitive extension or an enterprise scaling customer interactions, Chronos Studio is the execution layer for your intelligent systems.
              </p>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
