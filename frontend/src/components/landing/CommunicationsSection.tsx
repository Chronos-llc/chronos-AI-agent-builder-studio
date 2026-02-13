import React from 'react'
import { channels } from '../../config/iconRegistry'
import { ProviderLogo } from '../brand/ProviderLogo'
import { Reveal } from '../Reveal'

const channelNarratives = [
  {
    id: 'telegram',
    title: 'Telegram operations',
    detail: 'Deploy chat and automation workflows to Telegram with traceable conversation history.',
  },
  {
    id: 'slack',
    title: 'Slack collaboration',
    detail: 'Run team-facing agents and internal productivity flows in Slack channels and workspaces.',
  },
  {
    id: 'whatsapp',
    title: 'WhatsApp support',
    detail: 'Serve conversational support and task-driven interactions through WhatsApp channels.',
  },
  {
    id: 'discord',
    title: 'Discord communities',
    detail: 'Engage communities and automate moderation/help tasks in Discord environments.',
  },
  {
    id: 'webchat',
    title: 'Embedded web chat',
    detail: 'Launch website chat surfaces and continue tasks inside Agent Suite with unified context.',
  },
]

export const CommunicationsSection: React.FC = () => {
  return (
    <section id="channels" className="bg-[#0B111A] py-16">
      <div className="mx-auto w-full max-w-7xl px-6">
        <Reveal>
          <h2 className="text-3xl font-semibold text-white md:text-4xl">Communication channels with unified continuity</h2>
        </Reveal>
        <Reveal delay={80}>
          <p className="mt-4 max-w-3xl text-white/70">
            Chronos keeps conversations and task context connected across channels so users can resume work from the suite without
            losing operational state.
          </p>
        </Reveal>
        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {channelNarratives.map((item, index) => {
            const channel = channels[item.id]
            return (
              <Reveal key={item.id} delay={index * 70}>
                <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
                  <div className="flex items-center gap-3">
                    <ProviderLogo name={channel?.name || item.title} url={channel?.url} size={32} />
                    <h3 className="text-lg font-semibold text-white">{item.title}</h3>
                  </div>
                  <p className="mt-3 text-sm text-white/75">{item.detail}</p>
                </article>
              </Reveal>
            )
          })}
        </div>
      </div>
    </section>
  )
}
