import React from 'react'
import { Link } from 'react-router-dom'
import { Reveal } from '../Reveal'

const items = [
  {
    title: 'Publish MCP or API apps',
    body: 'Package your internal systems as integration apps with tools and endpoint metadata your agents can invoke.',
  },
  {
    title: 'Moderated trust pipeline',
    body: 'Submit your integration for review with icon, screenshots, policy links, and testing notes before global distribution.',
  },
  {
    title: 'Global propagation',
    body: 'Once approved, your integration appears in the hub, agent selectors, and workflow nodes so teams can reuse it everywhere.',
  },
]

export const PublishIntegrationSection: React.FC = () => {
  return (
    <section className="landing-section">
      <div className="landing-container">
        <Reveal>
          <div className="landing-surface border-[#ff8ea6]/35 bg-gradient-to-br from-[#ff6f89]/14 via-transparent to-cyan-400/12 p-8">
            <p className="text-xs uppercase tracking-[0.22em] text-[#ff9fb3]">Integration Marketplace</p>
            <h2 className="mt-3 text-3xl font-semibold text-white md:text-4xl">
              Turn your external system into an agent action surface
            </h2>
            <p className="mt-4 max-w-3xl text-white/75">
              Research teams and business operators can publish new MCP or API integrations, pass moderation, and make those
              capabilities available to agents across workspaces.
            </p>

            <div className="mt-8 grid gap-4 md:grid-cols-3">
              {items.map((item) => (
                <article key={item.title} className="landing-card border-white/12 bg-black/25 p-4">
                  <h3 className="text-sm font-semibold text-white">{item.title}</h3>
                  <p className="mt-2 text-sm text-white/70">{item.body}</p>
                </article>
              ))}
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                to="/app/integrations/create"
                className="rounded-full bg-[#ff607f] px-5 py-2.5 text-sm font-semibold text-[#0a0e1a] transition hover:bg-[#ff7893]"
              >
                Create New Integration
              </Link>
              <Link
                to="/app/integrations"
                className="rounded-full border border-white/20 px-5 py-2.5 text-sm font-semibold text-white transition hover:border-white/45"
              >
                View Integration Hub
              </Link>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
