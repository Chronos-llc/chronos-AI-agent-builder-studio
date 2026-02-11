import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { aiProviders } from '../../config/iconRegistry'
import { ProviderLogo } from '../brand/ProviderLogo'
import { Reveal } from '../Reveal'

export const ModelAccessSection: React.FC = () => {
  const providers = Object.values(aiProviders)

  return (
    <section className="mx-auto w-full max-w-7xl px-6 py-16">
      <Reveal>
        <h2 className="text-3xl font-semibold text-white">Access your favorite AI models.</h2>
      </Reveal>
      <Reveal delay={90}>
        <p className="mt-3 max-w-3xl text-white/70">
          Connect your preferred model services through the Integration Hub and select models directly inside bot settings, sub-agents, and workflow steps.
        </p>
      </Reveal>
      <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {providers.map((provider, index) => (
          <Reveal key={provider.id} delay={index * 60}>
            <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3">
              <ProviderLogo name={provider.name} url={provider.url} size={34} />
              <div>
                <div className="text-sm font-semibold text-white">{provider.name}</div>
                <div className="text-xs text-white/60">Provider integration</div>
              </div>
            </div>
          </Reveal>
        ))}
      </div>
      <Reveal delay={240}>
        <div className="mt-8">
          <Link
            to="/app/integrations"
            className="inline-flex items-center gap-2 rounded-full border border-white/20 px-5 py-2.5 text-sm font-semibold text-white hover:border-white/50"
          >
            Browse Integration Hub
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </Reveal>
    </section>
  )
}
