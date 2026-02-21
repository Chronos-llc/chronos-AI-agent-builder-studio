import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { Reveal } from '../Reveal'

export const EnterpriseSection: React.FC = () => {
  return (
    <section className="landing-section relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_bottom,_rgba(255,121,151,0.18),_transparent_55%)]" />
      <div className="landing-container relative">
        <Reveal>
          <h2 className="landing-heading">Enterprise delivery with governance and managed support.</h2>
        </Reveal>
        <Reveal delay={90}>
          <p className="mt-3 max-w-3xl text-white/70">
            Align security, compliance, operations, and dedicated support for production-grade agent programs.
          </p>
        </Reveal>
        <Reveal delay={160}>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to="/pricing"
              className="inline-flex items-center gap-2 rounded-full bg-[#ff607f] px-6 py-3 text-sm font-semibold text-[#0a0e1a] transition hover:bg-[#ff7893]"
            >
              Contact sales
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/app"
              className="inline-flex items-center gap-2 rounded-full border border-white/20 px-6 py-3 text-sm font-semibold text-white hover:border-white/40"
            >
              Explore Studio
            </Link>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
