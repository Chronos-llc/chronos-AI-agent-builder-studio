import React from 'react'
import { Link } from 'react-router-dom'
import { aiProviders, integrationConnectors, sttTtsProviders } from '../../config/iconRegistry'
import { ProviderLogo } from '../brand/ProviderLogo'
import { Reveal } from '../Reveal'

const highlights = [
  {
    title: 'Model flexibility',
    detail: 'Select provider and model per agent role, from chat to translation to media and speech.',
  },
  {
    title: 'MCP and connector hub',
    detail: 'Install servers and connectors once, then expose actions to orchestration and workflows.',
  },
  {
    title: 'Workflow + virtual execution',
    detail: 'Trigger code execution and action chains with observable logs and execution controls.',
  },
  {
    title: 'Marketplace operations',
    detail: 'Publish and install reusable agents while preserving configurable runtime settings.',
  },
]

export const IntegrationsAndModelsSection: React.FC = () => {
  const providerStrip = [...Object.values(aiProviders), ...Object.values(sttTtsProviders)]

  return (
    <section className="mx-auto w-full max-w-7xl px-6 py-16">
      <Reveal>
        <h2 className="text-3xl font-semibold text-white md:text-4xl">Integrations and model routing in one stack</h2>
      </Reveal>
      <Reveal delay={80}>
        <p className="mt-4 max-w-3xl text-white/70">
          Connect the services your agents need, map tool permissions, and keep provider choices visible across bot settings,
          sub-agents, and workflow paths.
        </p>
      </Reveal>

      <Reveal delay={140}>
        <div className="mt-6 flex gap-3 overflow-x-auto rounded-2xl border border-white/10 bg-white/[0.03] p-4">
          {providerStrip.map(provider => (
            <div key={`${provider.id}-${provider.name}`} className="flex min-w-[170px] items-center gap-3 rounded-xl border border-white/10 bg-black/20 px-3 py-2">
              <ProviderLogo name={provider.name} url={provider.url} size={30} />
              <span className="text-sm text-white">{provider.name}</span>
            </div>
          ))}
        </div>
      </Reveal>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {highlights.map((highlight, index) => (
          <Reveal key={highlight.title} delay={index * 70}>
            <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
              <h3 className="text-lg font-semibold text-white">{highlight.title}</h3>
              <p className="mt-3 text-sm text-white/75">{highlight.detail}</p>
            </article>
          </Reveal>
        ))}
      </div>

      <Reveal delay={180}>
        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Object.values(integrationConnectors).slice(0, 6).map(connector => (
            <div key={connector.id} className="flex items-center gap-3 rounded-xl border border-white/10 bg-black/20 px-3 py-2">
              <ProviderLogo name={connector.name} url={connector.url} size={28} />
              <span className="text-sm text-white/90">{connector.name}</span>
            </div>
          ))}
        </div>
      </Reveal>

      <Reveal delay={220}>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link to="/app/integrations" className="rounded-full bg-cyan-300 px-5 py-2.5 text-sm font-semibold text-[#081018] hover:bg-cyan-200">
            Explore integrations
          </Link>
          <Link to="/app/agents/new" className="rounded-full border border-white/20 px-5 py-2.5 text-sm font-semibold text-white hover:border-white/40">
            Configure models
          </Link>
        </div>
      </Reveal>
    </section>
  )
}
