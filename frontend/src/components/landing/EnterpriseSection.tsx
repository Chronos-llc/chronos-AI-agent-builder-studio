import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { Reveal } from '../Reveal'

export const EnterpriseSection: React.FC = () => {
  return (
    <section className="relative overflow-hidden py-16">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom,_rgba(45,212,191,0.18),_transparent_55%)]" />
      <div className="relative mx-auto w-full max-w-7xl px-6">
        <Reveal>
          <h2 className="text-3xl font-semibold text-white">Enterprise delivery with governance and managed support.</h2>
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
              className="inline-flex items-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-semibold text-[#081018] hover:bg-white/90"
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
