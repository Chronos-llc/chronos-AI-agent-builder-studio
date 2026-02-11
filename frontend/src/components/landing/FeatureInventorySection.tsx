import React from 'react'
import { Link } from 'react-router-dom'
import { Bot, Cable, ClipboardList, Compass, LayoutDashboard, Mic2, Puzzle, ShieldCheck, Sparkles, Workflow, Wrench } from 'lucide-react'
import { Reveal } from '../Reveal'

const features = [
  { name: 'Agent Builder', href: '/app/agents', icon: Bot },
  { name: 'Fuzzy assistant', href: '/app/agents/new', icon: Sparkles },
  { name: 'Workflow Generator', href: '/app/agents/new', icon: Workflow },
  { name: 'Virtual Computer', href: '/app/agents/new', icon: Compass },
  { name: 'MCP Hub', href: '/app/integrations', icon: Cable },
  { name: 'Marketplace', href: '/app/agents', icon: Puzzle },
  { name: 'Voice Studio', href: '/app/agents/new', icon: Mic2 },
  { name: 'Communication Channels', href: '/app/channels', icon: Wrench },
  { name: 'Testing Suites', href: '/app/agents/new', icon: ClipboardList },
  { name: 'Call Logs', href: '/app/dashboard', icon: LayoutDashboard },
  { name: 'Reports/Boards', href: '/app/dashboard', icon: LayoutDashboard },
  { name: 'Admin', href: '/app/admin', icon: ShieldCheck },
  { name: 'Compliance', href: '/app/settings', icon: ShieldCheck },
  { name: 'Analytics', href: '/app/dashboard', icon: LayoutDashboard },
  { name: 'Agent Suite', href: '/app/agents', icon: Bot },
]

export const FeatureInventorySection: React.FC = () => {
  return (
    <section id="features" className="bg-[#0D141D] py-16">
      <div className="mx-auto w-full max-w-7xl px-6">
        <Reveal>
          <h2 className="text-3xl font-semibold text-white">Everything needed to run an agent operation.</h2>
        </Reveal>
        <Reveal delay={90}>
          <p className="mt-3 max-w-3xl text-white/70">
            Chronos combines orchestration, model routing, voice operations, workflow automation, governance, and team collaboration in one studio.
          </p>
        </Reveal>
        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <Reveal key={feature.name} delay={index * 40}>
              <Link
                to={feature.href}
                className="group flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-white/85 transition hover:-translate-y-0.5 hover:border-cyan-300/40 hover:bg-white/[0.06]"
              >
                <span className="inline-flex items-center gap-2">
                  <feature.icon className="h-4 w-4 text-cyan-200" />
                  {feature.name}
                </span>
                <span className="text-xs text-white/50 group-hover:text-cyan-100">Open</span>
              </Link>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
