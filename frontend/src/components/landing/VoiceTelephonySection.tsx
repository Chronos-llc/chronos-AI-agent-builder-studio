import React from 'react'
import { Link } from 'react-router-dom'
import { phoneProviders, sttTtsProviders } from '../../config/iconRegistry'
import { ProviderLogo } from '../brand/ProviderLogo'
import { Reveal } from '../Reveal'

export const VoiceTelephonySection: React.FC = () => {
  return (
    <section id="voice" className="mx-auto w-full max-w-7xl px-6 py-16">
      <Reveal>
        <h2 className="text-3xl font-semibold text-white">Voice Studio + telephony orchestration</h2>
      </Reveal>
      <Reveal delay={80}>
        <p className="mt-3 max-w-3xl text-white/70">
          Configure STT/TTS/voice models, choose phone providers, and run call-ready assistants with one control plane.
        </p>
      </Reveal>

      <div className="mt-8 grid gap-4 lg:grid-cols-2">
        <Reveal delay={120}>
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h3 className="text-lg font-semibold text-white">Phone providers</h3>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {Object.values(phoneProviders).map(provider => (
                <div key={provider.id} className="flex items-center gap-3 rounded-xl border border-white/10 bg-black/20 px-3 py-2">
                  <ProviderLogo name={provider.name} url={provider.url} size={30} />
                  <div className="text-sm text-white">{provider.name}</div>
                </div>
              ))}
            </div>
            <p className="mt-4 text-xs text-white/55">Search, purchase, and assign phone numbers per agent.</p>
          </div>
        </Reveal>

        <Reveal delay={180}>
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h3 className="text-lg font-semibold text-white">Speech stack</h3>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {Object.values(sttTtsProviders).map(provider => (
                <div key={provider.id} className="flex items-center gap-3 rounded-xl border border-white/10 bg-black/20 px-3 py-2">
                  <ProviderLogo name={provider.name} url={provider.url} size={30} />
                  <div className="text-sm text-white">{provider.name}</div>
                </div>
              ))}
            </div>
            <p className="mt-4 text-xs text-white/55">Use catalog pattern pickers for STT/TTS and voice selection.</p>
          </div>
        </Reveal>
      </div>

      <Reveal delay={220}>
        <div className="mt-8">
          <Link
            to="/app/agents/new"
            className="inline-flex items-center gap-2 rounded-full bg-cyan-300 px-5 py-2.5 text-sm font-semibold text-[#081018] hover:bg-cyan-200"
          >
            Configure voice agents
          </Link>
        </div>
      </Reveal>
    </section>
  )
}
