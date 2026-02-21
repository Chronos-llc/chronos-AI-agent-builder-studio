import React from 'react'
import { Link } from 'react-router-dom'
import {
  aiProviders,
  sttTtsProviders,
  channels,
  integrationConnectors,
  phoneProviders,
} from '../../config/iconRegistry'
import { ProviderLogo } from '../brand/ProviderLogo'
import { Reveal } from '../Reveal'

export const IntegrationsAndModelsSection: React.FC = () => {
  const allIntegrations = [
    ...Object.values(aiProviders),
    ...Object.values(sttTtsProviders),
    ...Object.values(channels),
    ...Object.values(integrationConnectors),
    ...Object.values(phoneProviders),
  ]

  const featuredIntegrations = allIntegrations.slice(0, 12)
  const totalIntegrations = allIntegrations.length

  return (
    <section className="landing-section">
      <div className="landing-container">
        <Reveal>
          <h2 className="landing-heading">Works With Everything</h2>
        </Reveal>
        <Reveal delay={80}>
          <p className="landing-lead">
            Connect the services your agents need with our extensive integration ecosystem. From AI providers to communication channels, we&apos;ve got you covered.
          </p>
        </Reveal>

        <Reveal delay={140}>
          <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
            {featuredIntegrations.map(integration => (
              <div
                key={integration.id}
                className="landing-card flex flex-col items-center gap-3 p-5 transition-all hover:border-white/25 hover:bg-white/[0.06]"
              >
                <ProviderLogo name={integration.name} url={integration.url} size={40} />
                <span className="text-center text-sm text-white/90">{integration.name}</span>
              </div>
            ))}
          </div>
        </Reveal>

        <Reveal delay={180}>
          <div className="mt-8 flex justify-center">
            <Link
              to="/app/integrations"
              className="flex items-center gap-2 rounded-full bg-[#ff607f] px-6 py-3 text-sm font-semibold text-[#0a0e1a] transition-colors hover:bg-[#ff7893]"
            >
              <span>View all {totalIntegrations} integrations</span>
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 8l4 4m0 0l-4 4m4-4H3"
                />
              </svg>
            </Link>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
