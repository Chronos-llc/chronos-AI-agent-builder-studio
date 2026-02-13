import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { ChronosLogo } from '../brand/ChronosLogo'
import { Reveal } from '../Reveal'
import { LanguageSwitcher } from './LanguageSwitcher'
import { useMarketingI18n } from '../../hooks/useMarketingI18n'

export const HeroSection: React.FC = () => {
  const { t } = useMarketingI18n()

  return (
    <section className="relative overflow-hidden border-b border-white/10">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(45,212,191,0.18),_transparent_55%)]" />
      <div className="absolute -right-24 top-0 h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
      <div className="absolute -left-24 top-36 h-80 w-80 rounded-full bg-emerald-400/10 blur-3xl" />

      <header className="relative z-10 mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6">
        <ChronosLogo textClassName="text-white" markClassName="text-white" />
        <nav className="hidden items-center gap-6 text-sm text-white/70 md:flex">
          <a href="#unified-stack" className="hover:text-white">{t('nav.unifiedStack', 'Unified Stack')}</a>
          <a href="#suite" className="hover:text-white">{t('nav.agentSuite', 'Agent Suite')}</a>
          <a href="#channels" className="hover:text-white">{t('nav.channels', 'Channels')}</a>
          <Link to="/pricing" className="hover:text-white">{t('nav.pricing', 'Pricing')}</Link>
          <Link to="/docs" className="hover:text-white">{t('nav.docs', 'Docs')}</Link>
        </nav>
        <div className="flex items-center gap-2">
          <LanguageSwitcher />
          <Link
            to="/login"
            className="rounded-full border border-white/20 px-4 py-2 text-sm text-white/80 transition hover:border-white/40 hover:text-white"
          >
            {t('nav.signin', 'Sign in')}
          </Link>
          <Link
            to="/app"
            className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-[#081018] transition hover:bg-white/90"
          >
            {t('nav.launchStudio', 'Launch Studio')}
          </Link>
        </div>
      </header>

      <div className="relative z-10 mx-auto grid w-full max-w-7xl gap-10 px-6 pb-20 pt-10 lg:grid-cols-[1.2fr_1fr] lg:items-center">
        <div className="space-y-6">
          <Reveal>
            <div className="inline-flex rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.2em] text-white/70">
              {t('hero.badge', 'Chronos AI Agent Builder Studio')}
            </div>
          </Reveal>
          <Reveal delay={90}>
            <h1 className="text-4xl font-semibold leading-tight md:text-6xl">
              {t('hero.title', 'Build agent systems that run real work every day.')}
            </h1>
          </Reveal>
          <Reveal delay={150}>
            <p className="max-w-2xl text-lg text-white/75">
              {t(
                'hero.subtitle',
                'From Idea to Agent in Minutes. Build your own chatbot and give it tools to do actual work for you. Create a digital sidekick that works with your data, tools, voice, and workflows.'
              )}
            </p>
          </Reveal>
          <Reveal delay={220}>
            <div className="flex flex-wrap gap-3">
              <Link
                to="/app"
                className="inline-flex items-center gap-2 rounded-full bg-cyan-300 px-6 py-3 text-sm font-semibold text-[#081018] transition hover:bg-cyan-200"
              >
                {t('hero.start', 'Start building')}
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/pricing"
                className="inline-flex items-center gap-2 rounded-full border border-cyan-200/40 bg-cyan-200/10 px-6 py-3 text-sm font-semibold text-cyan-100 transition hover:border-cyan-200 hover:bg-cyan-200/20"
              >
                {t('hero.compare', 'Compare plans')}
              </Link>
              <Link
                to="/docs"
                className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-6 py-3 text-sm font-semibold text-white transition hover:border-white/40 hover:bg-white/10"
              >
                {t('hero.readDocs', 'Read docs')}
              </Link>
            </div>
          </Reveal>
        </div>

        <Reveal delay={180} direction="left">
          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur">
            <div className="mb-4 flex items-center justify-between text-xs text-white/60">
              <span>Live orchestration stack</span>
              <span>Studio preview</span>
            </div>
            <div className="space-y-3 text-sm">
              {[
                ['Primary model', 'GPT-5.2'],
                ['Voice runtime', 'Cartesia + Deepgram'],
                ['Tooling layer', 'MCP Hub + Integrations'],
                ['Automation', 'Workflow generator + sandbox'],
              ].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between rounded-xl border border-white/10 bg-black/20 px-3 py-2">
                  <span className="text-white/70">{label}</span>
                  <span className="rounded-full bg-cyan-300/15 px-2 py-1 text-xs text-cyan-100">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
