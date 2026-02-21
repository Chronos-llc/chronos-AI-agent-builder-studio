import React from 'react'
import { phoneProviders, sttTtsProviders } from '../../config/iconRegistry'
import { ProviderLogo } from '../brand/ProviderLogo'
import { Reveal } from '../Reveal'

export const VoiceAndTelephonySection: React.FC = () => {
  return (
    <section className="landing-section">
      <div className="landing-container">
        <Reveal>
          <h2 className="landing-heading">Voice Studio and telephony deployment</h2>
        </Reveal>
        <Reveal delay={80}>
          <p className="landing-lead">
            Configure speech providers, voice runtime settings, and phone orchestration in one layout. Route inbound/outbound calls
            and pair speech stack settings with your agent behavior.
          </p>
        </Reveal>

        <div className="mt-8 grid gap-4 lg:grid-cols-2">
          <Reveal delay={120}>
            <article className="landing-card p-5">
              <h3 className="text-lg font-semibold text-white">Phone providers</h3>
              <p className="mt-2 text-sm text-white/70">
                Search, purchase, and assign phone numbers per agent with provider-level controls.
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {Object.values(phoneProviders).map(provider => (
                  <div key={provider.id} className="flex items-center gap-3 rounded-xl border border-white/12 bg-white/[0.04] px-3 py-2">
                    <ProviderLogo name={provider.name} url={provider.url} size={30} />
                    <span className="text-sm text-white">{provider.name}</span>
                  </div>
                ))}
              </div>
            </article>
          </Reveal>

          <Reveal delay={180}>
            <article className="landing-card p-5">
              <h3 className="text-lg font-semibold text-white">STT / TTS and voice stack</h3>
              <p className="mt-2 text-sm text-white/70">
                Use catalog pickers for transcriber and voice models, then tune runtime behavior for conversation quality.
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {Object.values(sttTtsProviders).map(provider => (
                  <div key={provider.id} className="flex items-center gap-3 rounded-xl border border-white/12 bg-white/[0.04] px-3 py-2">
                    <ProviderLogo name={provider.name} url={provider.url} size={30} />
                    <span className="text-sm text-white">{provider.name}</span>
                  </div>
                ))}
              </div>
            </article>
          </Reveal>
        </div>
      </div>
    </section>
  )
}
